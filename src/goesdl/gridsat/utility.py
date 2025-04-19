from netCDF4 import Dataset

from ..geodesy import RectangularRegion
from ..gridsat.netcdf_geodetic import GSLatLonGrid
from ..gridsat.netcdf_image import GSImage
from ..gridsat.netcdf_metadata import GSDatasetMetadata
from ..gridsat.netcdf_time import GSCoverageTime


def read_gridsat_dataset(
    dataframe: Dataset,
    channel: str,
    region: RectangularRegion,
    corners: bool = False,
) -> tuple[GSImage, GSCoverageTime, GSDatasetMetadata]:
    grid = GSLatLonGrid(dataframe, region, corners=corners)

    data = GSImage(dataframe, channel, grid)

    coverage = GSCoverageTime(dataframe)

    metadata = GSDatasetMetadata(dataframe, channel)

    return data, coverage, metadata
