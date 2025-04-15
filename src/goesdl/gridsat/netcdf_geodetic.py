from typing import Any, cast

from netCDF4 import Dataset  # pylint: disable=no-name-in-module
from numpy import flatnonzero

from ..geodesy import RectangularExtent
from ..netcdf import DatasetView, HasStrHelp, variable
from ..utils.array import ArrayFloat32

LimitType = tuple[int, int, int, int]


class GSLatLonGridData(HasStrHelp):
    lon: ArrayFloat32
    lat: ArrayFloat32

    limits: LimitType

    def __init__(
        self,
        record: Dataset,
        extent: RectangularExtent | None = None,
        delta: int = 5,
    ) -> None:
        step = delta if extent else None
        data = self._extract(record, step, None)

        if extent:
            lon_limits = self._find_limits(data.lon, extent.lon_bounds, delta)
            lat_limits = self._find_limits(data.lat, extent.lat_bounds, delta)
            data = self._extract(record, None, lon_limits + lat_limits)
            lon_limits = self._find_limits(
                data.lon, extent.lon_bounds, 1, lon_limits[0]
            )
            lat_limits = self._find_limits(
                data.lat, extent.lat_bounds, 1, lat_limits[0]
            )
        else:
            lon_limits = 0, data.lon.size - 1
            lat_limits = 0, data.lat.size - 1

        self.lon = data.lon
        self.lat = data.lat
        self.limits = lon_limits + lat_limits

    @staticmethod
    def _extract(
        record: Dataset, step: int | None, limits: LimitType | None
    ) -> "GSLatLonGridData":
        def _sublon(x: Any) -> Any:
            begin, end = limits[:2] if limits else (None, None)
            return x[begin:end:step] if step else x[begin:end]

        def _sublat(x: Any) -> Any:
            begin, end = limits[2:] if limits else (None, None)
            return x[begin:end:step] if step else x[begin:end]

        class _LatLonData(DatasetView):
            lon: ArrayFloat32 = variable("lon").data(filter=_sublon)
            lat: ArrayFloat32 = variable("lat").data(filter=_sublat)

        data = _LatLonData(record)

        return cast(GSLatLonGridData, data)

    @staticmethod
    def _find_limits(
        coord: ArrayFloat32,
        min_max: tuple[float, float],
        delta: int,
        offset: int = 0,
    ) -> tuple[int, int]:
        min_value, max_value = min_max

        min_indices = flatnonzero(coord < min_value)
        min_bound = min_indices[-1] if min_indices.size > 0 else -1

        # Encontrar el índice del primer elemento mayor que 'mayor_que'
        max_indices = flatnonzero(coord > max_value)
        max_bound = max_indices[+1] if max_indices.size > 0 else -1

        return int(min_bound * delta + offset), int(max_bound * delta + offset)
