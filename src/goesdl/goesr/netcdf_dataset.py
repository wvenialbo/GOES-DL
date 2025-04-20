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
from typing import Any

from netCDF4 import Dataset

from ..netcdf import HasStrHelp, dimension
from .databook import (
    PIXELS_PER_DEGREE,
    abstract_goesr,
    channel_correspondence_goesr,
    channel_description_goesr,
    dataset_name_goesr,
    geospatial_resolution_deg,
    geospatial_resolution_km,
    platform_origin_goesr,
    square_igfov_at_nadir_goesr,
    wavelength_goesr,
)
from .netcdf_platform import GOESPlatformMetadata

NAN_TUPLE = math.nan, math.nan

NA = "not available"


class GOESDatasetMetadata(GOESPlatformMetadata):
    """
    Hold GOES dataset metadata information.

    Attributes
    ----------
    institution : str
        The institution responsible for the dataset.
    project : str
        The project under which the dataset was created.
    production_site : str
        The site where the dataset was produced.
    production_environment : str
        The environment where the dataset was produced.
    spatial_resolution : str
        The spatial resolution of the dataset.
    orbital_slot : str
        The orbital slot of the satellite.
    platform_ID : str
        The platform identifier of the satellite.
    instrument_type : str
        The type of instrument used to collect the data.
    scene_id : str
        The identifier for the scene.
    instrument_ID : str
        The identifier for the instrument.
    dataset_name : str
        The name of the dataset.
    title : str
        The title of the dataset.
    summary : str
        A summary of the dataset.
    keywords : str
        Keywords associated with the dataset.
    keywords_vocabulary : str
        The vocabulary used for the keywords.
    license : str
        The license under which the dataset is released.
    processing_level : str
        The processing level of the dataset.
    cdm_data_type : str
        The CDM data type of the dataset.
    date_created : str
        The date the dataset was created.
    time_coverage_start : str
        The start time of the data coverage.
    time_coverage_end : str
        The end time of the data coverage.
    timeline_id : str
        The identifier for the timeline.
    production_data_source : str
        The data source used to produce the dataset.
    y : int
        The number of rows in the dataset.
    x : int
        The number of columns in the dataset.
    """

    institution: str
    project: str
    production_site: str
    production_environment: str
    spatial_resolution: str
    orbital_slot: str
    instrument_type: str
    scene_id: str
    instrument_ID: str  # NOSONAR
    dataset_name: str
    title: str
    summary: str
    keywords: str
    keywords_vocabulary: str
    license: str
    processing_level: str
    cdm_data_type: str
    date_created: str
    time_coverage_start: str
    time_coverage_end: str
    timeline_id: str
    production_data_source: str
    y: int = dimension.size()
    x: int = dimension.size()


class GOESDatabookInfo(HasStrHelp):

    dataset: str = NA
    abstract: str = NA
    description: str = NA
    channel_id: str = NA
    channel: str = NA
    geospatial_resolution_deg: tuple[float, float] = NAN_TUPLE
    geospatial_resolution_km: tuple[float, float] = NAN_TUPLE
    pixels_per_degree: int = PIXELS_PER_DEGREE
    square_fov_at_nadir: float = math.nan
    wavelength: float = math.nan

    def __init__(self, channel: str, platform: str) -> None:
        # Validate origin parameter
        if platform not in platform_origin_goesr:
            allowed_platforms = ", ".join(platform_origin_goesr.keys())
            raise ValueError(
                f"Invalid 'platform': '{platform}'; "
                f"allowed platforms are: {allowed_platforms}"
            )

        self.dataset = dataset_name_goesr
        self.abstract = abstract_goesr

        self.description = channel_description_goesr[channel]

        self.channel_id = channel
        channel_orig = channel_correspondence_goesr[channel]
        self.channel = f"Channel {channel_orig}"

        self.geospatial_resolution_deg = geospatial_resolution_deg
        self.geospatial_resolution_km = geospatial_resolution_km

        self.square_fov_at_nadir = square_igfov_at_nadir_goesr[channel]

        self.wavelength = wavelength_goesr[channel]


class GOESDatasetInfo(GOESDatabookInfo, GOESDatasetMetadata):

    def __init__(self, record: Dataset, channel: str) -> None:
        self._validate_channel(channel)

        GOESDatasetMetadata.__init__(self, record, channel=channel)

    def __post_init__(self, record: Dataset, **kwargs: Any) -> None:
        channel: str = kwargs["channel"]

        GOESDatabookInfo.__init__(self, channel, self.platform)

    @staticmethod
    def _validate_channel(channel: str) -> None:
        # Validate field id
        if channel not in channel_correspondence_goesr:
            allowed_channels = ", ".join(channel_correspondence_goesr.keys())
            raise ValueError(
                f"Invalid 'channel': '{channel}'; "
                f"allowed channels are: {allowed_channels}"
            )
