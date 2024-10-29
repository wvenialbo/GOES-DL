"""
Constants for GOES dataset file handling.

This module contains constants used for handling GOES dataset files,
including file suffixes, date formats, and date patterns.
"""

GOESR_FILE_SUFFIX: str = ".nc"

GOESR_FILE_DATE_FORMAT: str = "%Y%j%H%M%S%f"
GOESR_FILE_DATE_PATTERN: str = r"\d{14}"
GOESR_PATH_DATE_FORMAT: str = "%Y/%j/%H"
