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

from ..projection import GOESABIFixedGrid, GOESProjection
from .array import ArrayFloat32, ArrayFloat64
from .grid_helper import make_consistent


def calculate_latlon_grid_pyproj(
    grid_data: GOESABIFixedGrid, projection_info: GOESProjection
) -> tuple[ArrayFloat32, ArrayFloat32]:
    """
    Calculate latitude and longitude grids using the pyproj package.

    Calculate latitude and longitude from GOES ABI fixed grid projection
    data. GOES ABI fixed grid projection is a map projection relative to
    the GOES satellite.

    Units: latitude in °N (°S < 0), longitude in °E (°W < 0)

    Parameters
    ----------
    grid_data : GOESABIFixedGrid
        Object containing the GOES ABI fixed grid coordinates in
        radians.
    projection_info : GOESProjection
        The projection information containing the satellite's
        perspective data.

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

    x_m: ArrayFloat64 = grid_data.x * projection_info.perspective_point_height
    y_m: ArrayFloat64 = grid_data.y * projection_info.perspective_point_height

    x_m, y_m = meshgrid(x_m, y_m)

    geos_proj = Proj(
        proj="geos",
        h=projection_info.perspective_point_height,
        lon_0=projection_info.longitude_of_projection_origin,
        sweep=projection_info.sweep_angle_axis,
        a=projection_info.semi_major_axis,
        b=projection_info.semi_minor_axis,
    )

    abi_lon: ArrayFloat64
    abi_lat: ArrayFloat64

    abi_lon, abi_lat = geos_proj(x_m, y_m, inverse=True)

    # The above is equivalent to the following:
    #
    # plate_carree_proj = Proj(proj="latlong", datum="WGS84")
    # transformer = Transformer.from_proj(geos_proj, plate_carree_proj)
    #
    # abi_lon, abi_lat = transformer.transform(x_m, y_m)

    abi_lon, abi_lat = make_consistent(abi_lon, abi_lat)

    return abi_lat.astype(float32), abi_lon.astype(float32)
