"""
Calculate latitude and longitude grids data using cartopy.

Notes
-----
See GOES-R Product User Guide (PUG) Volume 5 (L2 products) Section 4.2.8
for details & example of calculations.

Functions
---------
calculate_latlon_grid_cartopy
    Calculate latitude and longitude grids using the cartopy package.
"""

from numpy import float32, meshgrid

from ..array import ArrayFloat32, ArrayFloat64
from ..projection import GOESProjection
from .helper import make_consistent


def calculate_latlon_grid_cartopy(
    projection_info: GOESProjection,
) -> tuple[ArrayFloat32, ArrayFloat32]:
    """
    Calculate latitude and longitude grids using the cartopy package.

    Calculate latitude and longitude from GOES ABI fixed grid projection
    data. GOES ABI fixed grid projection is a map projection relative to
    the GOES satellite.

    Units: latitude in °N (°S < 0), longitude in °E (°W < 0)

    Parameters:
    -----------
    projection_info : GOESProjection
        Object containing the satellite's projection information and
        GOES ABI fixed grid data.

    Returns:
    --------
    tuple[ArrayFloat32, ArrayFloat32]
        A tuple containing the latitude and longitude grid data.
    """
    try:
        import cartopy.crs as ccrs
    except ImportError as error:
        raise ImportError(
            "The 'cartopy' package is required for this functionality."
        ) from error

    x_m: ArrayFloat64
    y_m: ArrayFloat64
    x_m, y_m = meshgrid(projection_info.x_m, projection_info.y_m)

    globe_geos = ccrs.Globe(
        ellipse=None,
        semimajor_axis=projection_info.semi_major_axis,
        semiminor_axis=projection_info.semi_minor_axis,
    )

    geos_proj = ccrs.Geostationary(
        satellite_height=projection_info.perspective_point_height,
        central_longitude=projection_info.longitude_of_projection_origin,
        sweep_axis=projection_info.sweep_angle_axis,
        globe=globe_geos,
    )

    plate_carree_proj = ccrs.PlateCarree(globe=globe_geos)

    points = plate_carree_proj.transform_points(geos_proj, x_m, y_m)

    abi_lon: ArrayFloat64 = points[..., 0]
    abi_lat: ArrayFloat64 = points[..., 1]

    abi_lon, abi_lat = make_consistent(abi_lon, abi_lat)

    return abi_lat.astype(float32), abi_lon.astype(float32)
