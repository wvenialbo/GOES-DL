"""
Define and export constants used across the GOES-DL datasource module.

These constants include date and time formats, and other fixed values
that are used throughout the module.

Classes
-------
DownloadStatus:
    Enumeration for download status.
"""

from enum import Enum


class DownloadStatus(Enum):
    """
    Enumeration for download status.

    Attributes
    ----------
    SUCCESS : int
        Indicates that the download was successful.
    FAILED : int
        Indicates that the download failed.
    ALREADY : int
        Indicates that the file was already downloaded.
    """

    SUCCESS = 0
    FAILED = 1
    ALREADY = 2
