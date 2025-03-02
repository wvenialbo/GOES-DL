"""
GOES precomputed latitude and longitude grids data extraction.

This module provides classes to extract and represent latitude and
longitude grids information from GOES satellite netCDF data files.

Classes
-------
GOESLatLonGrid
    Hold GOES satellite precomputed latitude and longitude data.
GOESLatLonGridData
    Represent GOES satellite precomputed latitude or longitude data.
GOESLatLonGridMetadata
    Hold GOES satellite latitude and longitude metadata.
GOESLatLonGridMetadataType
    Represent a GOES satellite latitude or longitude metadata.
GOESLatLonGridInfo
    Hold GOES geodetic grid dataset metadata information.
"""

from typing import Any, cast

from netCDF4 import Dataset  # pylint: disable=no-name-in-module
from numpy import (
    bool_,
    dtype,
    float32,
    float64,
)
from numpy.ma import MaskedArray
from numpy.typing import NDArray

from .class_help import HasStrHelp
from .fields import (
    VariableType,
    dimension,
    make_variable,
)
from .fragment import DataFragment

MaskedFloat32 = MaskedArray[Any, dtype[float32]]


class GOESLatLonGridData:
    """
    Represent GOES satellite precomputed latitude or longitude data.

    Attributes
    ----------
    data : NDArray[float32]
        The latitude or longitude grid data.
    mask : NDArray[bool]
        The array containing the mask values indicating invalid data
        points.
    fill_value : uint16
        The fill value used for missing or invalid data points.
    """

    def __init__(self, array: MaskedFloat32) -> None:
        """
        Initialize a GOESLatLonGridData object.

        Parameters
        ----------
        array : MaskedFloat32
            The masked array containing the latitude or longitude grid
            data.
        """
        self.data = array.data
        self.mask = array.mask
        self.fill_value = array.fill_value

    data: NDArray[float32]
    mask: NDArray[bool_]
    fill_value: float32


def _latlon_data(name: str, record: Dataset) -> GOESLatLonGridData:
    latlon: VariableType = make_variable(name, array=True)

    class _GOESLatLonGridData(DataFragment):
        data: NDArray[float32] = latlon()
        mask: NDArray[bool_] = latlon()
        fill_value: float32 = latlon()

    _GOESLatLonGridData.__module__ = GOESLatLonGridData.__module__
    _GOESLatLonGridData.__name__ = GOESLatLonGridData.__name__
    _GOESLatLonGridData.__qualname__ = GOESLatLonGridData.__qualname__

    data = _GOESLatLonGridData(record)

    return cast(GOESLatLonGridData, data)


class GOESLatLonGrid(HasStrHelp):
    """
    Hold GOES satellite precomputed latitude and longitude data.

    Notes
    -----
    For information on GOES Imager Projection and GOES orbit geometry,
    see [1]_ and Section 4.2. of [2]_ For information on getting the
    precomputed latitude and longitude grid dataset, see [1]_.

    Attributes
    ----------
    latitude : GOESLatLonGridData
        The latitude grid data.
    longitude : GOESLatLonGridData
        The longitude grid data.

    References
    ----------
    .. [1] STAR Atmospheric Composition Product Training, "GOES Imager
        Projection (ABI Fixed Grid)", NOAA/NESDIS/STAR, 2024.
        https://www.star.nesdis.noaa.gov/atmospheric-composition-training/satellite_data_goes_imager_projection.php.
    .. [2] GOES-R, " GOES-R Series Product Definition and User’s Guide
        (PUG), Volume 5: Level 2+ Products", Version 2.4,
        NASA/NOAA/NESDIS, 2022.
        https://www.ospo.noaa.gov/Organization/Documents/PUG/GS%20Series%20416-R-PUG-L2%20Plus-0349%20Vol%205%20v2.4.pdf
    """

    latitude: GOESLatLonGridData
    longitude: GOESLatLonGridData

    def __init__(self, record: Dataset) -> None:
        """
        Initialize a GOESGrid object from a precomputed netCDF dataset.

        Parameters
        ----------
        record : Dataset
            The netCDF dataset containing the precomputed latitude
            and longitude grid data.
        """
        self.latitude = _latlon_data("latitude", record)
        self.longitude = _latlon_data("longitude", record)


class GOESLatLonGridMetadataType:
    """
    Represent a GOES satellite latitude or longitude metadata.

    Attributes
    ----------
    long_name : str
        A descriptive name for the variable.
    valid_range : NDArray[float64]
        The valid range of values for the variable.
    units : str
        The units of measurement for the variable.
    comment : str
        Additional comments or information about the variable.
    """

    long_name: str
    valid_range: NDArray[float64]
    units: str
    comment: str


def _latlon_metadata(name: str, record: Dataset) -> GOESLatLonGridMetadataType:
    latlon: VariableType = make_variable(name)

    class _GOESLatLonGridMetadata(DataFragment):
        long_name: str = latlon()
        valid_range: NDArray[float64] = latlon()
        units: str = latlon()
        comment: str = latlon()

    _GOESLatLonGridMetadata.__module__ = GOESLatLonGridMetadataType.__module__
    _GOESLatLonGridMetadata.__name__ = (
        "GOESLatMetadata" if name == "latitude" else "GOESLonMetadata"
    )
    _GOESLatLonGridMetadata.__qualname__ = _GOESLatLonGridMetadata.__name__

    metadata = _GOESLatLonGridMetadata(record)

    return cast(GOESLatLonGridMetadataType, metadata)


class GOESLatLonGridMetadata(HasStrHelp):
    """
    Hold a GOES satellite latitude and longitude metadata.

    Attributes
    ----------
    latitude : GOESLatLonGridMetadataType
        The latitude metadata.
    longitude : GOESLatLonGridMetadataType
        The longitude metadata.
    """

    latitude: GOESLatLonGridMetadataType
    longitude: GOESLatLonGridMetadataType

    def __init__(self, record: Dataset) -> None:
        self.latitude = _latlon_metadata("latitude", record)
        self.longitude = _latlon_metadata("longitude", record)


class GOESLatLonGridInfo(DataFragment):
    """
    Hold GOES geodetic grid dataset metadata information.

    Attributes
    ----------
    title : str
        The title of the dataset.
    comment : str
        Comments or information about the dataset.
    created : str
        The date the dataset was created.
    rows : int
        The number of rows in the the grid.
    columns : int
        The number of columns in the the grid.
    """

    title: str
    comment: str
    created: str
    rows: int = dimension()
    columns: int = dimension()
