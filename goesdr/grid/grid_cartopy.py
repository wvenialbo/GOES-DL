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

from netCDF4 import Dataset  # pylint: disable=no-name-in-module
from numpy import float32, meshgrid, nan, where

from ..projection import GOESABIFixedGridArray, GOESProjection
from .array import ArrayFloat32, ArrayFloat64


def calculate_latlon_grid_cartopy(
    record: Dataset,
) -> tuple[ArrayFloat32, ArrayFloat32]:
    """
    Calculate latitude and longitude grids using the cartopy package.

    Calculate latitude and longitude from GOES ABI fixed grid projection
    data. GOES ABI fixed grid projection is a map projection relative to
    the GOES satellite.

    Units: latitude in °N (°S < 0), longitude in °E (°W < 0)

    Parameters:
    -----------
    record : Dataset
        The netCDF dataset containing GOES ABI L1b or L2 data with ABI
        fixed grid projection information. It is .nc file opened using
        the netCDF4 library.

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

    grid_data = GOESABIFixedGridArray(record)
    projection_info = GOESProjection(record)

    x_m: ArrayFloat64 = grid_data.x * projection_info.perspective_point_height
    y_m: ArrayFloat64 = grid_data.y * projection_info.perspective_point_height

    x_m, y_m = meshgrid(x_m, y_m)

    globe = ccrs.Globe(
        ellipse=None,
        semimajor_axis=projection_info.semi_major_axis,
        semiminor_axis=projection_info.semi_minor_axis,
    )

    geos_proj = ccrs.Geostationary(
        satellite_height=projection_info.perspective_point_height,
        central_longitude=projection_info.longitude_of_projection_origin,
        sweep_axis=projection_info.sweep_angle_axis,
        globe=globe,
    )

    globe_wgs84 = ccrs.Globe(ellipse="WGS84")

    plate_carree = ccrs.PlateCarree(globe=globe_wgs84)

    points = plate_carree.transform_points(geos_proj, x_m, y_m)

    abi_lon: ArrayFloat64 = points[..., 0]
    abi_lat: ArrayFloat64 = points[..., 1]

    valid_lon = (abi_lon >= -360.0) & (abi_lon <= 360.0)
    valid_lat = (abi_lat >= -90.0) & (abi_lat <= 90.0)
    is_valid = valid_lon & valid_lat

    abi_lon = where(is_valid, abi_lon, nan)
    abi_lat = where(is_valid, abi_lat, nan)

    abi_lon = where(abi_lon >= 180, abi_lon - 360, abi_lon)
    abi_lon = where(abi_lon < -180, abi_lon + 360, abi_lon)

    return abi_lat.astype(float32), abi_lon.astype(float32)
