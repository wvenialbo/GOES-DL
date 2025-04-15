from typing import Any, cast

from netCDF4 import Dataset  # pylint: disable=no-name-in-module

from ..geodesy import RectangularExtent
from ..netcdf import DatasetView, HasStrHelp, variable
from ..utils.array import ArrayFloat32


class GSLatLonGridData(HasStrHelp):
    lon: ArrayFloat32
    lat: ArrayFloat32

    def __init__(
        self,
        record: Dataset,
        extent: RectangularExtent | None = None,
        delta: int = 5,
    ) -> None:
        step = delta if extent else None
        data = self._extract(record, step)

        self.lon = data.lon
        self.lat = data.lat

    @staticmethod
    def _extract(record: Dataset, step: int | None) -> "GSLatLonGridData":
        def _subsample(x: Any) -> Any:
            return x[:] if step is None else x[:: step[0], :: step[1]]

        class _LatLonData(DatasetView):
            lon: ArrayFloat32 = variable("lon").data(filter=_subsample)
            lat: ArrayFloat32 = variable("lat").data(filter=_subsample)

        data = _LatLonData(record)

        return cast(GSLatLonGridData, data)
