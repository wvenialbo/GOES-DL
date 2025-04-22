import math
from re import search

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


# Platform-origin correspondence

platform_origin_goesr = {f"GOES-{id}": f"G{id:0>2}" for id in range(16, 20)}

origin_platform_goesr = {
    value: key for key, value in platform_origin_goesr.items()
}


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


# Mid-channel wavelength in µm

wavelength_goesr = {
    1: 0.47,
    2: 0.64,
    3: 0.865,
    4: 1.378,
    5: 1.61,
    6: 2.25,
    7: 3.90,
    8: 6.185,
    9: 6.95,
    10: 7.34,
    11: 8.5,
    12: 9.61,
    13: 10.35,
    14: 11.2,
    15: 12.3,
    16: 13.3,
}


# Spectral units

spectral_units_goesr = "micrometres"


# Nominal square IGFOV at nadir in km

square_igfov_at_nadir_goesr = {
    1: 1.0,
    2: 0.5,
    3: 1.0,
    4: 2.0,
    5: 1.0,
    6: 2.0,
    7: 2.0,
    8: 2.0,
    9: 2.0,
    10: 2.0,
    11: 2.0,
    12: 2.0,
    13: 2.0,
    14: 2.0,
    15: 2.0,
    16: 2.0,
}


def product_summary(dataset_name: str) -> tuple[str, str, int]:
    """
    Extract product, scene, and channel information from a dataset name.

    Parses the dataset name using regular expressions to extract the
    product, scene, and channel number.

    Parameters
    ----------
    dataset_name : str
        The name of the dataset.

    Returns
    -------
    tuple[str, str, int]
        A tuple containing the product, scene, and channel number.

    Raises
    ------
    ValueError
        If the dataset name is invalid or if there is a syntax error
        processing the channel number.
    """
    if not dataset_name.startswith("OR_ABI"):
        return "", "", 0

    product_scene_channel_pat = r"OR_ABI-L\db?-([^-]+)-M\d(C\d\d)?_G\d\d"
    product_scene_pat = r"(.+)([MFC]\d?)"

    match = search(product_scene_channel_pat, dataset_name)

    if not match:
        raise ValueError(f"Invalid dataset name: '{dataset_name}'")

    product_scene, channel = match.groups()

    match = search(product_scene_pat, product_scene)

    if not match:
        raise ValueError(f"Invalid dataset name: '{dataset_name}'")

    product_id, scene_id = match.groups()

    channel_nr = 0
    if channel:
        try:
            channel_nr = int(channel[1:])
        except ValueError as error:
            raise ValueError(
                "Syntax error processing " f"channel number '{channel}'"
            ) from error

    return product_id, scene_id, channel_nr
