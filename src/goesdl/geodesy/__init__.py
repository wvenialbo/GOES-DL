"""
Provide functions for latitude and longitude grid calculation.

These functions calculate latitude and longitude grid data from GOES ABI
fixed grid projection data. GOES ABI fixed grid projection is a map
projection relative to the GOES satellite.

Notes
-----
See [2]_, GOES-R Product User Guide (PUG) Volume 5 (L2 products) Section
4.2.8 for details & example of calculations.

Classes
-------
GeostationaryParameters
    Class to store GOES ABI fixed grid projection parameters.

Functions
---------
geos_to_latlon_grid
    Calculate latitude and longitude grids using a given algorithm.
geos_to_latlon_grid_cartopy
    Calculate latitude and longitude grids using the cartopy package.
geos_to_latlon_grid_goesdl
    Calculate latitude and longitude grids using an optimized version of
    classic's algorithm.
geos_to_latlon_grid_pyproj
    Calculate latitude and longitude grids using the pyproj package.
calculate_pixel_edges
    Calculate the pixel edges of the GOES ABI fixed grid.

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

from .geos_to_latlon_grid import geos_to_latlon_grid
from .geos_to_latlon_grid_cartopy import geos_to_latlon_grid_cartopy
from .geos_to_latlon_grid_goesdl import geos_to_latlon_grid_goesdl
from .geos_to_latlon_grid_pyproj import geos_to_latlon_grid_pyproj
from .geostationary_parameters import GeostationaryParameters
from .helpers import calculate_pixel_edges
from .rectangular_region import RectangularRegion

__all__ = [
    "calculate_pixel_edges",
    "geos_to_latlon_grid",
    "geos_to_latlon_grid_cartopy",
    "geos_to_latlon_grid_goesdl",
    "geos_to_latlon_grid_pyproj",
    "GeostationaryParameters",
    "RectangularRegion",
]
