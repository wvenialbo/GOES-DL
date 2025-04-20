from datetime import datetime
from typing import Any, cast

from netCDF4 import Dataset  # pylint: disable=no-name-in-module
from numpy import datetime64, float64, nan, newaxis

from ..geodesy import RectangularRegion
from ..netcdf import DatasetView, HasStrHelp, scalar, variable
from ..protocols.geodetic import IndexRange
from ..utils.array import ArrayBool, ArrayFloat64, ArrayInt8, MaskedFloat32
from .metadata import DeltaTimeMetadata, TimeMetadata, VariableMetadata
from .netcdf_geodetic import GSLatLonGrid

SECONDS_IN_DAY = 86400
SECONDS_IN_MINUTE = 60

NOT_A_DATETIME = cast(datetime, datetime64("NaT"))

MetadataType = TimeMetadata | DeltaTimeMetadata | VariableMetadata


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

    def __init__(self, record: Dataset, grid: GSLatLonGrid) -> None:
        data = self._extract_timedata(record, grid.lon_limits, grid.lat_limits)

        self.grid = grid

        self.delta_time = data.delta_time
        self.optimal_time = data.optimal_time
        self.optimal_time_bounds = data.optimal_time_bounds

        self.metadata = self._get_metadata(record)

    @staticmethod
    def _extract_bounds_metadata(record: Dataset) -> VariableMetadata:
        coordinate = variable("time_bounds")

        class _TimeMetata(DatasetView):
            long_name: str = coordinate.attribute()
            comment: str = coordinate.attribute()
            units: str = coordinate.attribute()
            shape: tuple[int] = coordinate.attribute()

        metadata = _TimeMetata(record)

        return VariableMetadata(metadata)

    @staticmethod
    def _extract_delta_metadata(record: Dataset) -> DeltaTimeMetadata:
        measurement = variable("delta_time")

        class _ImageMetata(DatasetView):
            long_name: str = measurement.attribute()
            coordinates: str = measurement.attribute()
            units: str = measurement.attribute()
            range: ArrayInt8 = measurement.attribute("actual_range")
            content_type: str = measurement.attribute("coverage_content_type")
            shape: tuple[int] = measurement.attribute()

        metadata = _ImageMetata(record)

        return DeltaTimeMetadata(metadata)

    @staticmethod
    def _extract_time_metadata(record: Dataset) -> TimeMetadata:
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

        metadata = _LatLonMetata(record)

        return TimeMetadata(metadata)

    @staticmethod
    def _extract_timedata(
        record: Dataset,
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

        data = _GSTimeData(record)

        data.delta_time.data[data.delta_time.mask] = nan

        return cast(GSTimeData, data)

    @classmethod
    def _get_metadata(cls, record: Dataset) -> dict[str, MetadataType]:
        return {
            "delta_time": cls._extract_delta_metadata(record),
            "time": cls._extract_time_metadata(record),
            "time_bounds": cls._extract_bounds_metadata(record),
        }

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


class GSCoverageTime(HasStrHelp):

    datetime_start: datetime = NOT_A_DATETIME
    datetime_end: datetime = NOT_A_DATETIME

    def __init__(self, record: Dataset) -> None:
        datetime_start = getattr(record, "time_coverage_start", "")
        datetime_end = getattr(record, "time_coverage_end", "")

        if datetime_start and datetime_end:
            self.datetime_start = datetime.fromisoformat(datetime_start)
            self.datetime_end = datetime.fromisoformat(datetime_end)

    @property
    def timestamp_start(self) -> float:
        return self.datetime_start.timestamp()

    @property
    def timestamp_end(self) -> float:
        return self.datetime_end.timestamp()
