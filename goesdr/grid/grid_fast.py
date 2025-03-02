"""
Calculate latitude and longitude grids data.

Notes
-----
See GOES-R Product User Guide (PUG) Volume 5 (L2 products) Section 4.2.8
for details & example of calculations.

Functions
---------
calculate_latlon_grid_opti_fast
    Calculate latitude and longitude grids using a shortened version of
    the optimized algorithm.
"""

from netCDF4 import Dataset  # pylint: disable=no-name-in-module
from numpy import (
    cos,
    dtype,
    float32,
    float64,
    hstack,
    meshgrid,
    ndarray,
    sin,
    vstack,
)

from ..projection import GOESABIFixedGridArray, GOESProjection
from .grid_helper import compute_latlon_grid

ArrayFloat32 = ndarray[tuple[int, ...], dtype[float32]]
ArrayFloat64 = ndarray[tuple[int, ...], dtype[float64]]


def calculate_latlon_grid_fast(
    record: Dataset,
) -> tuple[ArrayFloat32, ArrayFloat32]:
    """
    Calculate latitude and longitude grids.

    Calculate latitude and longitude from GOES ABI fixed grid projection
    data using a shortened version of the optimized algorithm. The
    function only computes the first quadrant of the grid and then
    reconstructs the remaining quadrants. GOES ABI fixed grid projection
    is a map projection relative to the GOES satellite.

    Units: latitude in °N (°S < 0), longitude in °E (°W < 0)

    Notes
    -----
    For information on GOES Imager Projection and GOES orbit geometry,
    see [1]_ and Section 4.2. of [3]_. For a Python demonstration on
    calculating latitude and longitude from GOES Imager Projection
    information, see [2]_. The code snippet in this class is based on
    the Python demonstration in [2]_.

    Parameters
    ----------
    record : Dataset
        The netCDF dataset containing ABI L1b or L2 data. It is .nc file
        opened using the netCDF4 library.

    References
    ----------
    .. [1] STAR Atmospheric Composition Product Training, "GOES Imager
        Projection (ABI Fixed Grid)", NOAA/NESDIS/STAR, 2024.
        https://www.star.nesdis.noaa.gov/atmospheric-composition-training/satellite_data_goes_imager_projection.php.
    .. [2] Aerosols and Atmospheric Composition Science Team, "Python
        Short Demo: Calculate Latitude and Longitude from GOES Imager
        Projection (ABI Fixed Grid) Information", NOAA/NESDIS/STAR,
        2024.
        https://www.star.nesdis.noaa.gov/atmospheric-composition-training/python_abi_lat_lon.php
    .. [3] GOES-R, " GOES-R Series Product Definition and User’s Guide
        (PUG), Volume 5: Level 2+ Products", Version 2.4,
        NASA/NOAA/NESDIS, 2022.
        https://www.ospo.noaa.gov/Organization/Documents/PUG/GS%20Series%20416-R-PUG-L2%20Plus-0349%20Vol%205%20v2.4.pdf
    """
    # Harness geodetic grid symmetry from geostationary perspective
    # to reduce the number of computations. Achieve ~24x performance
    # gain compared to the reference implementation in [2].
    projection_info = GOESProjection(record)

    lambda_0 = projection_info.longitude_of_projection_origin

    r_orb = projection_info.orbital_radius
    r_eq = projection_info.semi_major_axis
    r_pol = projection_info.semi_minor_axis

    # Compute only the first quadrant of the grid
    grid_data = GOESABIFixedGridArray(record)

    # pylint: disable=no-member # pylint false positive
    center = grid_data.x.size // 2
    odd_size = bool(grid_data.x.size % 2)
    # pylint: enable=no-member

    # pylint: disable=unsubscriptable-object # pylint false positive
    grid_x = grid_data.x[center:]
    grid_y = grid_x[::-1]
    # pylint: enable=unsubscriptable-object

    sin_x: ArrayFloat64 = sin(grid_x)
    cos_x: ArrayFloat64 = cos(grid_x)
    sin_y: ArrayFloat64 = sin(grid_y)
    cos_y: ArrayFloat64 = cos(grid_y)

    sin_x, sin_y = meshgrid(sin_x, sin_y)
    cos_x, cos_y = meshgrid(cos_x, cos_y)

    lat, lon = compute_latlon_grid(
        (r_orb, r_eq, r_pol),
        (sin_x, sin_y),
        (cos_x, cos_y),
    )

    lat = _reconstruct_lat_grid(lat, odd_size)
    lon = _reconstruct_lon_grid(lon, odd_size)

    return lat.astype(float32), (lon + lambda_0).astype(float32)


def _reconstruct_lat_grid(
    northeast_grid: ArrayFloat64, odd_size: bool
) -> ArrayFloat64:
    southeast_grid = (
        -northeast_grid[-2::-1, :] if odd_size else -northeast_grid[::-1, :]
    )
    east_grid = vstack((northeast_grid, southeast_grid))
    west_grid = east_grid[:, -1:0:-1] if odd_size else east_grid[:, ::-1]
    return hstack((west_grid, east_grid))


def _reconstruct_lon_grid(
    northeast_grid: ArrayFloat64, odd_size: bool
) -> ArrayFloat64:
    northwest_grid = (
        -northeast_grid[:, -1:0:-1] if odd_size else -northeast_grid[:, ::-1]
    )
    north_grid = hstack((northwest_grid, northeast_grid))
    south_grid = north_grid[-2::-1, :] if odd_size else north_grid[::-1, :]
    return vstack((north_grid, south_grid))
