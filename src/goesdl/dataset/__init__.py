"""
Export class providing the base functionalities for product locators.

Classes:
    - ProductLocator: Abstract a product locator for satellite imagery
      datasets.
    - ProductLocatorGG: Abstract a GridSat or GOES-R series dataset
      product locator.
"""

from .locator import ProductLocator
from .locator_gg import ProductLocatorGG

__all__ = ["ProductLocator", "ProductLocatorGG"]
