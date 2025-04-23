from datetime import datetime, timedelta, timezone
from math import nan
from re import search
from typing import Protocol

from netCDF4 import Dataset
from numpy import int32

from ..netcdf import DatasetView, HasStrHelp, attribute, scalar, variable
from ..utils.array import ArrayInt16, ArrayInt32, ArrayUint16
from .databook_gr import (
    channel_correspondence_goesr,
    channel_description_goesr,
    get_abstract_goesr,
    origin_platform_goesr,
    scene_id_goesr,
    scene_name_goesr,
    spectral_units_goesr,
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

    project: str
    title: str
    dataset_name: str
    cdm_data_type: str
    plaform_id: str = attribute("platform_ID")
    orbital_slot: str
    instrument_type: str
    summary: str
    keywords: str
    spatial_resolution: str
    timeline_id: str

    datetime_start: datetime = attribute(
        "time_coverage_start", convert=datetime.fromisoformat
    )
    datetime_end: datetime = attribute(
        "time_coverage_end", convert=datetime.fromisoformat
    )


class _MeasurementInfo(Protocol):

    standard_name: str
    long_name: str
    units: str

    valid_range: ArrayInt16
    scale_factor: float
    add_offset: float


class _BandInfo(Protocol):
    band_id: int
    band_wavelength: float
    sensor_band_bit_depth: int


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

    units: str = NA
    """
    The measurement field units.
    """

    remarks: str = NA
    """
    Remarks about the measurement.
    """

    valid_range: tuple[float, float] = ()
    """
    The valid range for the measurements.
    """

    shape: tuple[int, ...] = ()
    """
    The dimesions of the image.
    """

    def __init__(self, dataframe: Dataset, channel: str = "") -> None:
        if channel and channel not in channel_correspondence_goesr:
            allowed_channels = "', '".join(channel_correspondence_goesr.keys())
            raise ValueError(
                f"Invalid channel: '{channel}'; "
                f"allowed channels are: '{allowed_channels}'"
            )

        info = _DatasetInfo(dataframe)

        kilometres_per_pixel = self._get_spatial_resolution(
            info.spatial_resolution
        )

        self.database_name = info.project
        self.abstract = get_abstract_goesr(kilometres_per_pixel)
        self.product_name = info.title
        self.product_version = info.timeline_id
        self.summary = info.summary
        self.keywords = info.keywords
        self.dataset_name = info.dataset_name
        self.comment = NA
        self.content_type = info.cdm_data_type
        self.plaform_name = self._get_platform_name(info.plaform_id)
        self.orbital_slot = info.orbital_slot
        self.instrument_name = info.instrument_type
        self.scene_name = self._get_scene_name(dataframe, info.dataset_name)

        self.coverage_start = info.datetime_start
        self.coverage_end = info.datetime_end

        if coverage_time := self._get_frame_time(dataframe):
            self.coverage_midpoint = coverage_time
        else:
            delta = self.coverage_end - self.coverage_start
            self.coverage_midpoint = self.coverage_start + delta / 2

        self.spatial_resolution = kilometres_per_pixel

        if info.cdm_data_type != "Image":
            self.band_id = NAI
            self.band_description = NA
            self.band_wavelength = NAF
            self.wavelength_units = NA
            self.radiometric_resolution = NAI

            self.standard_name = NA
            self.measurement_name = NA
            self.units = NA
            self.valid_range = ()

            self.shape = ()

            return

        product_id = GOESDatasetInfo._get_product_id(info.dataset_name)

        if product_id in {"CMIP", "MCMIP", "Rad"}:
            binfo = self._get_radiometric_info(dataframe, product_id, channel)

            self.band_id = binfo.band_id
            self.band_description = channel_description_goesr[binfo.band_id]
            self.band_wavelength = binfo.band_wavelength
            self.wavelength_units = spectral_units_goesr
            self.radiometric_resolution = binfo.sensor_band_bit_depth

        else:
            self.band_id = NAI
            self.band_description = NA
            self.band_wavelength = NAF
            self.wavelength_units = NA
            self.radiometric_resolution = NAI

        field_id = self._get_field_id(product_id, channel)

        minfo = self._get_measurement_info(dataframe, field_id)

        self.standard_name = minfo.standard_name
        self.measurement_name = minfo.long_name
        self.units = minfo.units
        self.remarks = NA

        valid_range = minfo.valid_range * minfo.scale_factor + minfo.add_offset

        self.valid_range = float(valid_range[0]), float(valid_range[1])

        self.shape = self._get_shape_info(dataframe, field_id)

    @staticmethod
    def _get_field_id(product_id: str, channel: str) -> str:
        if product_id == "CMIP":
            return "CMI"

        if product_id == "MCMIP":
            if not channel:
                raise ValueError(
                    "Channel information is required for multi-band datasets"
                )
            return f"CMI_{channel}"

        return product_id

    @staticmethod
    def _get_frame_time(dataframe: Dataset) -> datetime | None:
        if "t" not in dataframe.variables:
            return None

        class _TimeInfo(DatasetView):
            frame_time: datetime = scalar("t", convert=_j200_to_utc)

        dtinfo = _TimeInfo(dataframe)

        return dtinfo.frame_time

    @staticmethod
    def _get_measurement_info(
        dataframe: Dataset, field_id: str
    ) -> _MeasurementInfo:
        field = variable(field_id)

        class _FieldInfo(DatasetView):
            standard_name: str = field.attribute()
            long_name: str = field.attribute()
            units: str = field.attribute()

            valid_range: ArrayInt32 = field.attribute(convert=_to_array_int_32)
            scale_factor: float = field.attribute(convert=float)
            add_offset: float = field.attribute(convert=float)

        return _FieldInfo(dataframe)

    @staticmethod
    def _get_platform_name(plaform_id: str) -> str:
        return origin_platform_goesr[plaform_id]

    @staticmethod
    def _get_product_id(dataset_name: str) -> str:
        patterns = (r"^OR_ABI-L\db?-([^-]+)", r"^([A-Za-z]+)(?:C|F|M\d?)$")
        product_name: str = dataset_name
        for pattern in patterns:
            if match := search(pattern, product_name):
                product_name = match[1]
            else:
                raise ValueError(f"Unexpected dataset name: '{dataset_name}'")
        return product_name

    @staticmethod
    def _get_radiometric_info(
        dataframe: Dataset, product_id: str, channel: str
    ) -> _BandInfo:
        if product_id == "MCMIP":
            if not channel:
                raise ValueError(
                    "Channel information is required for multi-band datasets"
                )
            field_id = f"CMI_{channel}"
            bid_name = f"band_id_{channel}"
            bwl_name = f"band_wavelength_{channel}"

        elif product_id in {"CMIP", "Rad"}:
            field_id = "CMI" if product_id == "CMIP" else "Rad"
            bid_name = "band_id"
            bwl_name = "band_wavelength"

        else:
            raise ValueError(f"Unexpected product ID: '{product_id}'")

        field = variable(field_id)

        class _FieldInfo(DatasetView):
            band_id: int = scalar(bid_name, convert=int)
            band_wavelength: float = scalar(bwl_name, convert=float)
            sensor_band_bit_depth: int = field.attribute(convert=int)

        return _FieldInfo(dataframe)

    @staticmethod
    def _get_scene_name(dataframe: Dataset, dataset_name: str) -> str:
        # Check for scene support
        scene_id_attr = "scene_id"
        if not hasattr(dataframe, scene_id_attr):
            return NA

        # Get the scene ID
        scene_id: str = getattr(dataframe, scene_id_attr)
        scene_char_id = scene_id_goesr[scene_id]

        if scene_char_id == "M":
            pattern = r"^OR_ABI-L\db?-([^-]+)"
            if match := search(pattern, dataset_name):
                product_id = match[1]
                pattern = r".+(M\d)"
                if match := search(pattern, product_id):
                    scene_id = match[1]
        else:
            scene_id = scene_char_id

        return scene_name_goesr[scene_id]

    @staticmethod
    def _get_shape_info(dataframe: Dataset, field_id: str) -> tuple[int, ...]:
        field = variable(field_id)

        class _ShapeInfo(DatasetView):
            shape: tuple[int] = field.attribute()

        sinfo = _ShapeInfo(dataframe)

        return sinfo.shape

    @staticmethod
    def _get_spatial_resolution(fov_at_nadir: str) -> float:
        pattern = r"^(\d+\.?\d*)([km]+)"

        if match := search(pattern, fov_at_nadir):
            value, units = match.groups()
        else:
            raise ValueError(
                f"Unable to parse spatial resolution: '{fov_at_nadir}'"
            )

        if units not in {"m", "km"}:
            raise ValueError(
                f"Unexpected spatial resolution units: '{fov_at_nadir}'"
            )

        units_per_pixel = float(value)

        scale = 1.0 if units == "km" else 1.0 / 1000.0

        return float(units_per_pixel * scale)
