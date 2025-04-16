from typing import Any, cast

from netCDF4 import Dataset  # pylint: disable=no-name-in-module
from numpy import float64, nan, newaxis

from ..geodesy import RectangularRegion
from ..netcdf import DatasetView, HasStrHelp, scalar, variable
from ..utils.array import ArrayBool, ArrayFloat64, MaskedFloat32
from .netcdf_geodetic import GSLatLonGrid, LimitType

SECONDS_IN_DAY = 86400
SECONDS_IN_MINUTE = 60


class GSTimeData(HasStrHelp):

    delta_time: MaskedFloat32
    optimal_time: float64
    optimal_time_bounds: ArrayFloat64


class GSTimeGrid(HasStrHelp):

    grid: GSLatLonGrid

    # Delta-time data in minutes.
    delta_time: MaskedFloat32

    # Optimal-time (in days since 1970-01-01 UTC).
    optimal_time: float64

    # Optimal-time-bounds (in days since 1970-01-01 UTC).
    optimal_time_bounds: ArrayFloat64

    def __init__(self, record: Dataset, grid: GSLatLonGrid) -> None:
        data = self._extract_image(record, grid.lon_limits, grid.lat_limits)

        self.grid = grid

        self.delta_time = data.delta_time
        self.optimal_time = data.optimal_time
        self.optimal_time_bounds = data.optimal_time_bounds

    @staticmethod
    def _extract_image(
        record: Dataset,
        lon_limits: LimitType | None,
        lat_limits: LimitType | None,
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

    @property
    def time(self) -> ArrayFloat64:
        # (in seconds since 1970-01-01 UTC)
        return (
            self.optimal_time * SECONDS_IN_DAY
            + self.delta_time.data * SECONDS_IN_MINUTE
        )

    @property
    def time_bounds(self) -> ArrayFloat64:
        # (in seconds since 1970-01-01 UTC)
        return (
            self.optimal_time_bounds[:, newaxis].T * SECONDS_IN_DAY
            + self.delta_time.data * SECONDS_IN_MINUTE
        )

    @property
    def mask(self) -> ArrayBool:
        return self.delta_time.mask

    @property
    def region(self) -> RectangularRegion:
        return self.grid.region
