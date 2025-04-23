from netCDF4 import Dataset

from ..geodesy import RectangularRegion
from .dataset_info import GSDatasetInfo
from .geodetic import GSLatLonGrid
from .image import GSImage


def read_gridsat_dataset(
    dataframe: Dataset,
    channel: str,
    region: RectangularRegion,
    corners: bool = False,
) -> tuple[GSImage, GSDatasetInfo]:
    grid = GSLatLonGrid(dataframe, region, corners=corners)

    data = GSImage(dataframe, grid, channel)

    metadata = GSDatasetInfo(dataframe, channel)

    return data, metadata
