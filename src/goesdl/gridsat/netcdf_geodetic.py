from collections.abc import Callable
from typing import Any, cast

from netCDF4 import Dataset  # pylint: disable=no-name-in-module
from numpy import concatenate, flatnonzero, meshgrid

from ..geodesy import RectangularExtent
from ..netcdf import DatasetView, HasStrHelp, variable
from ..utils.array import ArrayFloat32

LimitType = tuple[int, int]


class GSLatLonGrid(HasStrHelp):
    lon: ArrayFloat32
    lat: ArrayFloat32

    lon_limits: LimitType
    lat_limits: LimitType

    def __init__(
        self,
        record: Dataset,
        extent: RectangularExtent | None = None,
        delta: int = 5,
        corners: bool = False,
    ) -> None:
        if extent:
            data, lon_limits, lat_limits = self._slice(
                record, extent, delta, corners
            )
        else:
            data, lon_limits, lat_limits = self._full(record, corners)

        self.lon, self.lat = meshgrid(data.lon, data.lat)

        self.lon_limits = lon_limits
        self.lat_limits = lat_limits

    @staticmethod
    def _extract(
        record: Dataset,
        step: int | None,
        lon_limits: LimitType | None,
        lat_limits: LimitType | None,
    ) -> "GSLatLonGrid":
        def subsample(limits) -> Callable[[Any], Any]:
            def closure(x: Any) -> Any:
                begin, end = limits or (None, None)
                skip = step or None
                return x[begin:end:skip]

            return closure

        class _LatLonData(DatasetView):
            lon: ArrayFloat32 = variable("lon").data(
                filter=subsample(lon_limits)
            )
            lat: ArrayFloat32 = variable("lat").data(
                filter=subsample(lat_limits)
            )

        data = _LatLonData(record)

        return cast(GSLatLonGrid, data)

    @staticmethod
    def _extract_bounds(
        record: Dataset,
        lon_limits: LimitType | None,
        lat_limits: LimitType | None,
    ) -> "GSLatLonGrid":
        def subsample(limits) -> Callable[[Any], Any]:
            def closure(x: Any) -> Any:
                begin, end = limits or (None, None)
                coord = x[begin:end]
                return concatenate((coord[:, 0], coord[-1:, -1]))

            return closure

        class _LatLonData(DatasetView):
            lon: ArrayFloat32 = variable("lon_bounds").data(
                filter=subsample(lon_limits)
            )
            lat: ArrayFloat32 = variable("lat_bounds").data(
                filter=subsample(lat_limits)
            )

        data = _LatLonData(record)

        return cast(GSLatLonGrid, data)

    @staticmethod
    def _find_limits(
        coord: ArrayFloat32,
        min_max: tuple[float, float],
        delta: int,
        offset: int = 0,
    ) -> LimitType:
        min_value, max_value = min_max

        min_indices = flatnonzero(coord < min_value)
        min_bound = min_indices[-1] if min_indices.size > 0 else -1

        # Encontrar el índice del primer elemento mayor que 'mayor_que'
        max_indices = flatnonzero(coord > max_value)
        max_bound = max_indices[+1] if max_indices.size > 0 else -1

        return int(min_bound * delta + offset), int(max_bound * delta + offset)

    @classmethod
    def _full(
        cls,
        record: Dataset,
        corners: bool,
    ) -> tuple["GSLatLonGrid", LimitType, LimitType]:
        if corners:
            data = cls._extract_bounds(record, None, None)
            lon_limits = 0, data.lon.size - 1
            lat_limits = 0, data.lat.size - 1
        else:
            data = cls._extract(record, None, None, None)
            lon_limits = 0, data.lon.size
            lat_limits = 0, data.lat.size

        return data, lon_limits, lat_limits

    @classmethod
    def _slice(
        cls,
        record: Dataset,
        extent: RectangularExtent,
        delta: int,
        corners: bool,
    ) -> tuple["GSLatLonGrid", LimitType, LimitType]:
        data = cls._extract(record, delta, None, None)

        lon_limits = cls._find_limits(data.lon, extent.lon_bounds, delta)
        lat_limits = cls._find_limits(data.lat, extent.lat_bounds, delta)

        data = cls._extract(record, None, lon_limits, lat_limits)

        lon_limits = cls._find_limits(
            data.lon, extent.lon_bounds, 1, lon_limits[0]
        )
        lat_limits = cls._find_limits(
            data.lat, extent.lat_bounds, 1, lat_limits[0]
        )

        if corners:
            data = cls._extract_bounds(record, lon_limits, lat_limits)
        else:
            data = cls._extract(record, None, lon_limits, lat_limits)

        return data, lon_limits, lat_limits
