"""
Calculate latitude and longitude grids data.

Notes
-----
See GOES-R Product User Guide (PUG) Volume 5 (L2 products) Section 4.2.8
for details & example of calculations.

Functions
---------
calculate_latlon_grid
    Calculate latitude and longitude grids from geostationary grid.
"""

from typing import Literal

from ..utils.array import ArrayFloat32
from .geos_to_latlon_grid_cartopy import geos_to_latlon_grid_cartopy
from .geos_to_latlon_grid_goesdl import geos_to_latlon_grid_goesdl
from .geos_to_latlon_grid_pyproj import geos_to_latlon_grid_pyproj
from .geostationary_parameters import GeostationaryParameters


def geos_to_latlon_grid(
    parameters: GeostationaryParameters,
    algorithm: Literal["cartopy", "goesdl", "pyproj"] = "goesdl",
) -> tuple[ArrayFloat32, ArrayFloat32]:
    if algorithm == "cartopy":
        return geos_to_latlon_grid_cartopy(parameters)
    if algorithm == "pyproj":
        return geos_to_latlon_grid_pyproj(parameters)
    return geos_to_latlon_grid_goesdl(parameters)
