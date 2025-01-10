"""
Define and export constants used across the GOES-DL project.

These constants include date and time formats, file naming patterns, and other
fixed values that are used throughout the project.

Attributes
----------
ISO_TIMESTAMP_FORMAT : str
    The format string for ISO 8601 timestamps.
"""

ISO_TIMESTAMP_FORMAT: str = "%Y-%m-%dT%H:%M:%S%z"

# Default values for the time tolerance (in seconds).
TIME_TOLERANCE_DEFAULT: int = 60
TIME_TOLERANCE_MAX: int = 300
TIME_TOLERANCE_MIN: int = 30
