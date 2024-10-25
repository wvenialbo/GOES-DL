"""
Export locators for GOES-R Series imagery products.

Classes:
    - GOESProductLocatorABI: Locator for ABI products.
    - GOESProductLocatorABIDC: Locator for ABI products with derived
      channel.
    - GOESProductLocatorDMW: Locator for Derived Motion Winds (DMW)
      products.
    - GOESProductLocatorDMWV: Locator for Derived Motion Winds (DMW)
      products with visible channel.
    - GOESProductLocatorABIDP: Locator for ABI products with derived
      product.
    - GOESProductLocatorGLM: Locator for GLM products.
    - GOESProductLocatorLCFA: Locator for LCFA products.
    - GOESProductLocatorABIPM: Locator for ABI products with primary
      multiband.
    - GOESProductLocatorMCMIP: Locator for MCMIP products.
    - GOESProductLocatorABIPP: Locator for ABI products with primary
      product.
    - GOESProductLocatorCMIP: Locator for CMIP products.
    - GOESProductLocatorRad: Locator for Rad products.
"""

from .locator_abi import GOESProductLocatorABI as GOESProductLocatorABI
from .locator_dc import GOESProductLocatorABIDC as GOESProductLocatorABIDC
from .locator_dc import GOESProductLocatorDMW as GOESProductLocatorDMW
from .locator_dc import GOESProductLocatorDMWV as GOESProductLocatorDMWV
from .locator_dp import GOESProductLocatorABIDP as GOESProductLocatorABIDP
from .locator_glm import GOESProductLocatorGLM as GOESProductLocatorGLM
from .locator_lp import GOESProductLocatorLCFA as GOESProductLocatorLCFA
from .locator_pm import GOESProductLocatorABIPM as GOESProductLocatorABIPM
from .locator_pm import GOESProductLocatorMCMIP as GOESProductLocatorMCMIP
from .locator_pp import GOESProductLocatorABIPP as GOESProductLocatorABIPP
from .locator_pp import GOESProductLocatorCMIP as GOESProductLocatorCMIP
from .locator_pp import GOESProductLocatorRad as GOESProductLocatorRad

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
]
