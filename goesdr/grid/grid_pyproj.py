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
from numpy import float32, meshgrid

from ..projection import GOESABIFixedGridArray, GOESProjection
from .array import ArrayFloat32, ArrayFloat64
from .grid_helper import calculate_pixel_edges, make_consistent


def calculate_latlon_grid_pyproj(
    record: Dataset, corners: bool, step: tuple[int, int] | None
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
        The netCDF dataset containing GOES ABI L1b or L2 data with ABI
        fixed grid projection information. It is .nc file opened using
        the netCDF4 library.
    corners : bool
        If True, calculate the coordinates of the intersections
        (corners) of the grid. If False, calculate the coordinates of
        the center of the grid.

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

    if corners:
        x_m = calculate_pixel_edges(x_m)
        y_m = calculate_pixel_edges(y_m)

    if step:
        x_m = x_m[:: step[1]]
        y_m = y_m[:: step[0]]

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
