"""
Provide functions for latitude and longitude grid calculation.

These functions calculate latitude and longitude grid data from GOES ABI
fixed grid projection data. GOES ABI fixed grid projection is a map
projection relative to the GOES satellite.

Notes
-----
See [2]_, GOES-R Product User Guide (PUG) Volume 5 (L2 products) Section
4.2.8 for details & example of calculations.

Functions
---------
calculate_latlon_noaa
    Calculate latitude and longitude grids using NOAA's algorithm.

References
----------
.. [1] STAR Atmospheric Composition Product Training, "GOES Imager
    Projection (ABI Fixed Grid)", NOAA/NESDIS/STAR, 2024.
    https://www.star.nesdis.noaa.gov/atmospheric-composition-training/satellite_data_goes_imager_projection.php.
.. [2] Aerosols and Atmospheric Composition Science Team, "Python Short
    Demo: Calculate Latitude and Longitude from GOES Imager Projection
    (ABI Fixed Grid) Information", NOAA/NESDIS/STAR, 2024.
    https://www.star.nesdis.noaa.gov/atmospheric-composition-training/python_abi_lat_lon.php
.. [3] GOES-R, " GOES-R Series Product Definition and User’s Guide
    (PUG), Volume 5: Level 2+ Products", Version 2.4, NASA/NOAA/NESDIS,
    2022.
    https://www.ospo.noaa.gov/Organization/Documents/PUG/GS%20Series%20416-R-PUG-L2%20Plus-0349%20Vol%205%20v2.4.pdf

"""

from .grid_fast import calculate_latlon_grid_fast
from .grid_noaa import calculate_latlon_grid_noaa
from .grid_opti import calculate_latlon_grid_opti

__all__ = [
    "calculate_latlon_grid_fast",
    "calculate_latlon_grid_noaa",
    "calculate_latlon_grid_opti",
]
