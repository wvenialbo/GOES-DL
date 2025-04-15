"""
Provide functionality for accessing GOES-R Series and GridSat datasets.

This package provides classes to download and extract information from
GOES-R Series and GridSat netCDF data files. It uses the `requests`
and `boto3` packages to download the files and the `netCDF4` package to
read the data files.
"""

from . import dataset, datasource, downloader, grid, netcdf
from .dataset import ProductLocator
from .datasource import (
    Datasource,
    DatasourceAWS,
    DatasourceCache,
    DatasourceLocal,
    DatasourceNCEI,
)
from .downloader import Downloader
from .info import __package_id__, __package_name__, __version__

__all__ = [
    "__package_id__",
    "__package_name__",
    "__version__",
    "dataset",
    "datasource",
    "Datasource",
    "DatasourceAWS",
    "DatasourceCache",
    "DatasourceLocal",
    "DatasourceNCEI",
    "downloader",
    "Downloader",
    "grid",
    "netcdf",
    "ProductLocator",
]
