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
