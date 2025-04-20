"""
GOES Image data extraction.

This module provides classes to extract and represent image information
from GOES satellite netCDF data files.

Classes
-------
GOESImage
    Represent a GOES satellite image data.
GOESImageMetadata
    Represent GOES image metadata attributes.
"""

from typing import Any, Protocol, cast

from netCDF4 import Dataset  # pylint: disable=no-name-in-module
from numpy import float32, int8, int16, int32, nan
from numpy.typing import NDArray

from ..geodesy import RectangularRegion
from ..netcdf import DatasetView, HasStrHelp, computed, scalar, variable
from ..protocols.geodetic import IndexRange
from ..utils.array import ArrayBool, ArrayFloat32, MaskedFloat32
from .netcdf_geodetic import GOESLatLonGrid

cmip = variable("CMI")


class GOESImageMetadata(DatasetView):
    """
    Represent GOES image metadata attributes.

    Attributes
    ----------
    long_name : str
        A descriptive name for the dataset.
    standard_name : str
        A standard name for the dataset.
    sensor_band_bit_depth : int8
        The bit depth of the sensor band.
    valid_range : NDArray[int16]
        The valid range of data values.
    scale_factor : float32
        The scale factor to apply to the data values.
    add_offset : float32
        The offset to add to the data values.
    units : str
        The units of the data values.
    resolution : str
        The spatial resolution of the data.
    grid_mapping : str
        The grid mapping information.
    """

    long_name: str = cmip.attribute()
    standard_name: str = cmip.attribute()
    valid_range: NDArray[int16] = cmip.attribute()
    units: str = cmip.attribute()
    coordinates: str = cmip.attribute()
    grid_mapping: str = cmip.attribute()
    shape: tuple[int] = cmip.attribute()

    band_id: int32 = scalar()
    band_wavelength: float32 = scalar()


class GOESImageMetadataCMI(GOESImageMetadata):

    sensor_band_bit_depth: int8 = cmip.attribute()
    resolution: str = cmip.attribute()
    range: ArrayFloat32 = computed()

    def __post_init__(self, record, **kwargs) -> None:
        cmip = record.variables["CMI"]
        range_ = cmip.valid_range * cmip.scale_factor + cmip.add_offset
        object.__setattr__(self, "range", range_)


class ImageData(Protocol):

    raster: MaskedFloat32


class GOESImageData(HasStrHelp):

    raster: MaskedFloat32


class GOESImage(GOESImageData):
    """
    Represent a GOES satellite image data.

    Hold data for the Cloud and Moisture Imagery (CMI) bands.
    """

    _grid: GOESLatLonGrid

    metadata: GOESImageMetadata

    def __init__(
        self, record: Dataset, field: str, grid: GOESLatLonGrid
    ) -> None:
        # Validate channel parameter
        self._validate_field(field, record)

        data = self._extract_image(
            record, field, grid.lon_limits, grid.lat_limits
        )

        self._grid = grid
        self.raster = data.raster

        if field == "CMI":
            self.metadata = GOESImageMetadataCMI(record)
        else:
            self.metadata = GOESImageMetadata(record)

    @staticmethod
    def _extract_image(
        record: Dataset,
        field: str,
        lon_limits: IndexRange,
        lat_limits: IndexRange,
    ) -> ImageData:
        def slice(x: Any) -> Any:
            min_lon, max_lon = lon_limits
            min_lat, max_lat = lat_limits
            return x[min_lat:max_lat, min_lon:max_lon]

        class _GOESImageData(DatasetView):
            raster: MaskedFloat32 = variable(field).array(filter=slice)

        data = _GOESImageData(record)

        data.raster.data[data.raster.mask] = nan

        return data

    @staticmethod
    def _validate_field(field: str, record: Dataset) -> None:
        available_fields = {"CMI", "DQF"}
        # Validate field id
        if field not in available_fields:
            allowed_fields = ", ".join(available_fields)
            raise ValueError(
                f"Invalid 'field': '{field}'; "
                f"allowed fields are: {allowed_fields}"
            )

    @property
    def image(self) -> ArrayFloat32:
        return cast(ArrayFloat32, self.raster.data)

    @property
    def mask(self) -> ArrayBool:
        return cast(ArrayBool, self.raster.mask)

    @property
    def region(self) -> RectangularRegion:
        return self._grid.region

    @property
    def grid(self) -> GOESLatLonGrid:
        return self._grid
