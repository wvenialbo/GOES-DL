"""
Calculate latitude and longitude grids data.

Notes
-----
See GOES-R Product User Guide (PUG) Volume 5 (L2 products) Section 4.2.8
for details & example of calculations.

Functions
---------
calculate_latlon_grid_goesdr
    Calculate latitude and longitude grids using an optimized version of
    classic's algorithm.
"""

from numpy import (
    arctan,
    cos,
    float32,
    float64,
    meshgrid,
    power,
    rad2deg,
    sin,
    sqrt,
)

from ..array import ArrayFloat32, ArrayFloat64
from ..projection import GOESProjection
from .helper import make_common_mask


def calculate_latlon_grid_goesdr(
    projection_info: GOESProjection,
) -> tuple[ArrayFloat32, ArrayFloat32]:
    """
    Calculate latitude and longitude grids.

    Calculate latitude and longitude from GOES ABI fixed grid projection
    data using an optimized version of NOAA's algorithm. GOES ABI fixed
    grid projection is a map projection relative to the GOES satellite.

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
    projection_info : GOESProjection
        Object containing the satellite's projection information and
        GOES ABI fixed grid data.

    Returns
    -------
    tuple[ArrayFloat32, ArrayFloat32]
        A tuple containing the latitude and longitude grid data.

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
    # Reorganize operations to leverage NumPy vectorization,
    # reducing redundant computations. This yields ~6x performance
    # improvement over the baseline implementation from [2].
    lambda_0 = projection_info.longitude_of_projection_origin

    r_orb = projection_info.orbital_radius
    r_eq = projection_info.semi_major_axis
    r_pol = projection_info.semi_minor_axis

    x_r = projection_info.x
    y_r = projection_info.y

    sin_x: ArrayFloat64 = sin(x_r)
    cos_x: ArrayFloat64 = cos(x_r)
    sin_y: ArrayFloat64 = sin(y_r)
    cos_y: ArrayFloat64 = cos(y_r)

    sin_x, sin_y = meshgrid(sin_x, sin_y)
    cos_x, cos_y = meshgrid(cos_x, cos_y)

    lat, lon = _transform_grid(
        (r_orb, r_eq, r_pol),
        (sin_x, sin_y),
        (cos_x, cos_y),
    )

    return lat.astype(float32), (lon + lambda_0).astype(float32)


def _transform_grid(
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
