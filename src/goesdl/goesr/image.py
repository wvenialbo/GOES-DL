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

from re import search
from typing import Any, Protocol, cast

from netCDF4 import Dataset  # pylint: disable=no-name-in-module
from numpy import nan

from ..geodesy import RectangularRegion
from ..netcdf import DatasetView, HasStrHelp, variable
from ..protocols.geodetic import IndexRange
from ..utils.array import ArrayBool, ArrayFloat32, MaskedFloat32
from .databook_gr import channel_correspondence_goesr
from .geodetic import GOESLatLonGrid


class ImageData(Protocol):

    raster: MaskedFloat32


class GOESImageData(HasStrHelp):

    raster: MaskedFloat32


class _DatasetInfo(DatasetView):

    cdm_data_type: str
    dataset_name: str


class GOESImage(GOESImageData):
    """
    Represent a GOES-R Series satellite image data.

    Hold data for the Cloud and Moisture Imagery (CMI) bands.
    """

    grid: GOESLatLonGrid

    def __init__(
        self, dataframe: Dataset, grid: GOESLatLonGrid, channel: str = ""
    ) -> None:
        product_id = self._validate_product(dataframe)

        channel_id = self._validate_channel(product_id, channel)

        field_id = self._validate_field(dataframe, product_id, channel_id)

        data = self._extract_image(
            dataframe, field_id, grid.lon_limits, grid.lat_limits
        )

        self.grid = grid
        self.raster = data.raster

    @staticmethod
    def _extract_image(
        dataframe: Dataset,
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

        data = _GOESImageData(dataframe)

        data.raster.data[data.raster.mask] = nan

        return data

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
    def _validate_channel(product_id: str, channel: str) -> str:
        if product_id == "MCMIP" and not channel:
            raise ValueError(
                "Channel information is required for multi-band datasets"
            )

        if channel and channel not in channel_correspondence_goesr:
            allowed_channels = "', '".join(channel_correspondence_goesr.keys())
            raise ValueError(
                f"Invalid channel: '{channel}'; "
                f"allowed channels are: '{allowed_channels}'"
            )

        return channel

    @staticmethod
    def _validate_field(
        dataframe: Dataset, product_id: str, channel_id: str
    ) -> str:
        if product_id == "MCMIP":
            field_id = f"CMI_{channel_id}"
        elif product_id == "CMIP":
            field_id = "CMI"
        else:
            field_id = product_id

        if field_id not in dataframe.variables:
            raise ValueError(f"Field '{field_id}' not found in the dataset")

        if ("y", "x") != dataframe.variables[field_id].dimensions:
            raise ValueError(
                f"Field '{field_id}' does not have the required dimensions"
            )

        return field_id

    @classmethod
    def _validate_product(cls, dataframe: Dataset) -> str:
        dinfo = _DatasetInfo(dataframe)

        if dinfo.cdm_data_type != "Image":
            raise ValueError(
                f"The dataset '{dinfo.dataset_name}' does not containt"
                "an image"
            )

        return cls._get_product_id(dinfo.dataset_name)

    @property
    def image(self) -> ArrayFloat32:
        return cast(ArrayFloat32, self.raster.data)

    @property
    def mask(self) -> ArrayBool:
        return cast(ArrayBool, self.raster.mask)

    @property
    def region(self) -> RectangularRegion:
        return self.grid.region
