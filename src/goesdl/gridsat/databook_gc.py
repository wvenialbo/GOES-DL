import math

# Dataset name

dataset_name_gc: str = "GridSat"


# Spatial resolution (GRS80 ellipsoid)

GRS80_INVERSE_FLATTENING = 298.2572221
GRS80_SEMI_MAJOR_AXIS = 6378137.0
GRS80_SEMI_MINOR_AXIS = 6356752.31414

GRS80_EQUATORIAL_PERIMETER_M = 2.0 * math.pi * GRS80_SEMI_MAJOR_AXIS
GRS80_KILOMETRES_PER_DEGREE = GRS80_EQUATORIAL_PERIMETER_M / 360000.0


# Dataset abstract


def get_abstract_gridsat_gc(kilometres_per_pixel: float) -> str:
    """
    The abstract for the GridSat-GOES dataset.

    Parameters
    ----------
    kilometres_per_pixel : float
        The number of kilometres per pixel.

    Returns
    -------
    str
        The abstract for the GridSat-GOES dataset.
    """

    pixels_per_kilometre = 1.0 / kilometres_per_pixel
    pixels_per_degree = pixels_per_kilometre * GRS80_KILOMETRES_PER_DEGREE
    degrees_per_pixel = round(1.0 / pixels_per_degree, 2)
    pixels_per_degree = round(pixels_per_degree)

    return (
        f"This product is referred to as {dataset_name_gc}. "
        f"The resolution of the grid is 1/{pixels_per_degree}th of a degree, "
        f"or {degrees_per_pixel:.2f} degrees, equivalent "
        f"to {kilometres_per_pixel:.2f} km at the Equator, latitude "
        f"and longitude, yielding {pixels_per_degree} pixels per degree."
    )


# Platform-origin correspondence

platform_origin_gridsat_gc = {
    f"GOES-{id}": f"G{id:0>2}" for id in range(8, 16)
}


# Scene identifiers

scene_id_gc: dict[str, str] = {
    "GOES": "F",
    "CONUS": "C",
}

scene_name_gc: dict[str, str] = {
    "F": "Full Disk",
    "C": "CONUS (Contiguous United States)",
}


# Channel description

channel_description_gc = {
    "ch1": "Reflectance (or Scaled Radiance) for the 0.6 µm band",
    "ch2": "Brightness Temperature of the 3.9 µm channel",
    "ch3": "Brightness Temperature of the 6.7 µm channel",
    "ch4": "Brightness Temperature of the 10.7 µm channel",
    "ch5": "Brightness Temperature of the 12.0 µm channel",
    "ch6": "Brightness Temperature of the 13.4 µm channel",
}


ch1_standard_name = (
    "toa_lambertian_equivalent_albedo_"
    "multiplied_by_cosine_solar_zenith_angle"
)

# GridSat-GOES channel to actual channel correspondence

_channel_correspondence_il = {
    "ch1": 1,
    "ch2": 2,
    "ch3": 3,
    "ch4": 4,
    "ch5": 5,
    "ch6": 0,
}

_channel_correspondence_mp = {
    "ch1": 1,
    "ch2": 2,
    "ch3": 5,
    "ch4": 4,
    "ch5": 0,
    "ch6": 3,
}

channel_correspondence_gc = {
    "G08": _channel_correspondence_il,
    "G09": _channel_correspondence_il,
    "G10": _channel_correspondence_il,
    "G11": _channel_correspondence_il,
    "G12": _channel_correspondence_mp,
    "G13": _channel_correspondence_mp,
    "G14": _channel_correspondence_mp,
    "G15": _channel_correspondence_mp,
}


# Wavelength range lower bound in µm

_wavelength_range_lower_bound_il = {
    1: 0.55,
    2: 3.80,
    3: 6.50,
    4: 10.20,
    5: 11.50,
}

_wavelength_range_lower_bound_m = {
    1: 0.55,
    2: 3.80,
    3: 13.00,
    4: 10.20,
    5: 5.80,
}

_wavelength_range_lower_bound_np = {
    1: 0.52,
    2: 3.73,
    3: 13.00,
    4: 10.20,
    5: 5.80,
}

wavelength_range_lower_bound_gc = {
    "G08": _wavelength_range_lower_bound_il,
    "G09": _wavelength_range_lower_bound_il,
    "G10": _wavelength_range_lower_bound_il,
    "G11": _wavelength_range_lower_bound_il,
    "G12": _wavelength_range_lower_bound_m,
    "G13": _wavelength_range_lower_bound_np,
    "G14": _wavelength_range_lower_bound_np,
    "G15": _wavelength_range_lower_bound_np,
}


# Wavelength range upper bound in µm

_wavelength_range_upper_bound_il = {
    1: 0.75,
    2: 4.00,
    3: 7.00,
    4: 11.20,
    5: 12.50,
}

_wavelength_range_upper_bound_m = {
    1: 0.75,
    2: 4.00,
    3: 13.70,
    4: 11.20,
    5: 7.30,
}

_wavelength_range_upper_bound_np = {
    1: 0.71,
    2: 4.07,
    3: 13.70,
    4: 11.20,
    5: 7.30,
}

wavelength_range_upper_bound_gc = {
    "G08": _wavelength_range_upper_bound_il,
    "G09": _wavelength_range_upper_bound_il,
    "G10": _wavelength_range_upper_bound_il,
    "G11": _wavelength_range_upper_bound_il,
    "G12": _wavelength_range_upper_bound_m,
    "G13": _wavelength_range_upper_bound_np,
    "G14": _wavelength_range_upper_bound_np,
    "G15": _wavelength_range_upper_bound_np,
}


# Spectral units

spectral_units_gc = "micrometres"


# Radiometric resolution

radiometric_resolution_gc = 10


# Measurement range lower bound in % albedo (1) / K (2-5)

_measurement_range_lower_bound_im = {
    1: 1.6,
    2: 4.0,
    3: 4.0,
    4: 4.0,
    5: 4.0,
}

_measurement_range_lower_bound_np = {
    1: 0.0,
    2: 4.0,
    3: 4.0,
    4: 4.0,
    5: 4.0,
}

measurement_range_lower_bound_gc = {
    "G08": _measurement_range_lower_bound_im,
    "G09": _measurement_range_lower_bound_im,
    "G10": _measurement_range_lower_bound_im,
    "G11": _measurement_range_lower_bound_im,
    "G12": _measurement_range_lower_bound_im,
    "G13": _measurement_range_lower_bound_np,
    "G14": _measurement_range_lower_bound_np,
    "G15": _measurement_range_lower_bound_np,
}


# Measurement range upper bound in % albedo (1) / K (2-5)

_measurement_range_upper_bound_ik = {
    1: 100.0,
    2: 320.0,
    3: 320.0,
    4: 320.0,
    5: 320.0,
}

_measurement_range_upper_bound_lp = {
    1: 100.0,
    2: 335.0,
    3: 320.0,
    4: 320.0,
    5: 320.0,
}

measurement_range_upper_bound_gc = {
    "G08": _measurement_range_upper_bound_ik,
    "G09": _measurement_range_upper_bound_ik,
    "G10": _measurement_range_upper_bound_ik,
    "G11": _measurement_range_upper_bound_lp,
    "G12": _measurement_range_upper_bound_lp,
    "G13": _measurement_range_upper_bound_lp,
    "G14": _measurement_range_upper_bound_lp,
    "G15": _measurement_range_upper_bound_lp,
}


# Measurement units

ALBEDO = "% albedo"
KELVIN = "Kelvin"

measurement_units_gc = {
    1: ALBEDO,
    2: KELVIN,
    3: KELVIN,
    4: KELVIN,
    5: KELVIN,
}


# Nominal square IGFOV at nadir in km

_square_igfov_at_nadir_in = {
    1: 1.0,
    2: 4.0,
    3: 8.0,
    4: 4.0,
    5: 4.0,
}

_square_igfov_at_nadir_op = {
    1: 1.0,
    2: 4.0,
    3: 4.0,
    4: 4.0,
    5: 4.0,
}

square_igfov_at_nadir_gc = {
    "G08": _square_igfov_at_nadir_in,
    "G09": _square_igfov_at_nadir_in,
    "G10": _square_igfov_at_nadir_in,
    "G11": _square_igfov_at_nadir_in,
    "G12": _square_igfov_at_nadir_in,
    "G13": _square_igfov_at_nadir_in,
    "G14": _square_igfov_at_nadir_op,
    "G15": _square_igfov_at_nadir_op,
}
