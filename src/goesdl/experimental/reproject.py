import math
from typing import cast

import numpy as np
from cartopy.crs import PlateCarree, Projection
from numpy import float32
from numpy.ma import MaskedArray
from scipy.spatial import cKDTree

from ..utils.array import ArrayBool, ArrayFloat32, MaskedFloat32
from .geodesy import get_extent_metre


def calculate_image_size(
    extent_deg: tuple[float, float],
    resolution_m: float,
    target_crs: Projection,
) -> tuple[int, int]:
    n_rows, n_cols, _, _ = calculate_matrix_size(
        extent_deg, resolution_m, target_crs
    )

    return n_cols, n_rows


def calculate_matrix_size(
    extent_deg: tuple[float, float],
    resolution_m: float,
    target_crs: Projection,
) -> tuple[int, int, float, float]:
    # Compute the extent size in metres
    width_m, height_m = get_extent_metre(extent_deg, target_crs)

    # Compute the grid size
    n_cols = 2 * (math.ceil(width_m / resolution_m) // 2)
    n_rows = 2 * (math.ceil(height_m / resolution_m) // 2)

    return n_rows, n_cols, height_m, width_m


def create_matrix(
    data: MaskedFloat32 | ArrayFloat32,
    lat: ArrayFloat32,
    lon: ArrayFloat32,
    extent_deg: tuple[float, float],
    resolution_m: float,
    target_crs: Projection,
) -> ArrayFloat32:
    n_rows, n_cols, height_m, width_m = calculate_matrix_size(
        extent_deg, resolution_m, target_crs
    )

    half_width_m = 0.5 * width_m
    half_height_m = 0.5 * height_m

    # Create the target grid in projected coordinates
    x_target = np.linspace(-half_width_m, half_width_m, n_cols)
    y_target = np.linspace(half_height_m, -half_height_m, n_rows)
    x_target_grid, y_target_grid = np.meshgrid(x_target, y_target)

    # Define the source projection
    source_crs = PlateCarree(globe=target_crs.globe)

    # Transform the target grid coordinates to lat/lon
    points = cast(
        ArrayFloat32,
        source_crs.transform_points(target_crs, x_target_grid, y_target_grid),
    )
    lon_grid, lat_grid = points[..., 0], points[..., 1]

    if isinstance(data, MaskedArray):
        valid_mask = cast(ArrayBool, ~data.mask)
        field_value = data.data[valid_mask]
        roi_lat = lat[valid_mask]
        roi_lon = lon[valid_mask]
    else:
        field_value = data
        roi_lat = lat
        roi_lon = lon

    # Flatten the grids
    target_points = np.vstack((lon_grid.ravel(), lat_grid.ravel())).T
    source_points = np.vstack((roi_lon.ravel(), roi_lat.ravel())).T
    data_flat = cast(ArrayFloat32, field_value.ravel())

    # Build KDTree and interpolate
    tree = cKDTree(source_points)
    _, idx = tree.query(
        target_points, k=4
    )  # Get the 4 nearest neighbors for bilinear interpolation
    weights = 1 / np.maximum(
        tree.query(target_points, k=4)[0], 1e-12
    )  # Avoid division by zero
    weights /= np.sum(weights, axis=1, keepdims=True)  # Normalize weights

    # Compute interpolated values
    reprojected_data_flat = np.sum(
        data_flat[idx] * weights, axis=1, dtype=float32
    )
    reprojected_data_flat=reprojected_data_flat.reshape((n_rows, n_cols))

    # Reshape to grid
    return cast(ArrayFloat32, reprojected_data_flat)
