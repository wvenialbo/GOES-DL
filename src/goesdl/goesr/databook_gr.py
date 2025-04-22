import math

# Dataset name

dataset_name_goesr: str = "GOES-R Series"


# Spatial resolution (GRS80 ellipsoid)

GRS80_INVERSE_FLATTENING = 298.257222096
GRS80_SEMI_MAJOR_AXIS = 6378137.0
GRS80_SEMI_MINOR_AXIS = 6356752.31414

GRS80_EQUATORIAL_PERIMETER_M = 2.0 * math.pi * GRS80_SEMI_MAJOR_AXIS
GRS80_KILOMETRES_PER_DEGREE = GRS80_EQUATORIAL_PERIMETER_M / 360000.0


# Dataset abstract


def get_abstract_goesr(kilometres_per_pixel: float) -> str:
    """
    The abstract for the GOES-R Series dataset.

    Parameters
    ----------
    kilometres_per_pixel : float
        The number of kilometres per pixel.

    Returns
    -------
    str
        The abstract for the GOES-R Series dataset.
    """

    pixels_per_kilometre = 1.0 / kilometres_per_pixel
    pixels_per_degree = pixels_per_kilometre * GRS80_KILOMETRES_PER_DEGREE
    degrees_per_pixel = round(1.0 / pixels_per_degree, 2)
    pixels_per_degree = round(pixels_per_degree)

    return (
        f"This product is referred to as {dataset_name_goesr}. "
        f"The resolution of the grid is 1/{pixels_per_degree}th of a degree, "
        f"or {degrees_per_pixel:.2f} degrees, equivalent "
        f"to {kilometres_per_pixel:.2f} km at the Equator, latitude "
        f"and longitude, yielding {pixels_per_degree} pixels per degree."
    )


# Origin-platform correspondence

origin_platform_goesr = {f"G{id:0>2}": f"GOES-{id}" for id in range(16, 20)}


# Scene identifiers

scene_id_goesr: dict[str, str] = {
    "Full Disk": "F",
    "CONUS": "C",
    "Mesoscale": "M",
}

scene_name_goesr: dict[str, str] = {
    "F": "Full Disk",
    "C": "CONUS (Continental United States)",
    "M": "Mesoscale",
    "M1": "Mesoscale (Domain 1)",
    "M2": "Mesoscale (Domain 2)",
}


# Channel description

channel_description_goesr = {
    1: "Reflectance (or Scaled Radiance) for the 0.47 µm 'Blue' band",
    2: "Reflectance (or Scaled Radiance) for the 0.64 µm 'Red' band",
    3: "Reflectance (or Scaled Radiance) for the 0.86 µm 'Veggie' band",
    4: "Reflectance (or Scaled Radiance) for the 1.37 µm 'Cirrus' band",
    5: "Reflectance (or Scaled Radiance) for the 1.61 µm 'Snow/Ice' band",
    6: "Reflectance (or Scaled Radiance) for the 2.24 µm 'Cloud Particle Size' band",
    7: "Brightness Temperature of the 3.90 µm 'Shortwave Window' band",
    8: "Brightness Temperature of the 6.20 µm 'Upper-level water vapor' band",
    9: "Brightness Temperature of the 6.90 µm 'Mid-level water vapor' band",
    10: "Brightness Temperature of the 7.30 µm 'Lower-level water vapor' band",
    11: "Brightness Temperature of the 8.50 µm 'Cloud-Top Phase' channel",
    12: "Brightness Temperature of the 9.60 µm 'Ozone' channel",
    13: "Brightness Temperature of the 10.3 µm 'Clean IR Longwave Window' channel",
    14: "Brightness Temperature of the 11.2 µm 'IR Longwave Window' channel",
    15: "Brightness Temperature of the 12.3 µm 'Dirty Longwave Window' channel",
    16: "Brightness Temperature of the 13.3 µm 'CO2 longwave infrared' channel",
}


# GridSat-GOES channel to actual channel correspondence

channel_correspondence_goesr = {
    "C01": 1,
    "C02": 2,
    "C03": 3,
    "C04": 4,
    "C05": 5,
    "C06": 6,
    "C07": 7,
    "C08": 8,
    "C09": 9,
    "C10": 10,
    "C11": 11,
    "C12": 12,
    "C13": 13,
    "C14": 14,
    "C15": 15,
    "C16": 16,
}


# Spectral units

spectral_units_goesr = "micrometres"
