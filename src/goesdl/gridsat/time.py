from datetime import datetime
from typing import Any, cast

from netCDF4 import Dataset  # pylint: disable=no-name-in-module
from numpy import float64, nan, newaxis

from ..geodesy import RectangularRegion
from ..netcdf import DatasetView, HasStrHelp, attribute, scalar, variable
from ..protocols.geodetic import IndexRange
from ..utils.array import ArrayBool, ArrayFloat64, ArrayInt8, MaskedFloat32
from .geodetic import GSLatLonGrid
from .metadata import DeltaTimeMetadata, TimeMetadata, VariableMetadata

SECONDS_IN_DAY = 86400
SECONDS_IN_MINUTE = 60

MetadataType = TimeMetadata | DeltaTimeMetadata | VariableMetadata


class _DatasetInfo(DatasetView):

    cdm_data_type: str


class GSTimeData(HasStrHelp):

    # Delta-time data in minutes.
    delta_time: MaskedFloat32

    # Optimal-time (in days since 1970-01-01 UTC).
    optimal_time: float64

    # Optimal-time-bounds (in days since 1970-01-01 UTC).
    optimal_time_bounds: ArrayFloat64


class GSTimeGrid(GSTimeData):

    grid: GSLatLonGrid

    metadata: dict[str, MetadataType]

    def __init__(self, dataframe: Dataset, grid: GSLatLonGrid) -> None:
        info = _DatasetInfo(dataframe)

        self._validate_content_type(dataframe, info.cdm_data_type)

        data = self._extract_timedata(
            dataframe, grid.lon_limits, grid.lat_limits
        )

        self.grid = grid

        self.delta_time = data.delta_time
        self.optimal_time = data.optimal_time
        self.optimal_time_bounds = data.optimal_time_bounds

        self.metadata = self._get_metadata(dataframe)

    @staticmethod
    def _extract_bounds_metadata(dataframe: Dataset) -> VariableMetadata:
        coordinate = variable("time_bounds")

        class _TimeMetata(DatasetView):
            long_name: str = coordinate.attribute()
            comment: str = coordinate.attribute()
            units: str = coordinate.attribute()
            shape: tuple[int] = coordinate.attribute()

        metadata = _TimeMetata(dataframe)

        return VariableMetadata(metadata)

    @staticmethod
    def _extract_delta_metadata(dataframe: Dataset) -> DeltaTimeMetadata:
        measurement = variable("delta_time")

        class _ImageMetata(DatasetView):
            long_name: str = measurement.attribute()
            coordinates: str = measurement.attribute()
            units: str = measurement.attribute()
            range: ArrayInt8 = measurement.attribute("actual_range")
            content_type: str = measurement.attribute("coverage_content_type")
            shape: tuple[int] = measurement.attribute()

        metadata = _ImageMetata(dataframe)

        return DeltaTimeMetadata(metadata)

    @staticmethod
    def _extract_time_metadata(dataframe: Dataset) -> TimeMetadata:
        coordinate = variable("time")

        class _LatLonMetata(DatasetView):
            long_name: str = coordinate.attribute()
            comment: str = coordinate.attribute()
            standard_name: str = coordinate.attribute()
            units: str = coordinate.attribute()
            axis: str = coordinate.attribute()
            calendar: str = coordinate.attribute()
            content_type: str = coordinate.attribute("coverage_content_type")
            shape: tuple[int] = coordinate.attribute()

        metadata = _LatLonMetata(dataframe)

        return TimeMetadata(metadata)

    @staticmethod
    def _extract_timedata(
        dataframe: Dataset,
        lon_limits: IndexRange,
        lat_limits: IndexRange,
    ) -> "GSTimeData":
        def slice(x: Any) -> Any:
            min_lon, max_lon = lon_limits
            min_lat, max_lat = lat_limits
            return x[0, min_lat:max_lat, min_lon:max_lon]

        class _GSTimeData(DatasetView):
            delta_time: MaskedFloat32 = variable("delta_time").array(
                filter=slice
            )
            optimal_time: float64 = scalar("time")
            optimal_time_bounds: ArrayFloat64 = variable("time_bounds").data()

        data = _GSTimeData(dataframe)

        data.delta_time.data[data.delta_time.mask] = nan

        return cast(GSTimeData, data)

    @classmethod
    def _get_metadata(cls, dataframe: Dataset) -> dict[str, MetadataType]:
        return {
            "delta_time": cls._extract_delta_metadata(dataframe),
            "time": cls._extract_time_metadata(dataframe),
            "time_bounds": cls._extract_bounds_metadata(dataframe),
        }

    @staticmethod
    def _validate_content_type(dataframe: Dataset, content_type: str) -> None:
        if content_type != "Grid":
            raise ValueError(
                "Unexpected content type. "
                f"Expected 'Grid', got '{content_type}'"
            )

    @property
    def time(self) -> ArrayFloat64:
        # (in seconds since 1970-01-01 UTC)
        actual_time: ArrayFloat64 = (
            self.optimal_time * SECONDS_IN_DAY
            + self.delta_time.data * SECONDS_IN_MINUTE
        )
        return actual_time

    @property
    def time_bounds(self) -> ArrayFloat64:
        # (in seconds since 1970-01-01 UTC)
        actual_time_bounds: ArrayFloat64 = (
            self.optimal_time_bounds[:, newaxis].T * SECONDS_IN_DAY
            + self.delta_time.data * SECONDS_IN_MINUTE
        )
        return actual_time_bounds

    @property
    def mask(self) -> ArrayBool:
        return cast(ArrayBool, self.delta_time.mask)

    @property
    def region(self) -> RectangularRegion:
        return self.grid.region


class GSCoverageTime(DatasetView):

    datetime_start: datetime = attribute(
        "time_coverage_start", convert=datetime.fromisoformat
    )
    datetime_end: datetime = attribute(
        "time_coverage_end", convert=datetime.fromisoformat
    )

    @property
    def timestamp_start(self) -> float:
        return self.datetime_start.timestamp()

    @property
    def timestamp_end(self) -> float:
        return self.datetime_end.timestamp()
