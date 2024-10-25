"""
Export class providing the base functionalities for product locators.

Classes:
    - ProductLocator: Abstract a product locator for GridSat family of
    imagery datasets.
"""

from .locator import ProductLocator as ProductLocator

__all__ = ["ProductLocator"]
