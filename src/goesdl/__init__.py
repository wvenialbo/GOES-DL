"""
Provide functionality for accessing GOES-R Series and GridSat datasets.

This package provides classes to download and extract information from
GOES-R Series and GridSat netCDF data files. It uses the `requests`
and `boto3` packages to download the files and the `netCDF4` package to
read the data files.
"""

from .info import __package_id__, __package_name__, __version__

__all__ = [
    "__package_id__",
    "__package_name__",
    "__version__",
]
