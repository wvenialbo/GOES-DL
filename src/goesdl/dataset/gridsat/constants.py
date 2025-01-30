"""
Constants for the GridSat dataset file handling.

This module contains constants used for processing GridSat dataset
files, including file suffixes, date formats, and product versions.
"""

GRIDSAT_FILE_SUFFIX: str = ".nc"

B1_FILE_DATE_FORMAT: str = "%Y.%m.%d.%H"
B1_FILE_DATE_PATTERN: str = r"\d{4}\.\d{2}\.\d{2}\.\d{2}"
B1_FILE_PREFIX: str = "GRIDSAT"
B1_PATH_DATE_FORMAT: str = "%Y"
B1_PATH_PREFIX: str = ""
B1_PRODUCT_LATEST_VERSION: str = "v02r01"
B1_PRODUCT_NAME: str = "B1"

GOES_FILE_DATE_FORMAT: str = "%Y.%m.%d.%H%M"
GOES_FILE_DATE_PATTERN: str = r"\d{4}\.\d{2}\.\d{2}\.\d{4}"
GOES_FILE_PREFIX: str = "GridSat"
GOES_PATH_DATE_FORMAT: str = "%Y/%m"
GOES_PRODUCT_LATEST_VERSION: str = "v01"
