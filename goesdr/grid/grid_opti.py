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
from numpy import cos, float32, meshgrid, sin

from ..projection import GOESABIFixedGridArray, GOESProjection
from .array import ArrayFloat32, ArrayFloat64
from .grid_helper import compute_latlon_grid


def calculate_latlon_grid_opti(
    record: Dataset,
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
    record : Dataset
        The netCDF dataset containing GOES ABI L1b or L2 data with ABI
        fixed grid projection information. It is .nc file opened using
        the netCDF4 library.

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
    projection_info = GOESProjection(record)

    lambda_0 = projection_info.longitude_of_projection_origin

    r_orb = projection_info.orbital_radius
    r_eq = projection_info.semi_major_axis
    r_pol = projection_info.semi_minor_axis

    grid_data = GOESABIFixedGridArray(record)

    x_r = grid_data.x
    y_r = grid_data.y

    sin_x: ArrayFloat64 = sin(x_r)
    cos_x: ArrayFloat64 = cos(x_r)
    sin_y: ArrayFloat64 = sin(y_r)
    cos_y: ArrayFloat64 = cos(y_r)

    sin_x, sin_y = meshgrid(sin_x, sin_y)
    cos_x, cos_y = meshgrid(cos_x, cos_y)

    lat, lon = compute_latlon_grid(
        (r_orb, r_eq, r_pol),
        (sin_x, sin_y),
        (cos_x, cos_y),
    )

    return lat.astype(float32), (lon + lambda_0).astype(float32)
