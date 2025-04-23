from datetime import datetime
from math import nan
from re import search
from typing import Any, Protocol, cast

from netCDF4 import Dataset

from ..netcdf import DatasetView, HasStrHelp, attribute, field, variable
from .databook_gc import (
    GRS80_KILOMETRES_PER_DEGREE,
    ch1_standard_name,
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


class _DatasetInfo(DatasetView):

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


class _ImageInfo(Protocol):

    long_name: str
    standard_name: str
    units: str
    actual_range: tuple[float, float]
    comment: str
    shape: tuple[int]


class GSDatasetInfo(HasStrHelp):

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

    units: str = NA
    """
    The measurement field units.
    """

    remarks: str = NA
    """
    Remarks about the measurement.
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
        self._validate_channel(channel)

        info = _DatasetInfo(dataframe)

        self._validate_content_type(info.cdm_data_type)

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

        if channel_nr:
            self.band_description = channel_description_gc[channel]
            wl_lower = wavelength_range_lower_bound_gc[platform_id][channel_nr]
            wl_upper = wavelength_range_upper_bound_gc[platform_id][channel_nr]
            self.band_wavelength = 0.5 * (wl_lower + wl_upper)
            self.wavelength_units = spectral_units_gc
            self.radiometric_resolution = radiometric_resolution_gc
        else:
            self.band_description = NA
            self.band_wavelength = NAF
            self.wavelength_units = NA
            self.radiometric_resolution = NAI

        minfo = self._get_measurement_info(dataframe, channel)

        self.standard_name = minfo.standard_name
        self.measurement_name = minfo.long_name
        self.units = minfo.units
        self.remarks = minfo.comment
        self.valid_range = minfo.actual_range
        self.shape = minfo.shape

    @staticmethod
    def _get_measurement_info(dataframe: Dataset, field_id: str) -> _ImageInfo:
        image = variable(field_id)

        def _to_float_tuple(x: Any) -> tuple[float, float]:
            return float(x[0]), float(x[1])

        class _IMInfo(DatasetView):
            long_name: str = image.attribute()
            units: str = image.attribute()
            actual_range: tuple[float] = image.attribute(
                convert=_to_float_tuple
            )
            shape: tuple[int] = image.attribute()

        if field_id == "ch1":

            class _VISInfo(_IMInfo):
                standard_name: str = field(ch1_standard_name)
                comment: str = image.attribute()

            vis_info = _VISInfo(dataframe)

            return cast(_ImageInfo, vis_info)

        class _IRInfo(_IMInfo):
            standard_name: str = image.attribute()
            comment: str = field(NA)

        ir_info = _IRInfo(dataframe)

        return cast(_ImageInfo, ir_info)

    @staticmethod
    def _get_platform_name(platform: str) -> str:
        pattern = r"(GOES-\d+)"
        if match := search(pattern, platform):
            return match[1]
        raise ValueError(f"Unexpected platform: '{platform}'")

    @staticmethod
    def _get_scene_name(dataset_name: str) -> str:
        pattern = r"^GridSat-([CEGNOSU]+)\."
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

    @staticmethod
    def _validate_channel(channel: str) -> None:
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

    def _validate_content_type(self, content_type: str) -> None:
        if content_type != "Grid":
            raise ValueError(
                "Unexpected content type. "
                f"Expected 'Grid', got '{content_type}'"
            )
