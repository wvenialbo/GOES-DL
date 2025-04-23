from re import search
from typing import Any, cast

from netCDF4 import Dataset  # pylint: disable=no-name-in-module
from numpy import nan

from ..geodesy import RectangularRegion
from ..netcdf import DatasetView, HasStrHelp, variable
from ..protocols.geodetic import IndexRange
from ..utils.array import ArrayBool, ArrayFloat32, MaskedFloat32
from .databook_gc import (
    channel_correspondence_gc,
    channel_description_gc,
    platform_origin_gridsat_gc,
)
from .geodetic import GSLatLonGrid
from .metadata import MeasurementMetadata


class _DatasetInfo(DatasetView):

    platform: str
    cdm_data_type: str


class GSImageData(HasStrHelp):

    raster: MaskedFloat32


class GSImage(GSImageData):

    _grid: GSLatLonGrid

    channel_id: str

    metadata: MeasurementMetadata

    def __init__(
        self, dataframe: Dataset, grid: GSLatLonGrid, channel: str
    ) -> None:
        self._validate_channel(channel)

        info = _DatasetInfo(dataframe)

        self._validate_availability(channel, info.platform)

        self._validate_content_type(dataframe, info.cdm_data_type)
        self._validate_dimensions(dataframe, channel)

        data = self._extract_image(
            dataframe, channel, grid.lon_limits, grid.lat_limits
        )

        self.channel_id = channel

        self._grid = grid
        self.raster = data.raster

        self.metadata = self._extract_metadata(dataframe, channel)

    @staticmethod
    def _extract_image(
        dataframe: Dataset,
        channel: str,
        lon_limits: IndexRange,
        lat_limits: IndexRange,
    ) -> "GSImageData":
        def slice(x: Any) -> Any:
            min_lon, max_lon = lon_limits
            min_lat, max_lat = lat_limits
            return x[0, min_lat:max_lat, min_lon:max_lon]

        class _GSImageData(DatasetView):
            raster: MaskedFloat32 = variable(channel).array(filter=slice)

        data = _GSImageData(dataframe)

        data.raster.data[data.raster.mask] = nan

        return cast(GSImageData, data)

    @staticmethod
    def _extract_metadata(
        dataframe: Dataset, name: str
    ) -> MeasurementMetadata:
        measurement = variable(name)

        class _GSImageMetadata(DatasetView):
            long_name: str = measurement.attribute()
            standard_name: str = measurement.attribute()
            units: str = measurement.attribute()
            content_type: str = measurement.attribute("coverage_content_type")
            coordinates: str = measurement.attribute()
            range: ArrayFloat32 = measurement.attribute("actual_range")
            shape: tuple[int] = measurement.attribute()

        metadata = _GSImageMetadata(dataframe)

        return MeasurementMetadata(metadata)

    @staticmethod
    def _get_platform_name(platform: str) -> str:
        pattern = r"(GOES-\d+)"
        if match := search(pattern, platform):
            return match[1]
        raise ValueError(f"Unexpected platform: '{platform}'")

    @classmethod
    def _validate_availability(cls, channel: str, platform: str) -> None:
        plaform_name = cls._get_platform_name(platform)
        platform_id = platform_origin_gridsat_gc[plaform_name]
        channel_nr = channel_correspondence_gc[platform_id][channel]

        if not channel_nr:
            raise ValueError(
                f"Band '{channel}' is not supported by '{plaform_name}'"
            )

    @staticmethod
    def _validate_channel(channel: str) -> None:
        if not channel:
            raise ValueError(
                "Channel information is required for multi-band datasets"
            )
        if channel not in channel_description_gc:
            allowed_channels = "', '".join(channel_description_gc.keys())
            raise ValueError(
                f"Invalid channel: '{channel}'; "
                f"allowed channels are: '{allowed_channels}'"
            )

    @staticmethod
    def _validate_content_type(dataframe: Dataset, content_type: str) -> None:
        if content_type != "Grid":
            raise ValueError(
                "Unexpected content type. "
                f"Expected 'Grid', got '{content_type}'"
            )

    @staticmethod
    def _validate_dimensions(dataframe: Dataset, field_id: str) -> None:
        if ("time", "lat", "lon") != dataframe.variables[field_id].dimensions:
            raise ValueError(
                f"Field '{field_id}' does not have the required dimensions"
            )

    @property
    def image(self) -> ArrayFloat32:
        return cast(ArrayFloat32, self.raster.data)

    @property
    def mask(self) -> ArrayBool:
        return cast(ArrayBool, self.raster.mask)

    @property
    def region(self) -> RectangularRegion:
        return self._grid.region

    @property
    def grid(self) -> GSLatLonGrid:
        return self._grid
