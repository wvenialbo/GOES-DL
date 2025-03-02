"""
This module provides classes to extract and represent information from
GOES satellite netCDF data files. The classes dynamically set attributes
based on the annotations defined in the class and the corresponding
attributes or variables present in the provided netCDF data object.
"""

from typing import Any

from netCDF4 import Dataset  # pylint: disable=no-name-in-module
from numpy import (
    arctan,
    cos,
    dtype,
    errstate,
    float32,
    float64,
    hstack,
    isnan,
    meshgrid,
    nan,
    power,
    rad2deg,
    sin,
    sqrt,
    vstack,
    where,
)
from numpy.ma import MaskedArray, masked_invalid
from numpy.typing import NDArray

from .class_help import help_str

MaskedFloat32 = MaskedArray[Any, dtype[float32]]


FILL_VALUE = -999.99


class GOESGeodeticGrid:
    """
    Represent latitude and longitude grid data computed on the fly.

    Calculate the latitude and longitude grid arrays on the fly from the
    GOES Imager Projection information in ABI Level 2 files.

    Notes
    -----
    For information on GOES Imager Projection and GOES orbit geometry,
    see [1]_ and Section 4.2. of [3]_. For a Python demonstration on
    calculating latitude and longitude from GOES Imager Projection
    information, see [2]_. The code snippet in this class is based on
    the Python demonstration in [2]_.

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
    .. [2] Aerosols and Atmospheric Composition Science Team, "Python
        Short Demo: Calculate Latitude and Longitude from GOES Imager
        Projection (ABI Fixed Grid) Information", NOAA/NESDIS/STAR,
        2024.
        https://www.star.nesdis.noaa.gov/atmospheric-composition-training/python_abi_lat_lon.php
    .. [3] GOES-R, " GOES-R Series Product Definition and User’s Guide
        (PUG), Volume 5: Level 2+ Products", Version 2.4,
        NASA/NOAA/NESDIS, 2022.
        https://www.ospo.noaa.gov/Organization/Documents/PUG/GS%20Series%20416-R-PUG-L2%20Plus-0349%20Vol%205%20v2.4.pdf
    """

    latitude: GOESLatLonGridData
    longitude: GOESLatLonGridData

    def __init__(self, record: Dataset, fast: bool = False) -> None:
        """
        Initialize a GOESGeodeticGrid object.

        Parameters
        ----------
        record : Dataset
            The netCDF dataset containing ABI Level 2 data.
        """
        lat, lon = self._initialize_latlon_grid(record, fast)

        self.latitude = GOESLatLonGridData(lat)
        self.longitude = GOESLatLonGridData(lon)

    def __str__(self) -> str:
        # Returns a string representation of the GOESLatLonGridData object.
        return help_str(self)

    @classmethod
    def _initialize_latlon_grid(
        cls, record: Dataset, fast: bool
    ) -> tuple[MaskedFloat32, MaskedFloat32]:
        # Ignore numpy errors for `sqrt` of negative number; reference
        # [2] states that this "occurs for GOES-16 ABI CONUS sector
        # data", however I found it also occurs for Full Disd sector.
        with errstate(invalid="ignore"):
            if fast:
                lat, lon = cls._calculate_latlon_grid_fast(record)
            else:
                lat, lon = cls._calculate_latlon_grid(record)

        latitude: MaskedFloat32 = masked_invalid(lat)  # type: ignore
        longitude: MaskedFloat32 = masked_invalid(lon)  # type: ignore

        latitude.fill_value = FILL_VALUE
        longitude.fill_value = FILL_VALUE

        return latitude, longitude
