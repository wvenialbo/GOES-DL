"""
Export the class for the downloader object.

The downloader object is responsible for downloading files from a
specified location.

Classes
-------
Downloader
    Abstract a downloader object.
"""

from .downloader import Downloader as Downloader

__all__ = ["Downloader"]
