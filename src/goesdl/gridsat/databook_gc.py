import math

# Dataset name

dataset_name_gridsat_gc: str = "GridSat-GOES"

# Spatial resolution (GRS80 ellipsoid)

GRS80_EQUATORIAL_RADIUS_M = 6378137.0
GRS80_INVERSE_FLATTENING = 298.257223563
GRS80_EQUATORIAL_PERIMETER_M = 2.0 * math.pi * GRS80_EQUATORIAL_RADIUS_M
DEG_TO_KM = GRS80_EQUATORIAL_PERIMETER_M / 360000.0
PIXELS_PER_DEGREE = 25
SPATIAL_RESOLUTION_DEG = 1.0 / PIXELS_PER_DEGREE
SPATIAL_RESOLUTION_KM = SPATIAL_RESOLUTION_DEG * DEG_TO_KM

geospatial_resolution_deg = SPATIAL_RESOLUTION_DEG, SPATIAL_RESOLUTION_DEG
geospatial_resolution_km = SPATIAL_RESOLUTION_KM, SPATIAL_RESOLUTION_KM

# Dataset abstract

ppd = PIXELS_PER_DEGREE
dpc = SPATIAL_RESOLUTION_DEG
kpc = SPATIAL_RESOLUTION_KM

abstract_gridsat_gc = (
    f"This product is referred to as {dataset_name_gridsat_gc}. The "
    f"resolution of the grid is 1/{ppd}th of a degree, or {dpc:.2f} "
    f"degrees, equivalent to {kpc:.2f} km at the Equator, latitude "
    f"and longitude, yielding {ppd} pixels per degree."
)

# Long platform name

platform_origin_gridsat_gc = {
    f"GOES-{id}": f"G{id:0>2}" for id in range(8, 16)
}

origin_platform_gridsat_gc = {
    value: key for key, value in platform_origin_gridsat_gc.items()
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

# GridSat-GOES channel to actual channel correspondence

channel_correspondence_il = {
    "ch1": 1,
    "ch2": 2,
    "ch3": 3,
    "ch4": 4,
    "ch5": 5,
    "ch6": 0,
}

channel_correspondence_mp = {
    "ch1": 1,
    "ch2": 2,
    "ch3": 5,
    "ch4": 4,
    "ch5": 0,
    "ch6": 3,
}

channel_correspondence = {
    "G08": channel_correspondence_il,
    "G09": channel_correspondence_il,
    "G10": channel_correspondence_il,
    "G11": channel_correspondence_il,
    "G12": channel_correspondence_mp,
    "G13": channel_correspondence_mp,
    "G14": channel_correspondence_mp,
    "G15": channel_correspondence_mp,
}

# Wavelength range lower bound in µm

wavelength_range_lower_bound_il = {
    1: 0.55,
    2: 3.80,
    3: 6.50,
    4: 10.20,
    5: 11.50,
}

wavelength_range_lower_bound_m = {
    1: 0.55,
    2: 3.80,
    3: 13.00,
    4: 10.20,
    5: 5.80,
}

wavelength_range_lower_bound_np = {
    1: 0.52,
    2: 3.73,
    3: 13.00,
    4: 10.20,
    5: 5.80,
}

wavelength_range_lower_bound = {
    "G08": wavelength_range_lower_bound_il,
    "G09": wavelength_range_lower_bound_il,
    "G10": wavelength_range_lower_bound_il,
    "G11": wavelength_range_lower_bound_il,
    "G12": wavelength_range_lower_bound_m,
    "G13": wavelength_range_lower_bound_np,
    "G14": wavelength_range_lower_bound_np,
    "G15": wavelength_range_lower_bound_np,
}

# Wavelength upper bound in µm

wavelength_range_upper_bound_il = {
    1: 0.75,
    2: 4.00,
    3: 7.00,
    4: 11.20,
    5: 12.50,
}

wavelength_range_upper_bound_m = {
    1: 0.75,
    2: 4.00,
    3: 13.70,
    4: 11.20,
    5: 7.30,
}

wavelength_range_upper_bound_np = {
    1: 0.71,
    2: 4.07,
    3: 13.70,
    4: 11.20,
    5: 7.30,
}

wavelength_range_upper_bound = {
    "G08": wavelength_range_upper_bound_il,
    "G09": wavelength_range_upper_bound_il,
    "G10": wavelength_range_upper_bound_il,
    "G11": wavelength_range_upper_bound_il,
    "G12": wavelength_range_upper_bound_m,
    "G13": wavelength_range_upper_bound_np,
    "G14": wavelength_range_upper_bound_np,
    "G15": wavelength_range_upper_bound_np,
}

# Measurement range lower bound in % albedo (1) / K (2-5)

measurement_range_lower_bound_im = {
    1: 1.6,
    2: 4.0,
    3: 4.0,
    4: 4.0,
    5: 4.0,
}

measurement_range_lower_bound_np = {
    1: 0.0,
    2: 4.0,
    3: 4.0,
    4: 4.0,
    5: 4.0,
}

measurement_range_lower_bound = {
    "G08": measurement_range_lower_bound_im,
    "G09": measurement_range_lower_bound_im,
    "G10": measurement_range_lower_bound_im,
    "G11": measurement_range_lower_bound_im,
    "G12": measurement_range_lower_bound_im,
    "G13": measurement_range_lower_bound_np,
    "G14": measurement_range_lower_bound_np,
    "G15": measurement_range_lower_bound_np,
}

# Measurement range upper bound in % albedo (1) / K (2-5)

measurement_range_upper_bound_ik = {
    1: 100.0,
    2: 320.0,
    3: 320.0,
    4: 320.0,
    5: 320.0,
}

measurement_range_upper_bound_lp = {
    1: 100.0,
    2: 335.0,
    3: 320.0,
    4: 320.0,
    5: 320.0,
}

measurement_range_upper_bound = {
    "G08": measurement_range_upper_bound_ik,
    "G09": measurement_range_upper_bound_ik,
    "G10": measurement_range_upper_bound_ik,
    "G11": measurement_range_upper_bound_lp,
    "G12": measurement_range_upper_bound_lp,
    "G13": measurement_range_upper_bound_lp,
    "G14": measurement_range_upper_bound_lp,
    "G15": measurement_range_upper_bound_lp,
}

# Measurement units

ALBEDO = "% albedo"
KELVIN = "Kelvin"

measurement_units = {
    1: ALBEDO,
    2: KELVIN,
    3: KELVIN,
    4: KELVIN,
    5: KELVIN,
}

# Nominal square IGFOV at nadir in km

square_igfov_at_nadir_in = {
    1: 1.0,
    2: 4.0,
    3: 8.0,
    4: 4.0,
    5: 4.0,
}

square_igfov_at_nadir_op = {
    1: 1.0,
    2: 4.0,
    3: 4.0,
    4: 4.0,
    5: 4.0,
}

square_igfov_at_nadir = {
    "G08": square_igfov_at_nadir_in,
    "G09": square_igfov_at_nadir_in,
    "G10": square_igfov_at_nadir_in,
    "G11": square_igfov_at_nadir_in,
    "G12": square_igfov_at_nadir_in,
    "G13": square_igfov_at_nadir_in,
    "G14": square_igfov_at_nadir_op,
    "G15": square_igfov_at_nadir_op,
}
