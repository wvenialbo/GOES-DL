from typing import Any, cast

from netCDF4 import Dataset  # pylint: disable=no-name-in-module
from numpy import nan

from ..netcdf import DatasetView, HasStrHelp, variable
from ..utils.array import MaskedFloat32
from .netcdf_geodetic import GSLatLonGrid, LimitType


class GSImageData(HasStrHelp):

    image: MaskedFloat32


class GSImage(HasStrHelp):

    grid: GSLatLonGrid
    image: MaskedFloat32

    def __init__(self, record: Dataset, name: str, grid: GSLatLonGrid) -> None:
        data = self._extract_image(
            record, name, grid.lon_limits, grid.lat_limits
        )

        self.grid = grid
        self.image = data.image

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
            image: MaskedFloat32 = variable(name).array(filter=slice)

        data = _GSImageData(record)

        data.image.data[data.image.mask] = nan

        return cast(GSImageData, data)
