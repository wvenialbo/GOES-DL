"""
Define and export constants used across the GOES-DL downloader module.

These constants include date and time formats, and other fixed values
that are used throughout the module.

Classes
-------
DownloadStatus:
    Enumeration for download status.

Attributes
----------
ISO_TIMESTAMP_FORMAT : str
    The format string for ISO 8601 timestamps.
TIME_TOLERANCE_DEFAULT : int
    The default value for the time tolerance.
TIME_TOLERANCE_MAX : int
    The upper limit for the time tolerance.
TIME_TOLERANCE_MIN : int
    The lower limit for the time tolerance.
"""

from enum import Enum

ISO_TIMESTAMP_FORMAT: str = "%Y-%m-%dT%H:%M:%S%z"

# Default values for the time tolerance (in seconds).
TIME_TOLERANCE_DEFAULT: int = 60
TIME_TOLERANCE_MAX: int = 300
TIME_TOLERANCE_MIN: int = 30


class DownloadStatus(Enum):
    """
    Enumeration for download status.

    Attributes
    ----------
    SUCCESS
        Indicates that the download was successful.
    FAILED
        Indicates that the download failed.
    ALREADY
        Indicates that the file was already downloaded.
    """

    SUCCESS = 0
    FAILED = 1
    ALREADY = 2
