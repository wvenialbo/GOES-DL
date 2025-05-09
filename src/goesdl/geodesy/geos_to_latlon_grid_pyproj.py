"""
Calculate latitude and longitude grids data using pyproj.

Notes
-----
See GOES-R Product User Guide (PUG) Volume 5 (L2 products) Section 4.2.8
for details & example of calculations.

Functions
---------
calculate_latlon_grid_pyproj
    Calculate latitude and longitude grids using the pyproj package.
"""

from numpy import float32, meshgrid

from ..utils.array import ArrayFloat32, ArrayFloat64
from .helpers import make_consistent
from .geostationary_parameters import GeostationaryParameters


def geos_to_latlon_grid_pyproj(
    projection_info: GeostationaryParameters,
) -> tuple[ArrayFloat32, ArrayFloat32]:
    """
    Calculate latitude and longitude grids using the pyproj package.

    Calculate latitude and longitude from GOES ABI fixed grid projection
    data. GOES ABI fixed grid projection is a map projection relative to
    the GOES satellite.

    Units: latitude in °N (°S < 0), longitude in °E (°W < 0)

    Parameters
    ----------
    projection_info : GOESProjection
        Object containing the satellite's projection information and
        GOES ABI fixed grid data.

    Returns
    -------
    tuple[ArrayFloat32, ArrayFloat32]
        A tuple containing the latitude and longitude grid data.
    """
    try:
        from pyproj import Proj  # , Transformer
    except ImportError as error:
        raise ImportError(
            "The 'pyproj' package is required for this functionality."
        ) from error

    geos_proj = Proj(
        proj="geos",
        h=projection_info.orbit.perspective_point_height,
        lon_0=projection_info.orbit.longitude_of_projection_origin,
        sweep=projection_info.orbit.sweep_angle_axis,
        a=projection_info.globe.semi_major_axis,
        b=projection_info.globe.semi_minor_axis,
        rf=projection_info.globe.inverse_flattening,
    )

    x_m: ArrayFloat64
    y_m: ArrayFloat64
    x_m, y_m = meshgrid(projection_info.x_m, projection_info.y_m)

    abi_lon: ArrayFloat64
    abi_lat: ArrayFloat64
    abi_lon, abi_lat = geos_proj(x_m, y_m, inverse=True)

    # The above is equivalent to the following:
    #
    # plate_carree_proj = Proj(
    #     proj="latlong",
    #     a=projection_info.globe.semi_major_axis,
    #     b=projection_info.globe.semi_minor_axis,
    #     rf=projection_info.globe.inverse_flattening,
    # )
    # transformer = Transformer.from_proj(geos_proj, plate_carree_proj)
    #
    # abi_lon, abi_lat = transformer.transform(x_m, y_m)

    abi_lon, abi_lat = make_consistent(abi_lon, abi_lat)

    return abi_lat.astype(float32), abi_lon.astype(float32)
