from datetime import datetime, timedelta, timezone
from math import nan
from re import search
from typing import Protocol

from netCDF4 import Dataset
from numpy import int32

from ..netcdf import DatasetView, HasStrHelp, attribute
from ..utils.array import ArrayInt16, ArrayInt32, ArrayUint16
from .databook_gc import (
    GRS80_KILOMETRES_PER_DEGREE,
    channel_correspondence_gc,
    channel_description_gc,
    dataset_name_gc,
    get_abstract_gridsat_gc,
    platform_origin_gridsat_gc,
    radiometric_resolution_gc,
    scene_id_gc,
    scene_name_gc,
    spectral_units_gc,
    wavelength_range_lower_bound_gc,
    wavelength_range_upper_bound_gc,
)

NA = "not available"
NAI = -999
NAF = nan


def _j200_to_utc(j200_time_sec: float) -> datetime:
    j2000_epoch_utc = datetime(2000, 1, 1, 12, tzinfo=timezone.utc)
    delta_sec = timedelta(seconds=j200_time_sec)
    return j2000_epoch_utc + delta_sec


def _to_array_int_32(array: ArrayInt16 | ArrayUint16) -> ArrayInt32:
    return array.astype(int32)


class _DatasetInfo(DatasetView):

    # project: str
    title: str
    platform: str
    product_version: str
    id: str
    comment: str
    cdm_data_type: str
    instrument: str
    summary: str
    keywords: str
    spatial_resolution: float = attribute(
        "geospatial_lat_resolution", convert=float
    )

    datetime_start: datetime = attribute(
        "time_coverage_start", convert=datetime.fromisoformat
    )
    datetime_end: datetime = attribute(
        "time_coverage_end", convert=datetime.fromisoformat
    )


class _VISInfo(Protocol):

    long_name: str
    units: str
    actual_range: ArrayInt16

    shape: tuple[int]


class _IRInfo(Protocol):

    long_name: str
    standard_name: str
    units: str
    actual_range: ArrayInt16

    measurement_name: str
    measurement_units: str

    shape: tuple[int]


class GOESDatasetInfo(HasStrHelp):

    database_name: str = NA
    """
    The database name.
    """

    abstract: str = NA
    """
    The database abstract.
    """

    product_name: str = NA
    """
    The product name.
    """

    product_version: str
    """
    The product version.
    """

    summary: str = NA
    """
    The product summary.
    """

    keywords: str = NA
    """
    The product keywords.
    """

    dataset_name: str = NA
    """
    The dataset name.
    """

    comment: str = NA
    """
    The dataset comment.
    """

    content_type: str = NA
    """
    The dataset content type.
    """

    plaform_name: str = NA
    """
    The platform name (e.g. 'GOES-16', 'GOES-19', etc.).
    """

    orbital_slot: str = NA
    """
    The orbital slot identifier.
    """

    instrument_name: str = NA
    """
    The instrument name.
    """

    scene_name: str = NA
    """
    The scene name (e.g. 'Full Disk', etc.).
    """

    coverage_start: datetime
    """
    The coverage start time.
    """

    coverage_end: datetime
    """
    The coverage end time.
    """

    coverage_midpoint: datetime
    """
    The mid-point between the start and end image scan.
    """

    band_id: int = NAI
    """
    The band identifier.
    """

    band_description: str = NA
    """
    The band description.
    """

    band_wavelength: float = NAF
    """
    The band central wavelength.
    """

    wavelength_units: str = NA
    """
    The wavelength units.
    """

    spatial_resolution: float = NAF
    """
    The spatial resolution (square FOV at nadir) in kilometres per
    pixel.
    """

    radiometric_resolution: int = NAI
    """
    The radiometric resolution in bits.
    """

    standard_name: str = NA
    """
    The measurement field standard name.
    """

    measurement_name: str = NA
    """
    The measurement field name.
    """

    measurement_units: str = NA
    """
    The measurement field units.
    """

    valid_range: tuple[float, float] = (NAF, NAF)
    """
    The valid range for the measurements.
    """

    shape: tuple[int, ...] = ()
    """
    The dimesions of the image.
    """

    def __init__(self, dataframe: Dataset, channel: str) -> None:
        if not channel:
            raise ValueError(
                "Channel information is required for multi-band datasets"
            )
        if channel not in channel_description_gc:
            allowed_channels = "', '".join(channel_description_gc.keys())
            raise ValueError(
                f"Invalid channel: '{channel}'; "
                f"allowed channels are: '{allowed_channels}'"
            )

        info = _DatasetInfo(dataframe)

        if info.cdm_data_type != "Grid":
            raise ValueError(
                "Unexpected content type. "
                f"Expected 'Grid', got '{info.cdm_data_type}'"
            )

        kilometres_per_pixel = self._get_spatial_resolution(
            info.spatial_resolution
        )

        self.database_name = dataset_name_gc
        self.abstract = get_abstract_gridsat_gc(kilometres_per_pixel)
        self.product_name = info.title
        self.product_version = info.product_version
        self.summary = info.summary
        self.keywords = info.keywords
        self.dataset_name = info.id
        self.comment = info.comment
        self.content_type = info.cdm_data_type
        self.plaform_name = self._get_platform_name(info.platform)
        self.orbital_slot = NA
        self.instrument_name = info.instrument
        self.scene_name = self._get_scene_name(info.id)

        self.coverage_start = info.datetime_start
        self.coverage_end = info.datetime_end

        delta = self.coverage_end - self.coverage_start
        self.coverage_midpoint = self.coverage_start + delta / 2

        self.spatial_resolution = kilometres_per_pixel

        platform_id = platform_origin_gridsat_gc[self.plaform_name]

        channel_nr = channel_correspondence_gc[platform_id][channel]

        self.band_id = channel_nr
        self.band_description = channel_description_gc[channel]

        wl_lower = wavelength_range_lower_bound_gc[platform_id][channel_nr]
        wl_upper = wavelength_range_upper_bound_gc[platform_id][channel_nr]
        self.band_wavelength = 0.5 * (wl_lower + wl_upper)

        self.wavelength_units = spectral_units_gc

        self.radiometric_resolution = radiometric_resolution_gc

        # ---------------------------------------

        self.standard_name = NA
        self.measurement_name = NA
        self.measurement_units = NA
        self.valid_range = ()

        self.shape = ()

    @staticmethod
    def _get_platform_name(platform: str) -> str:
        pattern = r"(GOES-\d+)"
        if match := search(pattern, platform):
            return match[1]
        raise ValueError(f"Unexpected platform: '{platform}'")

    @staticmethod
    def _get_scene_name(dataset_name: str) -> str:
        pattern = r"^GOES-([CEGNOSU]+)\."
        if match := search(pattern, dataset_name):
            scene_id: str = match[1]
        else:
            raise ValueError(f"Unexpected dataset ID: '{dataset_name}'")
        scene_char_id = scene_id_gc[scene_id]

        return scene_name_gc[scene_char_id]

    @staticmethod
    def _get_spatial_resolution(degrees_per_pixel: float) -> float:
        pixels_per_degree = 1.0 / degrees_per_pixel
        pixels_per_kilometre = pixels_per_degree / GRS80_KILOMETRES_PER_DEGREE
        return 1.0 / pixels_per_kilometre
