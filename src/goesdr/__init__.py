"""
Provide functionality for accessing GOES-R Series and GridSat datasets.

This package provides classes to download and extract information from
GOES-R Series and GridSat netCDF data files. It uses the `requests`
and `boto3` packages to download the files and the `netCDF4` package to
read the data files.
"""

__package_id__ = "GOES-CORE"
__package_name__ = (
    f"{__package_id__} — GOES Satellite Dataset Access Core Functionality"
)
__version__ = "v0.0-rc0"
