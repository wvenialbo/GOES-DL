"""
Export the class for the downloader object.

The downloader object is responsible for downloading files from a
specified location.

Classes
-------
Downloader
    Abstract a downloader object.
DownloaderRepository
    Manage file operations for the downloader object.
"""

from .downloader import Downloader as Downloader
from .downloader_repository import DownloaderRepository as DownloaderRepository
