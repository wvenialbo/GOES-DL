import math
from re import search
from typing import Any

from netCDF4 import Dataset  # pylint: disable=no-name-in-module

from ..netcdf import DatasetView, HasStrHelp, attribute
from .constants import NA
from .databook_gc import (
    abstract_gridsat_gc,
    channel_correspondence,
    channel_description_gc,
    dataset_name_gridsat_gc,
    geospatial_resolution_deg,
    geospatial_resolution_km,
    measurement_range_lower_bound,
    measurement_range_upper_bound,
    measurement_units,
    platform_gridsat_gc,
    square_igfov_at_nadir,
    wavelength_range_lower_bound,
    wavelength_range_upper_bound,
)

NAN_TUPLE = math.nan, math.nan


class DatabookMetadata(HasStrHelp):

    dataset: str = NA
    abstract: str = NA
    description: str = NA
    channel_id: str = NA
    channel: str = NA
    geospatial_resolution_deg: tuple[float, float] = NAN_TUPLE
    geospatial_resolution_km: tuple[float, float] = NAN_TUPLE
    measurement_bounds: tuple[float, float] = NAN_TUPLE
    measurement_units: str = NA
    square_fov_at_nadir: float = math.nan
    wavelength: float = math.nan
    wavelength_bounds: tuple[float, float] = NAN_TUPLE

    def __init__(self, channel: str, platform: str) -> None:
        origin = platform_gridsat_gc[platform]
        channel_orig = channel_correspondence[origin][channel]

        self.dataset = dataset_name_gridsat_gc
        self.abstract = abstract_gridsat_gc

        if channel_orig == 0:
            self.channel += (
                f"GridSat '{channel}' is not supported by {platform} origin"
            )
            return

        self.description = channel_description_gc[channel]

        self.channel_id = channel
        self.channel = f"Channel {channel_orig}"

        self.geospatial_resolution_deg = geospatial_resolution_deg
        self.geospatial_resolution_km = geospatial_resolution_km

        measurement_lo = measurement_range_lower_bound[origin][channel_orig]
        measurement_up = measurement_range_upper_bound[origin][channel_orig]
        self.measurement_bounds = measurement_lo, measurement_up

        self.measurement_units = measurement_units[channel_orig]

        wavelength_lo = wavelength_range_lower_bound[origin][channel_orig]
        wavelength_up = wavelength_range_upper_bound[origin][channel_orig]
        self.wavelength_bounds = wavelength_lo, wavelength_up

        self.wavelength = 0.5 * (wavelength_lo + wavelength_up)

        self.square_fov_at_nadir = square_igfov_at_nadir[origin][channel_orig]


class DatasetMetadata(DatasetView):

    title: str = attribute()
    id: str = attribute()
    summary: str = attribute()
    conventions: str = attribute("Conventions")
    license: str = attribute()
    processing_level: str = attribute()
    product_version: str = attribute()
    project: str = attribute()
    institution: str = attribute()
    comment: str = attribute()
    platform: str = attribute()
    instrument: str = attribute()
    keywords: str = attribute()
    platform_vocabulary: str = attribute()
    sensor_vocabulary: str = attribute()
    keywords_vocabulary: str = attribute()
    naming_authority: str = attribute()
    standard_name_vocabulary: str = attribute()
    metadata_link: str = attribute()
    ncei_template_version: str = attribute()
    date_created: str = attribute()
    date_modified: str = attribute()
    projection: str = attribute("Projection")
    time_coverage_start: str = attribute()
    time_coverage_end: str = attribute()
    history: str = attribute()

    @property
    def origin(self) -> str:
        return (
            match[0]
            if (match := search(r"GOES-\d{1,2}", self.platform))
            else ""
        )


class GSDatasetMetadata(DatabookMetadata, DatasetMetadata):

    def __init__(self, record: Dataset, channel: str) -> None:
        DatasetMetadata.__init__(self, record, channel=channel)

    def __post_init__(self, record: Dataset, **kwargs: Any) -> None:
        channel: str = kwargs["channel"]
        DatabookMetadata.__init__(self, channel, self.origin)
