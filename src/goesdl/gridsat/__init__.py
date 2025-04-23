"""
Export locators for GridSat imagery products.

Classes:
    - GridSatProductLocatorB1: Locator for B1 products.
    - GridSatProductLocatorGC: Locator for GC products.
"""

from .dataset_info import GSDatasetInfo
from .locator_b1 import GridSatProductLocatorB1
from .locator_gc import GridSatProductLocatorGC
from .netcdf_geodetic import GSLatLonGrid
from .netcdf_image import GSImage
from .netcdf_info import (
    GSGeospatialInfo,
    GSPlatformInfo,
    GSRadiometricInfo,
)
from .projection import GSGlobe, GSOrbitGeometry
from .netcdf_time import GSCoverageTime, GSTimeGrid
from .utility import read_gridsat_dataset

__all__ = [
    "GridSatProductLocatorB1",
    "GridSatProductLocatorGC",
    "GSImage",
    "GSLatLonGrid",
    "GSTimeGrid",
    "GSCoverageTime",
    "GSDatasetInfo",
    "GSPlatformInfo",
    "GSGeospatialInfo",
    "GSRadiometricInfo",
    "read_gridsat_dataset",
    "GSOrbitGeometry",
    "GSGlobe",
]
