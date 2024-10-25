"""
Export class providing the base functionalities for product locators.

Classes:
    - ProductLocatorGG: Abstract a GridSat or GOES-R series dataset
      product locator.
"""

from .locator_gg import ProductLocatorGG as ProductLocatorGG

__all__ = ["ProductLocatorGG"]
