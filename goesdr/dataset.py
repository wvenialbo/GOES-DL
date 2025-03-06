"""
GOES dataset metadata extraction.

This module provides classes to extract and represent dataset metadata
from GOES satellite netCDF data files.

Classes
-------
GOESDatasetInfo
    Represent GOES dataset metadata attributes.
"""

from .netcdf import DatasetView, dimension


class GOESDatasetInfo(DatasetView):
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
    platform_ID: str  # NOSONAR
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
