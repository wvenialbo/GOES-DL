"""
Export the class for the downloader object.

The downloader object is responsible for downloading files from a
specified location.

Classes
-------
Downloader
    Abstract a downloader object.
"""

from .downloader import Downloader
from .inventory import DatasetInventory

__all__ = ["DatasetInventory", "Downloader"]
