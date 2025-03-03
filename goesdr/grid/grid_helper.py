"""
Helper functions for the grid module.

These functions are used to calculate latitude and longitude grid data
from GOES ABI fixed grid projection data.

Functions
---------
compute_latlon_grid
    Calculate latitude and longitude grids.
"""

from numpy import (
    arctan,
    column_stack,
    concatenate,
    float32,
    float64,
    full,
    isnan,
    nan,
    power,
    rad2deg,
    sqrt,
    vstack,
    where,
)

from .array import ArrayFloat32, ArrayFloat64


def compute_latlon_grid(
    params: tuple[float64, float64, float64],
    sin_xy: tuple[ArrayFloat64, ArrayFloat64],
    cos_xy: tuple[ArrayFloat64, ArrayFloat64],
) -> tuple[ArrayFloat64, ArrayFloat64]:
    """
    Calculate latitude and longitude grids.

    Helper function for functions calculate_latlon_grid_opti and
    calculate_latlon_grid_fast.

    Parameters
    ----------
    params : tuple[float64, float64, float64]
        Tuple containing the orbital radius, semi-major axis, and
        semi-minor axis of the Earth.
    sin_xy : tuple[ArrayFloat64, ArrayFloat64]
        Tuple containing the sine values of the x and y grid points.
    cos_xy : tuple[ArrayFloat64, ArrayFloat64]
        Tuple containing the cosine values of the x and y grid points.

    Returns
    -------
    tuple[ArrayFloat32, ArrayFloat32]
        A tuple containing the latitude and longitude grid data.

    Notes
    -----
    Based on NOAA/NESDIS/STAR Aerosols and Atmospheric Composition
    Science Team's code found on [2], which is based on the GOES-R
    Product User Guide (PUG) Volume 5 (L2 products) Section 4.2.8.
    Retrieved at 2025-02-24.
    """

    r_orb, r_eq, r_pol = params
    sin_x, sin_y = sin_xy
    cos_x, cos_y = cos_xy

    # Equations to calculate latitude and longitude
    a_var = power(sin_x, 2.0) + (
        power(cos_x, 2.0)
        * (
            power(cos_y, 2.0)
            + (((r_eq * r_eq) / (r_pol * r_pol)) * power(sin_y, 2.0))
        )
    )

    b_var = -2.0 * r_orb * cos_x * cos_y
    c_var = (r_orb**2.0) - (r_eq**2.0)
    r_s = (-1.0 * b_var - sqrt((b_var**2) - (4.0 * a_var * c_var))) / (
        2.0 * a_var
    )

    s_x = r_s * cos_x * cos_y
    s_y = -r_s * sin_x
    s_z = r_s * cos_x * sin_y

    abi_lat: ArrayFloat64 = rad2deg(
        arctan(
            ((r_eq * r_eq) / (r_pol * r_pol))
            * (s_z / sqrt(((r_orb - s_x) * (r_orb - s_x)) + (s_y * s_y)))
        )
    )
    abi_lon: ArrayFloat64 = rad2deg(arctan(s_y / (s_x - r_orb)))

    abi_lat, abi_lon = make_common_mask(abi_lat, abi_lon)

    return abi_lat, abi_lon


def make_consistent(
    abi_lon: ArrayFloat64, abi_lat: ArrayFloat64
) -> tuple[ArrayFloat64, ArrayFloat64]:
    """
    Make the latitude and longitude grids consistent.

    Helper function for functions calculate_latlon_grid_cartopy and
    calculate_latlon_grid_pyproj.

    Parameters
    ----------
    abi_lon : ArrayFloat64
        The longitude grid data.
    abi_lat : ArrayFloat64
        The latitude grid data.

    Returns
    -------
    tuple[ArrayFloat64, ArrayFloat64]
        A tuple containing the consistent latitude and longitude grid
        data.
    """
    valid_lon = (abi_lon >= -360.0) & (abi_lon <= 360.0)
    valid_lat = (abi_lat >= -90.0) & (abi_lat <= 90.0)
    is_valid = valid_lon & valid_lat

    abi_lon = where(is_valid, abi_lon, nan)
    abi_lat = where(is_valid, abi_lat, nan)

    abi_lon = where(abi_lon >= 180, abi_lon - 360, abi_lon)
    abi_lon = where(abi_lon < -180, abi_lon + 360, abi_lon)

    return abi_lon, abi_lat


def make_common_mask(
    abi_lat: ArrayFloat64, abi_lon: ArrayFloat64
) -> tuple[ArrayFloat64, ArrayFloat64]:
    """
    Make the latitude and longitude grid masks consistent.

    Helper function for function calculate_latlon_grid_noaa and
    compute_latlon_grid.

    Parameters
    ----------
    abi_lat : ArrayFloat64
        The latitude grid data.
    abi_lon : ArrayFloat64
        The longitude grid data.

    Returns
    -------
    tuple[ArrayFloat64, ArrayFloat64]
        A tuple containing the consistent latitude and longitude grid
        data.
    """
    is_valid = ~(isnan(abi_lat) | isnan(abi_lon))

    abi_lat = where(is_valid, abi_lat, nan)
    abi_lon = where(is_valid, abi_lon, nan)

    return abi_lat, abi_lon


def calculate_pixel_edges(centers: ArrayFloat64) -> ArrayFloat64:
    """
    Calculate pixel edges coordinates from center coordinates.

    Parameters
    ----------
    centers : ArrayFloat64
        A n-elements 1-d array containing the coordinates of the center
        of pixels.

    Returns
    -------
    ArrayFloat64
        A (n+1)-elements 1-d array containing the coordinates of the
        edges of pixels.
    """
    left_offset: float64 = 2 * centers[0] - centers[1]
    right_offset: float64 = 2 * centers[-1] - centers[-2]

    left_centers = concatenate(([left_offset], centers))
    right_centers = concatenate((centers, [right_offset]))

    return 0.5 * (left_centers + right_centers)


def calculate_pixel_corners(
    lat: ArrayFloat32, lon: ArrayFloat32
) -> tuple[ArrayFloat32, ArrayFloat32]:
    """
    Calculate the coordinates of the intersection (corners) of the grid.

    Calculate the coordinates of the crossing-points of the latitude and
    longitude grids.

    Note
    ----
    This function is based on the algorithm found in [1]_. The function
    calculates a rough approximation and its results is no reliable; the
    size of the error is not negligible. We recommend using any of the
    other functions to calculate the latitude and longitude grids on the
    fly if you need a more accurate result using coordinates of corners.
    A better solution should be investigated and implemented in the
    future.

    Parameters
    ----------
    lat : ArrayFloat32
        The latitude grid data.
    lon : ArrayFloat32
        The longitude grid data.

    Returns
    -------
    tuple[ArrayFloat32, ArrayFloat32]
        A tuple containing the latitude and longitude grid data
        representing the corners of the grid.

    References
    ----------
    .. [1] Joao Henry Huamán Chinchay, "GOES: Python package to download
        and manipulate GOES-16/17/18 data.", GitHub repository, 2019.
        https://github.com/joaohenry23/GOES/
    """
    lat_grid = lat.astype(float64, copy=True)
    lat_grid = _midpoint_in_y(lat_grid)
    lat_grid = _midpoint_in_x(lat_grid)
    lat_grid = where(lat_grid < -400.0, nan, lat_grid)

    lon_grid = lon.astype(float64, copy=True)
    lon_grid = _midpoint_in_x(lon_grid)
    lon_grid = _midpoint_in_y(lon_grid)
    lon_grid = where(lon_grid < -400.0, nan, lon_grid)

    return lat_grid.astype(float32), lon_grid.astype(float32)


def _midpoint_in_x(grid: ArrayFloat64) -> ArrayFloat64:
    fill_value = float64(-999.99)
    fill_1 = full([grid.shape[0], 1], fill_value)
    fill_2 = full([grid.shape[0], 2], fill_value)

    grid = column_stack((grid, fill_1))
    right = column_stack((grid[:, 1:], fill_1))
    left_1 = column_stack((fill_1, grid[:, :-1]))
    left_2 = column_stack((fill_2, grid[:, :-2]))

    cond_1 = grid > -400.0
    cond_2 = grid < -400.0
    cond_3 = left_1 < -400.0
    cond_4 = left_1 > -400.0

    is_valid_1 = cond_1 & cond_3
    is_valid_2 = cond_1 & cond_4
    is_valid_3 = cond_2 & cond_4

    midpoint = where(is_valid_1, 0.5 * (3 * grid - right), fill_value)
    midpoint = where(is_valid_2, 0.5 * (grid + left_1), midpoint)
    midpoint = where(is_valid_3, 0.5 * (3 * left_1 - left_2), midpoint)

    return midpoint


def _midpoint_in_y(grid: ArrayFloat64) -> ArrayFloat64:
    fill_value = float64(-999.99)
    fill_1 = full([1, grid.shape[1]], fill_value)
    fill_2 = full([2, grid.shape[1]], fill_value)

    grid = vstack((grid, fill_1))
    lower = vstack((grid[1:, :], fill_1))
    upper_1 = vstack((fill_1, grid[:-1, :]))
    upper_2 = vstack((fill_2, grid[:-2, :]))

    cond_1 = grid > -400.0
    cond_2 = grid < -400.0
    cond_3 = upper_1 < -400.0
    cond_4 = upper_1 > -400.0

    is_valid_1 = cond_1 & cond_3
    is_valid_2 = cond_1 & cond_4
    is_valid_3 = cond_2 & cond_4

    midpoint = where(is_valid_1, 0.5 * (3 * grid - lower), fill_value)
    midpoint = where(is_valid_2, 0.5 * (grid + upper_1), midpoint)
    midpoint = where(is_valid_3, 0.5 * (3 * upper_1 - upper_2), midpoint)

    return midpoint
