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
    dtype,
    float64,
    isnan,
    nan,
    ndarray,
    power,
    rad2deg,
    sqrt,
    where,
)

ArrayFloat64 = ndarray[tuple[int, ...], dtype[float64]]


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

    is_valid = ~(isnan(abi_lat) | isnan(abi_lon))

    abi_lat = where(is_valid, abi_lat, nan)
    abi_lon = where(is_valid, abi_lon, nan)

    return abi_lat, abi_lon
