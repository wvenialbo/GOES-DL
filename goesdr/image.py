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

from numpy import bool_, float32, int8, int16, int32, uint16
from numpy.typing import NDArray

from .netcdf import DataFragment, make_variable, scalar
from .netcdf.fields import VariableType

cmip: VariableType = make_variable("CMI", array=True)


class GOESImage(DataFragment):
    """
    Represent a GOES satellite image data.

    Hold data for the Cloud and Moisture Imagery (CMI) bands.

    Attributes
    ----------
    band_id : int32
        The ID of the band.
    band_wavelength : float32
        The wavelength of the band.
    data : NDArray[float32]
        The image data.
    mask : NDArray[bool]
        The array containing the mask values indicating invalid data
        points.
    fill_value : uint16
        The fill value used for missing or invalid data points.
    """

    band_id: int32 = scalar()
    band_wavelength: float32 = scalar()

    data: NDArray[float32] = cmip()
    mask: NDArray[bool_] = cmip()
    fill_value: uint16 = cmip()


class GOESImageMetadata(DataFragment):
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

    long_name: str = cmip()
    standard_name: str = cmip()
    sensor_band_bit_depth: int8 = cmip()
    valid_range: NDArray[int16] = cmip()
    scale_factor: float32 = cmip()
    add_offset: float32 = cmip()
    units: str = cmip()
    resolution: str = cmip()
    grid_mapping: str = cmip()
