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
calculate_latlon_grid_pyproj_deprecated
    Calculate latitude and longitude grids using the pyproj package.
"""

from netCDF4 import Dataset  # pylint: disable=no-name-in-module
from numpy import float32, meshgrid, nan, where

from ..projection import GOESABIFixedGridArray, GOESProjection
from .array import ArrayFloat32, ArrayFloat64


def calculate_latlon_grid_pyproj(
    record: Dataset,
) -> tuple[ArrayFloat32, ArrayFloat32]:
    """
    Calculate latitude and longitude grids using the pyproj package.

    Calculate latitude and longitude from GOES ABI fixed grid projection
    data. GOES ABI fixed grid projection is a map projection relative to
    the GOES satellite.

    Units: latitude in °N (°S < 0), longitude in °E (°W < 0)

    Parameters
    ----------
    record : Dataset
        The netCDF dataset containing ABI L1b or L2 data.

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

    grid_data = GOESABIFixedGridArray(record)
    projection_info = GOESProjection(record)

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

    valid_lon = (abi_lon >= -360.0) & (abi_lon <= 360.0)
    valid_lat = (abi_lat >= -90.0) & (abi_lat <= 90.0)
    is_valid = valid_lon & valid_lat

    abi_lon = where(is_valid, abi_lon, nan)
    abi_lat = where(is_valid, abi_lat, nan)

    abi_lon = where(abi_lon >= 180, abi_lon - 360, abi_lon)
    abi_lon = where(abi_lon < -180, abi_lon + 360, abi_lon)

    return abi_lat.astype(float32), abi_lon.astype(float32)
