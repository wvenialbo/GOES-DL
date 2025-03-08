"""
Helper functions for the grid module.

These functions are used to calculate latitude and longitude grid data
from GOES ABI fixed grid projection data.

Functions
---------
make_consistent
    Make the latitude and longitude grids consistent.
make_common_mask
    Make the latitude and longitude grid masks consistent.
calculate_pixel_edges
    Calculate the coordinates of the edges of the pixels.
"""

from numpy import (
    concatenate,
    float64,
    isnan,
    nan,
    where,
)

from .array import ArrayFloat64


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
        A tuple containing consistently masked latitude and longitude
        grid data.
    """
    is_nan = isnan(abi_lat) | isnan(abi_lon)

    abi_lat = where(is_nan, nan, abi_lat)
    abi_lon = where(is_nan, nan, abi_lon)

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
