"""
Provide functionality for reading fragments of GOES-R datasets.

This package provides classes to extract and represent information from
GOES satellite netCDF data files. It uses the `netCDF4` package to read
the data files and the netcdf subpackage to extract the information.
"""

from . import grid
from . import netcdf

__all__ = [
    "grid",
    "netcdf",
]

__package_id__ = "GOES-CORE"
__package_name__ = f"{__package_id__} — GOES Satellite Imagery Dataset Reader"
__version__ = "v0.0-rc0"
