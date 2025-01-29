"""
Define and export constants used across the GOES-DL downloader module.

These constants include date and time formats, and other fixed values
that are used throughout the module.

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

ISO_TIMESTAMP_FORMAT: str = "%Y-%m-%dT%H:%M:%S%z"

# Default values for the time tolerance (in seconds).
TIME_TOLERANCE_DEFAULT: int = 60
TIME_TOLERANCE_MAX: int = 300
TIME_TOLERANCE_MIN: int = 30
