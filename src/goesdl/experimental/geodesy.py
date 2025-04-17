import math

from pyproj import CRS, Transformer


def get_semimajor_axis(projection):
    # Get the ellipsoid semimajor axis in metres
    if projection.globe is None:
        ellipsoid = CRS("WGS84").ellipsoid
        return ellipsoid.semi_major_metre

    if projection.globe.semimajor_axis is None:
        globe = projection.globe
        ellipse_name = globe.ellipse or globe.datum
        ellipsoid = CRS(ellipse_name).ellipsoid
        return ellipsoid.semi_major_metre

    return projection.globe.semimajor_axis


def get_extent_metre(extent_deg, projection):
    # Get the ellipsoid semimajor axis in metres
    semimajor_axis = get_semimajor_axis(projection)

    # Compute the extent size in metres
    deg_to_m = math.pi * semimajor_axis / 180.0
    width_deg, height_deg = extent_deg
    width_m = width_deg * deg_to_m
    height_m = height_deg * deg_to_m

    return width_m, height_m


def get_centered_domain(extent_deg, aeqd, pc):
    width_m, height_m = get_extent_metre(extent_deg, aeqd)

    half_width_m = 0.5 * width_m
    half_height_m = 0.5 * height_m

    limits = [-half_width_m, half_width_m, -half_height_m, half_height_m]

    x_coords = [
        -half_width_m,
        -half_width_m,
        -half_width_m,
        0,
        0,
        half_width_m,
        half_width_m,
        half_width_m,
    ]
    y_coords = [
        -half_height_m,
        0,
        half_height_m,
        -half_height_m,
        half_height_m,
        -half_height_m,
        0,
        half_height_m,
    ]

    # lons_deg, lats_deg = transform(aeqd, pc, x_coords, y_coords)
    transformer = Transformer.from_crs(aeqd, pc, always_xy=True)
    lons_deg, lats_deg = transformer.transform(x_coords, y_coords)

    domain = [min(lons_deg), max(lons_deg), min(lats_deg), max(lats_deg)]

    return domain, limits
