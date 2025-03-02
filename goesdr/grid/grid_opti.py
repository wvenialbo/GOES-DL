"""
Calculate latitude and longitude grids data.

Notes
-----
See GOES-R Product User Guide (PUG) Volume 5 (L2 products) Section 4.2.8
for details & example of calculations.

Functions
---------
calculate_latlon_opti
    Calculate latitude and longitude grids using an optimized version of
    NOAA's algorithm.
"""

from netCDF4 import Dataset  # pylint: disable=no-name-in-module
from numpy import (
    cos,
    dtype,
    float32,
    float64,
    meshgrid,
    ndarray,
    sin,
)

from ..projection import GOESABIFixedGridArray, GOESProjection
from .grid_helper import compute_latlon_grid

ArrayFloat32 = ndarray[tuple[int, ...], dtype[float32]]
ArrayFloat64 = ndarray[tuple[int, ...], dtype[float64]]


def calculate_latlon_grid_opti(
    record: Dataset,
) -> tuple[ArrayFloat32, ArrayFloat32]:
    """
    Calculate latitude and longitude grids.

    Calculate latitude and longitude from GOES ABI fixed grid projection
    data using an optimized version of NOAA's algorithm. GOES ABI fixed
    grid projection is a map projection relative to the GOES satellite.

    Units: latitude in °N (°S < 0), longitude in °E (°W < 0)

    Parameters
    ----------
    file_id : Dataset
        The netCDF dataset containing ABI L1b or L2 data. It is .nc file
        opened using the netCDF4 library.
    """
    # Reorganize operations to leverage NumPy vectorization,
    # reducing redundant computations. This yields ~6x performance
    # improvement over the baseline implementation from [2].
    projection_info = GOESProjection(record)

    lambda_0 = projection_info.longitude_of_projection_origin

    r_orb = projection_info.orbital_radius
    r_eq = projection_info.semi_major_axis
    r_pol = projection_info.semi_minor_axis

    grid_data = GOESABIFixedGridArray(record)

    sin_x: ArrayFloat64 = sin(grid_data.x)
    cos_x: ArrayFloat64 = cos(grid_data.x)
    sin_y: ArrayFloat64 = sin(grid_data.y)
    cos_y: ArrayFloat64 = cos(grid_data.y)

    sin_x, sin_y = meshgrid(sin_x, sin_y)
    cos_x, cos_y = meshgrid(cos_x, cos_y)

    lat, lon = compute_latlon_grid(
        (r_orb, r_eq, r_pol),
        (sin_x, sin_y),
        (cos_x, cos_y),
    )

    return lat.astype(float32), (lon + lambda_0).astype(float32)
