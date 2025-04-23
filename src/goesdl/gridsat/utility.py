from netCDF4 import Dataset

from ..geodesy import RectangularRegion
from ..gridsat.netcdf_geodetic import GSLatLonGrid
from ..gridsat.netcdf_image import GSImage
from .time import GSCoverageTime
from .dataset_info import GSDatasetInfo


def read_gridsat_dataset(
    dataframe: Dataset,
    channel: str,
    region: RectangularRegion,
    corners: bool = False,
) -> tuple[GSImage, GSCoverageTime, GSDatasetInfo]:
    grid = GSLatLonGrid(dataframe, region, corners=corners)

    data = GSImage(dataframe, grid, channel)

    coverage = GSCoverageTime(dataframe)

    metadata = GSDatasetInfo(dataframe, channel)

    return data, coverage, metadata
