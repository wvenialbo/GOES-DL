"""
Provide functionality for reading fragments of GOES-R datasets.

This package provides classes to extract and represent information from
GOES satellite netCDF data files. It uses the `netCDF4` package to read
the data files and the netcdf subpackage to extract the information.
"""

from . import netcdf
from .dataset import GOESDatasetInfo
from .geodetic import (
    GOESGeodeticGrid,
    GOESLatLonGrid,
    GOESLatLonGridData,
    GOESLatLonGridInfo,
    GOESLatLonGridMetadata,
)
from .image import GOESImage, GOESImageMetadata
from .projection import (
    GOESABIFixedGrid,
    GOESABIFixedGridArray,
    GOESGlobe,
    GOESOrbitGeometry,
    GOESProjection,
)

__all__ = [
    "GOESABIFixedGrid",
    "GOESABIFixedGridArray",
    "GOESDatasetInfo",
    "GOESGeodeticGrid",
    "GOESGlobe",
    "GOESImage",
    "GOESImageMetadata",
    "GOESLatLonGrid",
    "GOESLatLonGridData",
    "GOESLatLonGridInfo",
    "GOESLatLonGridMetadata",
    "GOESOrbitGeometry",
    "GOESProjection",
    "netcdf",
]

__package_id__ = "GOES-DR"
__package_name__ = f"{__package_id__} — GOES Satellite Imagery Dataset Reader"
__version__ = "v0.1-rc1"
