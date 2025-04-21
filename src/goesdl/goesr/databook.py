import math

# Dataset name

dataset_name_goesr: str = "GOES-R Series"

# Spatial resolution (GRS80 ellipsoid)

GOES_EQUATORIAL_RADIUS_M = 6378137.0
GOES_INVERSE_FLATTENING = 298.2572221
GOES_EQUATORIAL_PERIMETER_M = 2.0 * math.pi * GOES_EQUATORIAL_RADIUS_M
DEG_TO_KM = GOES_EQUATORIAL_PERIMETER_M / 360000.0
PIXELS_PER_DEGREE = 55
SPATIAL_RESOLUTION_DEG = 1.0 / PIXELS_PER_DEGREE
SPATIAL_RESOLUTION_KM = SPATIAL_RESOLUTION_DEG * DEG_TO_KM

geospatial_resolution_deg = SPATIAL_RESOLUTION_DEG, SPATIAL_RESOLUTION_DEG
geospatial_resolution_km = SPATIAL_RESOLUTION_KM, SPATIAL_RESOLUTION_KM

# Dataset abstract

ppd = PIXELS_PER_DEGREE
dpc = SPATIAL_RESOLUTION_DEG
kpc = SPATIAL_RESOLUTION_KM

abstract_goesr = (
    f"This product is referred to as {dataset_name_goesr}. The "
    f"resolution of the grid is 1/{ppd}th of a degree, or {dpc:.2f} "
    f"degrees, equivalent to {kpc:.2f} km at the Equator, latitude "
    f"and longitude, yielding {ppd} pixels per degree."
)

# Long platform name

platform_origin_goesr = {f"GOES-{id}": f"G{id:0>2}" for id in range(16, 20)}

origin_platform_goesr = {
    value: key for key, value in platform_origin_goesr.items()
}

# Channel description

channel_description_goesr = {
    "C01": "Reflectance (or Scaled Radiance) for the 0.47 µm 'Blue' band",
    "C02": "Reflectance (or Scaled Radiance) for the 0.64 µm 'Red' band",
    "C03": "Reflectance (or Scaled Radiance) for the 0.86 µm 'Veggie' band",
    "C04": "Reflectance (or Scaled Radiance) for the 1.37 µm 'Cirrus' band",
    "C05": "Reflectance (or Scaled Radiance) for the 1.61 µm 'Snow/Ice' band",
    "C06": "Reflectance (or Scaled Radiance) for the 2.24 µm 'Cloud Particle Size' band",
    "C07": "Reflectance (or Scaled Radiance) for the 3.90 µm 'Shortwave Window' band",
    "C08": "Reflectance (or Scaled Radiance) for the 6.20 µm 'Upper-level water vapor' band",
    "C09": "Reflectance (or Scaled Radiance) for the 6.90 µm 'Mid-level water vapor' band",
    "C10": "Reflectance (or Scaled Radiance) for the 7.30 µm 'Lower-level water vapor' band",
    "C11": "Brightness Temperature of the 8.50 µm 'Cloud-Top Phase' channel",
    "C12": "Brightness Temperature of the 9.60 µm 'Ozone' channel",
    "C13": "Brightness Temperature of the 10.3 µm 'Clean IR Longwave Window' channel",
    "C14": "Brightness Temperature of the 11.2 µm 'IR Longwave Window' channel",
    "C15": "Brightness Temperature of the 12.3 µm 'Dirty Longwave Window' channel",
    "C16": "Brightness Temperature of the 13.3 µm 'CO2 longwave infrared' channel",
}

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

wavelength_goesr = {
    "C01": 0.47,
    "C02": 0.64,
    "C03": 0.86,
    "C04": 1.37,
    "C05": 1.61,
    "C06": 2.24,
    "C07": 3.90,
    "C08": 6.20,
    "C09": 6.90,
    "C10": 7.30,
    "C11": 8.50,
    "C12": 9.60,
    "C13": 10.3,
    "C14": 11.2,
    "C15": 12.3,
    "C16": 13.3,
}

square_igfov_at_nadir_goesr = {
    "C01": 1.0,
    "C02": 0.5,
    "C03": 1.0,
    "C04": 2.0,
    "C05": 1.0,
    "C06": 2.0,
    "C07": 2.0,
    "C08": 2.0,
    "C09": 2.0,
    "C10": 2.0,
    "C11": 2.0,
    "C12": 2.0,
    "C13": 2.0,
    "C14": 2.0,
    "C15": 2.0,
    "C16": 2.0,
}
