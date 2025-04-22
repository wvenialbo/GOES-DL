"""
GOES dataset metadata extraction.

This module provides classes to extract and represent dataset metadata
from GOES satellite netCDF data files.

Classes
-------
GOESDatasetInfo
    Represent GOES dataset metadata attributes.
"""

import math
from re import search

from netCDF4 import Dataset
from numpy import float32, int32

from ..netcdf import DatasetView, HasStrHelp, scalar
from .databook_gr import (
    GRS80_KILOMETRES_PER_DEGREE,
    channel_correspondence_goesr,
    channel_description_goesr,
    dataset_name_goesr,
    origin_platform_goesr,
    product_summary,
    scene_id_goesr,
    scene_name_goesr,
    spectral_units_goesr,
    square_igfov_at_nadir_goesr,
    wavelength_goesr,
)

NA = "not available"


class _PlatformInfo(DatasetView):

    cdm_data_type: str
    dataset_name: str
    instrument_ID: str  # NOSONAR
    instrument_type: str
    platform_ID: str
    orbital_slot: str


class _ChannelInfo(DatasetView):

    band_id: int32 = scalar(convert=int32)
    band_wavelength: float32 = scalar()


class _SceneInfo(DatasetView):

    scene_id: str


class GOESPlatformInfo(HasStrHelp):
    """
    Class to hold dataset platform information.

    Attributes
    ----------
    channel_nr : int
        The original channel number, 0 for unsupported channels.
    instrument_id : str
        The identifier for the instrument.
    origin : str
        The platform origin (platform-id).
    scene_id : str
        The identifier for the scene.

    Properties
    ----------
    channel : str
        A human-readable channel name.
    channel_description : str
        The channel description.
    channel_id : str
        Channel ID (e.g. 'C01', 'C02', etc.).
    dataset : str
        The dataset name.
    platform : str
        The platform name (e.g. 'GOES-16', 'GOES-19', etc.)
    """

    channel_nr: int = 0
    """
    The original channel number, 0 for unsupported channels.
    """

    content_type: str

    instrument_id: str = NA
    """
    The identifier for the instrument.
    """

    instrument_type: str
    """
    The instrument type specification.
    """

    orbital_slot: str = NA

    origin: str = NA
    """
    The platform origin (platform-id).
    """

    scene_id: str = NA
    """
    The identifier for the scene.
    """

    def __init__(self, record: Dataset, channel: str = "") -> None:
        pinfo = _PlatformInfo(record)

        product_name, scene_id, channel_nr = product_summary(
            pinfo.dataset_name
        )

        if channel_nr:
            cinfo = _ChannelInfo(record)
            self.channel_nr = cinfo.band_id
        elif product_name == "MCMIP":
            if not channel:
                raise ValueError(
                    f"Product '{product_name}' requires a channel id"
                )
            if channel not in channel_correspondence_goesr:
                allowed_channels = "', '".join(
                    channel_correspondence_goesr.keys()
                )
                raise ValueError(
                    f"Invalid channel: '{channel}'; "
                    f"allowed channels are: '{allowed_channels}'"
                )
            self.channel_nr = channel_correspondence_goesr[channel]
        else:
            self.channel_nr = 0

        self.content_type = pinfo.cdm_data_type
        self.instrument_id = pinfo.instrument_ID
        self.instrument_type = pinfo.instrument_type
        self.origin = pinfo.platform_ID
        self.orbital_slot = pinfo.orbital_slot

        if scene_id:
            sinfo = _SceneInfo(record)
            if scene_id[0] != scene_id_goesr[sinfo.scene_id]:
                raise TypeError("Unexpected scene id found")
            self.scene_id = scene_id
        else:
            self.scene_id = NA

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
        return (
            channel_description_goesr[self.channel_nr]
            if self.channel_nr
            else NA
        )

    @property
    def channel_id(self) -> str:
        """
        Channel ID (e.g. 'C01', 'C02', etc.).
        """
        return f"C{self.channel_nr:0>2}" if self.channel_nr else NA

    @property
    def dataset(self) -> str:
        """
        The dataset name.
        """
        return dataset_name_goesr

    @property
    def platform(self) -> str:
        """
        The platform name (e.g. 'GOES-16', 'GOES-19', etc.).
        """
        return origin_platform_goesr[self.origin]

    @property
    def scene(self) -> str:
        """
        The scene name (e.g. 'Full Disk', etc.).
        """
        return scene_name_goesr[self.scene_id] if self.scene_id != NA else NA


class _GeospatialInfo(DatasetView):

    spatial_resolution: str


class GOESGeospatialInfo(HasStrHelp):
    """
    Class to hold dataset geospatial information.

    Attributes
    ----------
    square_fov_at_nadir : float
        Nominal square IGFOV at nadir in km.

    Properties
    ----------
    pixels_per_degree : float
        The number of pixels per degree at nadir.
    pixels_per_kilometre : float
        The number of pixels per kilometre at nadir.
    """

    square_fov_at_nadir: float = math.nan
    """
    Nominal square IGFOV at nadir in km.
    """

    def __init__(self, record: Dataset, channel: str = "") -> None:
        # Get platform information
        pinfo = GOESPlatformInfo(record, channel)

        # Get nominal square IGFOV at nadir in km
        if pinfo.channel_nr:
            self.square_fov_at_nadir = square_igfov_at_nadir_goesr[
                pinfo.channel_nr
            ]
        else:
            ginfo = _GeospatialInfo(record)
            pattern = r"(\d+\.?\d*)([km]+)"
            match = search(pattern, ginfo.spatial_resolution)
            if not match:
                raise ValueError(
                    "Unable to find spatial resolution information"
                )
            resolution, units = match.groups()
            if not match or units != "km":
                raise ValueError(
                    "Unexpected spatial resolution: "
                    f"'{ginfo.spatial_resolution}'"
                )
            self.square_fov_at_nadir = float(resolution)

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
    wavelength : float
        Central wavelength in micrometres.
    spectral_units : str
        Spectral units.
    """

    spectral_units: str = NA
    """
    Spectral units.
    """

    wavelength: float = math.nan
    """
    Central wavelength in micrometres.
    """

    def __init__(self, record: Dataset, channel: str = "") -> None:
        # Get platform information
        pinfo = GOESPlatformInfo(record, channel)

        if not pinfo.channel_nr:
            raise ValueError(
                "This product does not have radiometric information"
            )

        cinfo = _ChannelInfo(record)

        self.spectral_units = spectral_units_goesr

        self.nominal_wavelength = wavelength_goesr[pinfo.channel_nr]

        self.wavelength = float(cinfo.band_wavelength)
