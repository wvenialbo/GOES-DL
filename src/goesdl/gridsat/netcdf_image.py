from typing import Any, cast

from netCDF4 import Dataset  # pylint: disable=no-name-in-module
from numpy import nan

from ..geodesy import RectangularRegion
from ..netcdf import DatasetView, HasStrHelp, variable
from ..utils.array import ArrayBool, ArrayFloat32, MaskedFloat32
from .metadata import MeasurementMetadata
from .netcdf_geodetic import GSLatLonGrid, LimitType


class GSImageData(HasStrHelp):

    raster: MaskedFloat32


class GSImage(HasStrHelp):

    grid: GSLatLonGrid
    raster: MaskedFloat32

    metadata: MeasurementMetadata

    def __init__(
        self, record: Dataset, channel: str, grid: GSLatLonGrid
    ) -> None:
        data = self._extract_image(
            record, channel, grid.lon_limits, grid.lat_limits
        )

        self.grid = grid
        self.raster = data.raster

        self.metadata = self._extract_metadata(record, channel)

    @staticmethod
    def _extract_image(
        record: Dataset,
        channel: str,
        lon_limits: LimitType,
        lat_limits: LimitType,
    ) -> "GSImageData":
        def slice(x: Any) -> Any:
            min_lon, max_lon = lon_limits
            min_lat, max_lat = lat_limits
            return x[0, min_lat:max_lat, min_lon:max_lon]

        class _GSImageData(DatasetView):
            raster: MaskedFloat32 = variable(channel).array(filter=slice)

        data = _GSImageData(record)

        data.raster.data[data.raster.mask] = nan

        return cast(GSImageData, data)

    @staticmethod
    def _extract_metadata(record: Dataset, name: str) -> MeasurementMetadata:
        measurement = variable(name)

        class _ImageMetata(DatasetView):
            long_name: str = measurement.attribute()
            standard_name: str = measurement.attribute()
            units: str = measurement.attribute()
            content_type: str = measurement.attribute("coverage_content_type")
            coordinates: str = measurement.attribute()
            range: ArrayFloat32 = measurement.attribute("actual_range")
            shape: tuple[int] = measurement.attribute()

        metadata = _ImageMetata(record)

        return MeasurementMetadata(metadata)

    @property
    def image(self) -> ArrayFloat32:
        return cast(ArrayFloat32, self.raster.data)

    @property
    def mask(self) -> ArrayBool:
        return cast(ArrayBool, self.raster.mask)

    @property
    def region(self) -> RectangularRegion:
        return self.grid.region
