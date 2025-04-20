"""
Export locators for GOES-R Series imagery dataset products.

Classes:
    - GOESProductLocatorABI: All primary and derived Advanced Baseline
      Imager (ABI) products.
    - GOESProductLocatorABIDC: All derived ABI products supporting
      channels.
    - GOESProductLocatorDMW: ABI Derived Motion Winds (DMW).
    - GOESProductLocatorDMWV: ABI Derived Motion WV Winds (DMWV).
    - GOESProductLocatorABIDP: All derived ABI products.
    - GOESProductLocatorGLM: All Geostationary Lightning Mapper (GLM)
      products.
    - GOESProductLocatorLCFA: GLM Lightning Cluster-Filter Algorithm
      (LCFA).
    - GOESProductLocatorABIPM: Multi-band primary ABI products.
    - GOESProductLocatorMCMIP: Multi-band CMIP Product.
    - GOESProductLocatorABIPP: All primary ABI products.
    - GOESProductLocatorCMIP: ABI Cloud and Moisture Imagery Product
      (CMIP).
    - GOESProductLocatorRad: ABI Radiance Product (Rad).
"""

from .locator_abi import GOESProductLocatorABI
from .locator_dc import (
    GOESProductLocatorABIDC,
    GOESProductLocatorDMW,
    GOESProductLocatorDMWV,
)
from .locator_dp import GOESProductLocatorABIDP
from .locator_glm import GOESProductLocatorGLM
from .locator_lp import GOESProductLocatorLCFA
from .locator_pm import GOESProductLocatorABIPM, GOESProductLocatorMCMIP
from .locator_pp import (
    GOESProductLocatorABIPP,
    GOESProductLocatorCMIP,
    GOESProductLocatorRad,
)
from .netcdf_dataset import GOESDatasetInfo
from .netcdf_geodetic import GOESLatLonGrid
from .netcdf_image import GOESImage
from .netcdf_time import GOESCoverageTime

GOESDerivedProductLocator = GOESProductLocatorABIDP
GOESDerivedWithCannelProductLocator = GOESProductLocatorABIDC
GOESLightningMapperProductLocator = GOESProductLocatorGLM
GOESPrimaryMultibandProductLocator = GOESProductLocatorABIPM
GOESPrimaryProductLocator = GOESProductLocatorABIPP

__all__ = [
    "GOESProductLocatorABI",
    "GOESProductLocatorABIDC",
    "GOESProductLocatorDMW",
    "GOESProductLocatorDMWV",
    "GOESProductLocatorABIDP",
    "GOESProductLocatorGLM",
    "GOESProductLocatorLCFA",
    "GOESProductLocatorABIPM",
    "GOESProductLocatorMCMIP",
    "GOESProductLocatorABIPP",
    "GOESProductLocatorCMIP",
    "GOESProductLocatorRad",
    "GOESDerivedProductLocator",
    "GOESDerivedWithCannelProductLocator",
    "GOESLightningMapperProductLocator",
    "GOESPrimaryMultibandProductLocator",
    "GOESPrimaryProductLocator",
    "GOESLatLonGrid",
    "GOESImage",
    "GOESDatasetInfo",
    "GOESCoverageTime",
]
