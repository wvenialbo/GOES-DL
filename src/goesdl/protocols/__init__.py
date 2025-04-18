"""Protocols for GOES-DL Satellite Imagery Dataset Accessing Toolbox.

This module contains the protocols for the GOES-R Series data
extraction and processing. The protocols define the structure of
the data, including the grid data, image data, and region of
interest (ROI). The protocols are used to ensure that the data
extracted from the satellite dataset is in the correct format
and can be processed correctly.
"""

from .geodetic import GeodeticGrid, GeodeticRegion
from .image import SatImageData

__all__ = [
    "GeodeticGrid",
    "GeodeticRegion",
    "SatImageData",
]
