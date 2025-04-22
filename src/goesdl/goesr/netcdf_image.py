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
from numpy import nan

from ..geodesy import RectangularRegion
from ..netcdf import DatasetView, HasStrHelp, variable
from ..protocols.geodetic import IndexRange
from ..utils.array import ArrayBool, ArrayFloat32, MaskedFloat32
from .databook_gr import product_summary
from .netcdf_geodetic import GOESLatLonGrid
from .netcdf_info import GOESPlatformInfo


class ImageData(Protocol):

    raster: MaskedFloat32


class GOESImageData(HasStrHelp):

    raster: MaskedFloat32


class _DatasetInfo(DatasetView):

    dataset_name: str


class GOESImage(GOESImageData):
    """
    Represent a GOES-R Series satellite image data.

    Hold data for the Cloud and Moisture Imagery (CMI) bands.
    """

    grid: GOESLatLonGrid

    def __init__(
        self, record: Dataset, grid: GOESLatLonGrid, channel: str = ""
    ) -> None:
        product_name = self._validate_product(record)

        channel_id = self._validate_channel(record, channel)

        field = self._validate_field(record, product_name, channel_id)

        data = self._extract_image(
            record, field, grid.lon_limits, grid.lat_limits
        )

        self.grid = grid
        self.raster = data.raster

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
    def _validate_channel(record: Dataset, channel: str) -> str:
        pinfo = GOESPlatformInfo(record, channel)
        return pinfo.channel_id

    @staticmethod
    def _validate_field(
        record: Dataset, product_name: str, channel_id: str
    ) -> str:
        if product_name == "MCMIP":
            field = f"CMI_{channel_id}"
        elif product_name == "CMIP":
            field = "CMI"
        else:
            field = product_name

        if field not in record.variables:
            raise ValueError(f"Field '{field}' not found in the dataset")

        if record.variables[field].ndim != 2:
            raise ValueError(
                f"The product '{product_name}' does not containt an image"
            )

        return field

    @staticmethod
    def _validate_product(record: Dataset) -> str:
        dinfo = _DatasetInfo(record)

        product_name, _, _ = product_summary(dinfo.dataset_name)

        if not product_name:
            raise ValueError(
                f"The dataset '{dinfo.dataset_name}' does not containt"
                "an image"
            )

        return product_name

    @property
    def image(self) -> ArrayFloat32:
        return cast(ArrayFloat32, self.raster.data)

    @property
    def mask(self) -> ArrayBool:
        return cast(ArrayBool, self.raster.mask)

    @property
    def region(self) -> RectangularRegion:
        return self.grid.region
