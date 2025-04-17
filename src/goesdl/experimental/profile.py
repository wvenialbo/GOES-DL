import numpy as np


def create_radial_grid(shape):
    # Create a grid of pixel indices
    y_coords, x_coords = np.indices((shape), dtype=np.float64)

    # Get the grid extent in cells
    y_extent, x_extent = shape

    # Compute the grid center coordinates
    y_center, x_center = (y_extent - 1) / 2, (x_extent - 1) / 2

    # Compute the distance of each cell to the center
    return np.sqrt((x_coords - x_center) ** 2 + (y_coords - y_center) ** 2)


def radial_profile(data):
    # Compute the distance grid (of each cell to the grid center)
    r_grid = create_radial_grid(data.shape)
    radii = np.round(r_grid).astype(np.int32)

    # Calculate the azimuthal integral for each radii
    azimuthal_integral = np.bincount(radii.ravel(), data.ravel()).astype(
        np.float32
    )

    # Calculate the line integral for each radii
    line_integral = np.bincount(radii.ravel()).astype(np.float32)

    # Mask zero values
    line_integral[line_integral == 0] = np.nan

    # Calulate the azimuthal average for each radii, i.e. for each
    # radii divide the azimuthal integral by the line integral
    profile = azimuthal_integral / line_integral

    # Compute the region radius
    radius = min(data.shape[0] // 2, data.shape[1] // 2)

    return profile, radius


def azimuthal_average_transform(profile, radius, shading="nearest"):
    # Compute the profile extent
    n_profile = len(profile)

    # Compute the side for the output data matrix
    side = 2 * radius

    # Compute the distance grid (of each cell to the grid center)
    r_grid = create_radial_grid((side, side))

    # Compute the azimuthal average transform
    if shading == "nearest":
        # Convert radii to indices
        radii = np.round(r_grid).astype(np.int32)

        # Clip radii to profile extent
        radii = np.clip(radii, 0, n_profile - 1)

        # Transform by lookup table
        return profile[radii]

    if shading == "interp":
        radii = r_grid
        profile_radii = np.arange(n_profile, dtype=np.float32)

        return np.interp(radii, profile_radii, profile)

    raise ValueError("'shading' must be 'interp' oo 'nearest' (default)")


def azimuthal_average_factory(radius, shading="nearest"):
    # Compute the side for the output data matrix
    side = 2 * radius

    # Compute the distance grid (of each cell to the grid center)
    r_grid = create_radial_grid((side, side))

    # Compute the azimuthal average transform
    if shading == "nearest":
        # Convert radii to indices
        radii_nearest = np.round(r_grid).astype(np.int32)

        def transform_nearest(profile):
            # Compute the profile extent
            n_profile = len(profile)

            # Clip radii to profile extent
            radii = np.clip(radii_nearest, 0, n_profile - 1)

            return profile[radii]

        return transform_nearest

    if shading == "interp":
        # Use radii as is
        radii_interp = r_grid

        def transform_interp(profile):
            # Compute the profile extent
            n_profile = len(profile)

            # Create key values
            profile_radii = np.arange(n_profile, dtype=np.float32)

            return np.interp(radii_interp, profile_radii, profile)

        return transform_interp

    raise ValueError("'shading' must be 'interp' or 'nearest' (default)")
