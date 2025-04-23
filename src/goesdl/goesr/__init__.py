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

from .dataset_info import GOESDatasetInfo
from .dataset_time import GOESCoverageTime
from .geodetic import GOESLatLonGrid
from .image import GOESImage
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

GOESDerivedProductLocator = GOESProductLocatorABIDP
GOESDerivedWithCannelProductLocator = GOESProductLocatorABIDC
GOESLightningMapperProductLocator = GOESProductLocatorGLM
GOESPrimaryMultibandProductLocator = GOESProductLocatorABIPM
GOESPrimaryProductLocator = GOESProductLocatorABIPP

__all__ = [
    "GOESCoverageTime",
    "GOESDatasetInfo",
    "GOESDerivedProductLocator",
    "GOESDerivedWithCannelProductLocator",
    "GOESImage",
    "GOESLatLonGrid",
    "GOESLightningMapperProductLocator",
    "GOESPrimaryMultibandProductLocator",
    "GOESPrimaryProductLocator",
    "GOESProductLocatorABI",
    "GOESProductLocatorABIDC",
    "GOESProductLocatorABIDP",
    "GOESProductLocatorABIPM",
    "GOESProductLocatorABIPP",
    "GOESProductLocatorCMIP",
    "GOESProductLocatorDMW",
    "GOESProductLocatorDMWV",
    "GOESProductLocatorGLM",
    "GOESProductLocatorLCFA",
    "GOESProductLocatorMCMIP",
    "GOESProductLocatorRad",
]
