import math
import re
from re import search

from netCDF4 import Dataset
from numpy import float32

from ..netcdf import DatasetView, HasStrHelp, attribute
from .constants import NA
from .databook_gc import (
    GRS80_KILOMETRES_PER_DEGREE,
    channel_correspondence_gc,
    channel_description_gc,
    dataset_name_gc,
    measurement_range_lower_bound_gc,
    measurement_range_upper_bound_gc,
    measurement_units_gc,
    platform_origin_gridsat_gc,
    scene_id_gc,
    scene_name_gc,
    spectral_units_gc,
    square_igfov_at_nadir_gc,
    wavelength_range_lower_bound_gc,
    wavelength_range_upper_bound_gc,
)

# Platform information


class _PlatformInfo(DatasetView):

    id: str
    instrument: str
    platform: str


class GSPlatformInfo(HasStrHelp):
    """
    Class to hold dataset platform information.

    Attributes
    ----------
    channel_id : str
        Channel ID (e.g. 'ch1', 'ch2', etc.).
    platform_domain : str
        Platform domain chain.

    Properties
    ----------
    channel : str
        A human-readable channel name.
    channel_description : str
        The channel description.
    channel_nr : int
        The original channel number, 0 for unsupported channels.
    dataset : str
        The dataset name.
    origin : str
        The platform origin (platform-id).
    platform : str
        The platform name (e.g. 'GOES-12', 'GOES-15', etc.).
    """

    channel_id: str = NA
    """
    Channel ID (e.g. 'ch1', 'ch2', etc.).
    """

    instrument_specs: str = NA
    """
    Instrument specification.
    """

    platform_specs: str
    """
    Platform domain specification.
    """

    scene_id: str = NA
    """
    The identifier for the scene.
    """

    def __init__(
        self,
        record: Dataset,
        channel: str,
        raise_if_not_available: bool = True,
    ) -> None:
        # Get platform information
        pinfo = _PlatformInfo(record)

        self.channel_id = channel

        self.instrument_specs = pinfo.instrument

        self.platform_specs = pinfo.platform

        if match := re.match(r"^GridSat-([A-Z]+)\.", pinfo.id):
            self.scene_id = scene_id_gc[match[1]]
        else:
            self.scene_id = NA

        # Validate platform parameter
        if self.platform not in platform_origin_gridsat_gc:
            allowed_platforms = "', '".join(platform_origin_gridsat_gc.keys())
            raise ValueError(
                f"Invalid platform: '{self.platform}'; "
                f"allowed platforms are: '{allowed_platforms}'"
            )

        # Validate channel id
        channel_correspondence = channel_correspondence_gc[self.origin]
        if self.channel_id not in channel_correspondence:
            allowed_channels = "', '".join(channel_correspondence.keys())
            raise ValueError(
                f"Invalid channel: '{channel}'; "
                f"allowed channels are: '{allowed_channels}'"
            )

        if self.channel_nr == 0 and raise_if_not_available:
            raise ValueError(
                f"{self.dataset} channel '{self.channel_id}' "
                f"is not available for origin '{self.origin}'"
            )

    @property
    def channel(self) -> str:
        """
        A human-readable channel name.
        """
        return f"Channel {self.channel_nr}" if self.channel_nr else NA

    @property
    def channel_description(self) -> str:
        """
        The channel description.
        """
        return channel_description_gc[self.channel_id]

    @property
    def channel_nr(self) -> int:
        """
        The original channel number, 0 for unsupported channels.
        """
        return channel_correspondence_gc[self.origin][self.channel_id]

    @property
    def dataset(self) -> str:
        """
        The dataset name.
        """
        return dataset_name_gc

    @property
    def origin(self) -> str:
        """
        The platform origin (platform-id).
        """
        return platform_origin_gridsat_gc[self.platform]

    @property
    def platform(self) -> str:
        """
        The platform name (e.g. 'GOES-12', 'GOES-15', etc.).
        """
        return (
            match[0]
            if (match := search(r"GOES-\d{1,2}", self.platform_specs))
            else NA
        )

    @property
    def scene(self) -> str:
        """
        The scene name (e.g. 'Full Disk', etc.).
        """
        return scene_name_gc[self.scene_id]


class _GeospatialInfo(DatasetView):

    geospatial_vertical_min: str
    geospatial_vertical_max: str

    geospatial_lat_min: float32
    geospatial_lat_max: float32
    geospatial_lat_units: str
    geospatial_lat_resolution: float32

    geospatial_lon_min: float32
    geospatial_lon_max: float32
    geospatial_lon_units: str
    geospatial_lon_resolution: float32


class GSGeospatialInfo(HasStrHelp):
    """
    Class to hold dataset geospatial information.

    Attributes
    ----------
    square_fov_at_nadir : float
        Nominal square IGFOV at nadir in km.
    vertical_range : tuple[float, float]
        Vertical range in metres.
    vertical_units : str
        Vertical units.
    latitude_range : tuple[float, float]
        Latitude range in degrees north.
    latitude_units : str
        Latitude units.
    latitude_resolution : float
        Latitude resolution in degrees.
    longitude_range : tuple[float, float]
        Longitude range in degrees east.
    longitude_units : str
        Longitude units.
    longitude_resolution : float
        Longitude resolution in degrees.

    Properties
    ----------
    degrees_per_pixel : float
        The geospatial resolution in degrees per pixel at nadir.
    kilometres_per_pixel : float
        The geospatial resolution in kilometres per pixel at nadir.
    pixels_per_degree : float
        The number of pixels per degree at nadir.
    pixels_per_kilometre : float
        The number of pixels per kilometre at nadir.
    """

    square_fov_at_nadir: float = math.nan
    """
    Nominal square IGFOV at nadir in km.
    """

    vertical_range: tuple[float, float] = math.nan, math.nan
    """
    Vertical range in metres.
    """

    vertical_units: str = NA
    """
    Vertical units.
    """

    latitude_range: tuple[float, float] = math.nan, math.nan
    """
    Latitude range in degrees north.
    """

    latitude_resolution: float = math.nan
    """
    Latitude resolution in degrees.
    """

    latitude_units: str = NA
    """
    Latitude units.
    """

    longitude_range: tuple[float, float] = math.nan, math.nan
    """
    Longitude range in degrees east.
    """

    longitude_units: str = NA
    """
    Longitude units.
    """

    longitude_resolution: float = math.nan
    """
    Longitude resolution in degrees.
    """

    def __init__(self, record: Dataset, channel: str) -> None:
        # Get platform information
        pinfo = GSPlatformInfo(record, channel)

        # Get nominal square IGFOV at nadir in km
        self.square_fov_at_nadir = square_igfov_at_nadir_gc[pinfo.origin][
            pinfo.channel_nr
        ]

        ginfo = _GeospatialInfo(record)

        vert_min = ginfo.geospatial_vertical_min.split()[0]
        vert_max = ginfo.geospatial_vertical_max.split()[0]
        vert_units = ginfo.geospatial_vertical_min.split()[1]

        self.vertical_range = float(vert_min.strip()), float(vert_max.strip())
        self.vertical_units = vert_units.strip()

        lat_min = ginfo.geospatial_lat_min
        lat_max = ginfo.geospatial_lat_max
        lat_units = ginfo.geospatial_lat_units

        self.latitude_range = float(lat_min), float(lat_max)
        self.latitude_units = lat_units
        self.latitude_resolution = float(ginfo.geospatial_lat_resolution)

        lon_min = ginfo.geospatial_lon_min
        lon_max = ginfo.geospatial_lon_max
        lon_units = ginfo.geospatial_lon_units

        self.longitude_range = float(lon_min), float(lon_max)
        self.longitude_units = lon_units
        self.longitude_resolution = float(ginfo.geospatial_lon_resolution)

    @property
    def degrees_per_pixel(self) -> float:
        """
        The geospatial resolution in degrees per pixel at nadir.
        """
        return round(1.0 / self.pixels_per_degree, 2)

    @property
    def kilometres_per_pixel(self) -> float:
        """
        The geospatial resolution in kilometres per pixel at nadir.
        """
        return self.square_fov_at_nadir

    @property
    def pixels_per_degree(self) -> float:
        """
        The number of pixels per kilometre at nadir.
        """
        return round(self.pixels_per_kilometre * GRS80_KILOMETRES_PER_DEGREE)

    @property
    def pixels_per_kilometre(self) -> float:
        """
        The number of pixels per kilometre at nadir.
        """
        return round(1.0 / self.kilometres_per_pixel, 2)


class GSRadiometricInfo(HasStrHelp):
    """
    Class to hold dataset radiometric information.

    Attributes
    ----------
    measurement_range : tuple[float, float]
        Measurement range in the original units.
    measurement_units : str
        Measurement units.
    spectral_range : tuple[float, float]
        Spectral range in micrometres.

    Properties
    ----------
    wavelength : float
        Central wavelength in micrometres.
    spectral_units : str
        Spectral units.
    """

    measurement_range: tuple[float, float] = math.nan, math.nan
    """
    Measurement range in the original units.
    """

    measurement_units: str = NA
    """
    Measurement units.
    """

    spectral_range: tuple[float, float] = math.nan, math.nan
    """
    Spectral range in micrometres.
    """

    def __init__(self, record: Dataset, channel: str) -> None:
        # Get platform information
        pinfo = GSPlatformInfo(record, channel)

        origin = pinfo.origin
        channel_nr = pinfo.channel_nr

        # Get measurement range in the original units
        measurement_lo = measurement_range_lower_bound_gc[origin][channel_nr]
        measurement_up = measurement_range_upper_bound_gc[origin][channel_nr]

        self.measurement_range = measurement_lo, measurement_up

        # Get measurement units
        self.measurement_units = measurement_units_gc[channel_nr]

        # Get spectral range in micrometres
        wavelength_lo = wavelength_range_lower_bound_gc[origin][channel_nr]
        wavelength_up = wavelength_range_upper_bound_gc[origin][channel_nr]

        self.spectral_range = wavelength_lo, wavelength_up

    @property
    def spectral_units(self) -> str:
        """
        Spectral units.
        """
        return spectral_units_gc

    @property
    def wavelength(self) -> float:
        """
        Central wavelength in micrometres.
        """
        return 0.5 * (self.spectral_range[0] + self.spectral_range[1])


class _DatasetInfo(DatasetView):
    """
    Class to hold dataset information.
    """

    id: str
    title: str
    project: str
    institution: str
    summary: str
    comment: str
    product_version: str
    processing_level: str
    license: str

    conventions: str = attribute("Conventions")
    keywords: str

    date_created: str
    date_modified: str

    time_coverage_start: str
    time_coverage_end: str

    platform_vocabulary: str
    sensor_vocabulary: str
    keywords_vocabulary: str
    standard_name_vocabulary: str

    naming_authority: str
    metadata_link: str
    ncei_template_version: str

    history: str
