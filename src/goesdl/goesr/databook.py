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
    "CH1": "Reflectance (or Scaled Radiance) for the 0.47 µm 'Blue' band",
    "CH2": "Reflectance (or Scaled Radiance) for the 0.64 µm 'Red' band",
    "CH3": "Reflectance (or Scaled Radiance) for the 0.86 µm 'Veggie' band",
    "CH4": "Reflectance (or Scaled Radiance) for the 1.37 µm 'Cirrus' band",
    "CH5": "Reflectance (or Scaled Radiance) for the 1.61 µm 'Snow/Ice' band",
    "CH6": "Reflectance (or Scaled Radiance) for the 2.24 µm 'Cloud Particle Size' band",
    "CH7": "Reflectance (or Scaled Radiance) for the 3.90 µm 'Shortwave Window' band",
    "CH8": "Reflectance (or Scaled Radiance) for the 6.20 µm 'Upper-level water vapor' band",
    "CH9": "Reflectance (or Scaled Radiance) for the 6.90 µm 'Mid-level water vapor' band",
    "CH10": "Reflectance (or Scaled Radiance) for the 7.30 µm 'Lower-level water vapor' band",
    "CH11": "Brightness Temperature of the 8.50 µm 'Cloud-Top Phase' channel",
    "CH12": "Brightness Temperature of the 9.60 µm 'Ozone' channel",
    "CH13": "Brightness Temperature of the 10.3 µm 'Clean IR Longwave Window' channel",
    "CH14": "Brightness Temperature of the 11.2 µm 'IR Longwave Window' channel",
    "CH15": "Brightness Temperature of the 12.3 µm 'Dirty Longwave Window' channel",
    "CH16": "Brightness Temperature of the 13.3 µm 'CO2 longwave infrared' channel",
}

channel_correspondence_goesr = {
    "CH1": 1,
    "CH2": 2,
    "CH3": 3,
    "CH4": 4,
    "CH5": 5,
    "CH6": 6,
    "CH7": 7,
    "CH8": 8,
    "CH9": 9,
    "CH10": 10,
    "CH11": 11,
    "CH12": 12,
    "CH13": 13,
    "CH14": 14,
    "CH15": 15,
    "CH16": 16,
}

wavelength_goesr = {
    "CH1": 0.47,
    "CH2": 0.64,
    "CH3": 0.86,
    "CH4": 1.37,
    "CH5": 1.61,
    "CH6": 2.24,
    "CH7": 3.90,
    "CH8": 6.20,
    "CH9": 6.90,
    "CH10": 7.30,
    "CH11": 8.50,
    "CH12": 9.60,
    "CH13": 10.3,
    "CH14": 11.2,
    "CH15": 12.3,
    "CH16": 13.3,
}

square_igfov_at_nadir_goesr = {
    "CH1": 1.0,
    "CH2": 0.5,
    "CH3": 1.0,
    "CH4": 2.0,
    "CH5": 1.0,
    "CH6": 2.0,
    "CH7": 2.0,
    "CH8": 2.0,
    "CH9": 2.0,
    "CH10": 2.0,
    "CH11": 2.0,
    "CH12": 2.0,
    "CH13": 2.0,
    "CH14": 2.0,
    "CH15": 2.0,
    "CH16": 2.0,
}
