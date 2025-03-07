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
    concatenate,
    float64,
    isnan,
    nan,
    power,
    rad2deg,
    sqrt,
    where,
)

from .array import ArrayFloat64


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
    Calculate the coordinates of the edges of the pixels.

    Given the coordinates of the center of pixels, calculate the
    coordinates of the edges of the pixels using linear interpolation,
    i.e. the midpoints between the centers. For the first and last
    elements, the edges are calculated using linear extrapolation.

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
