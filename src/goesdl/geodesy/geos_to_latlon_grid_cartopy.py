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

from ..utils.array import ArrayFloat32, ArrayFloat64
from .helpers import make_consistent
from .geostationary_parameters import GeostationaryParameters


def geos_to_latlon_grid_cartopy(
    projection_info: GeostationaryParameters,
) -> tuple[ArrayFloat32, ArrayFloat32]:
    """
    Calculate latitude and longitude grids using the cartopy package.

    Calculate latitude and longitude from GOES ABI fixed grid projection
    data. GOES ABI fixed grid projection is a map projection relative to
    the GOES satellite.

    Units: latitude in °N (°S < 0), longitude in °E (°W < 0)

    Parameters:
    -----------
    projection_info : ProjectionParameters
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

    globe_geos = ccrs.Globe(
        ellipse=None,
        semimajor_axis=projection_info.globe.semi_major_axis,
        semiminor_axis=projection_info.globe.semi_minor_axis,
        inverse_flattening=projection_info.globe.inverse_flattening,
    )

    geos_proj = ccrs.Geostationary(
        satellite_height=projection_info.orbit.perspective_point_height,
        central_longitude=projection_info.orbit.longitude_of_projection_origin,
        sweep_axis=projection_info.orbit.sweep_angle_axis,
        globe=globe_geos,
    )

    plate_carree_proj = ccrs.PlateCarree(globe=globe_geos)

    x_m: ArrayFloat64
    y_m: ArrayFloat64
    x_m, y_m = meshgrid(projection_info.x_m, projection_info.y_m)

    points = plate_carree_proj.transform_points(geos_proj, x_m, y_m)

    abi_lon: ArrayFloat64 = points[..., 0]
    abi_lat: ArrayFloat64 = points[..., 1]

    abi_lon, abi_lat = make_consistent(abi_lon, abi_lat)

    return abi_lat.astype(float32), abi_lon.astype(float32)
