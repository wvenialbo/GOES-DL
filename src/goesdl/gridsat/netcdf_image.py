from typing import Any, cast

from netCDF4 import Dataset  # pylint: disable=no-name-in-module
from numpy import nan

from ..geodesy import RectangularRegion
from ..netcdf import DatasetView, HasStrHelp, variable
from ..utils.array import ArrayFloat32, MaskedFloat32
from .netcdf_geodetic import GSLatLonGrid, LimitType


class GSImageData(HasStrHelp):

    raster: MaskedFloat32


class GSImage(HasStrHelp):

    grid: GSLatLonGrid
    raster: MaskedFloat32

    def __init__(self, record: Dataset, name: str, grid: GSLatLonGrid) -> None:
        data = self._extract_image(
            record, name, grid.lon_limits, grid.lat_limits
        )

        self.grid = grid
        self.raster = data.raster

    @staticmethod
    def _extract_image(
        record: Dataset,
        name: str,
        lon_limits: LimitType | None,
        lat_limits: LimitType | None,
    ) -> "GSImageData":
        def slice(x: Any) -> Any:
            min_lon, max_lon = lon_limits
            min_lat, max_lat = lat_limits
            return x[0, min_lat:max_lat, min_lon:max_lon]

        class _GSImageData(DatasetView):
            raster: MaskedFloat32 = variable(name).array(filter=slice)

        data = _GSImageData(record)

        data.raster.data[data.raster.mask] = nan

        return cast(GSImageData, data)

    @property
    def image(self) -> ArrayFloat32:
        return self.raster.data

    @property
    def mask(self) -> ArrayFloat32:
        return self.raster.mask

    @property
    def region(self) -> RectangularRegion:
        return self.grid.region
