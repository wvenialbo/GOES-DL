"""
This module provides classes to extract and represent information from
GOES satellite netCDF data files. The classes dynamically set attributes
based on the annotations defined in the class and the corresponding
attributes or variables present in the provided netCDF data object.
"""

from typing import Any, cast

from netCDF4 import Dataset  # pylint: disable=no-name-in-module
from numpy import (
    arctan,
    bool_,
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

from .class_help import HasStrHelp, help_str
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
    Represent GOES satellite precomputed latitude and longitude data.

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
    Represent a GOES satellite latitude and longitude metadata.

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

    @classmethod
    def _calculate_latlon_grid(
        cls, record: Dataset
    ) -> tuple[NDArray[float32], NDArray[float32]]:
        # Reorganize operations to leverage NumPy vectorization,
        # reducing redundant computations. This yields ~6x performance
        # improvement over the baseline implementation from [2].
        projection_info = GOESProjection(record)

        lambda_0 = projection_info.longitude_of_projection_origin

        r_orb = projection_info.orbital_radius
        r_eq = projection_info.semi_major_axis
        r_pol = projection_info.semi_minor_axis

        grid_data = GOESABIFixedGridArray(record)

        sin_x: NDArray[float64] = sin(grid_data.x)
        cos_x: NDArray[float64] = cos(grid_data.x)
        sin_y: NDArray[float64] = sin(grid_data.y)
        cos_y: NDArray[float64] = cos(grid_data.y)

        sin_x, sin_y = meshgrid(sin_x, sin_y)
        cos_x, cos_y = meshgrid(cos_x, cos_y)

        lat, lon = cls._compute_latlon_grid(
            (r_orb, r_eq, r_pol),
            (sin_x, sin_y),
            (cos_x, cos_y),
        )

        return lat.astype(float32), (lon + lambda_0).astype(float32)

    @classmethod
    def _calculate_latlon_grid_fast(
        cls, record: Dataset
    ) -> tuple[NDArray[float32], NDArray[float32]]:
        # Harness geodetic grid symmetry from geostationary perspective
        # to reduce the number of computations. Achieve ~24x performance
        # gain compared to the reference implementation in [2].
        projection_info = GOESProjection(record)

        lambda_0 = projection_info.longitude_of_projection_origin

        r_orb = projection_info.orbital_radius
        r_eq = projection_info.semi_major_axis
        r_pol = projection_info.semi_minor_axis

        # Compute only the first quadrant of the grid
        grid_data = GOESABIFixedGridArray(record)

        # pylint: disable=no-member # pylint false positive
        center = grid_data.x.size // 2
        odd_size = bool(grid_data.x.size % 2)
        # pylint: enable=no-member

        # pylint: disable=unsubscriptable-object # pylint false positive
        grid_x = grid_data.x[center:]
        grid_y = grid_x[::-1]
        # pylint: enable=unsubscriptable-object

        sin_x: NDArray[float64] = sin(grid_x)
        cos_x: NDArray[float64] = cos(grid_x)
        sin_y: NDArray[float64] = sin(grid_y)
        cos_y: NDArray[float64] = cos(grid_y)

        sin_x, sin_y = meshgrid(sin_x, sin_y)
        cos_x, cos_y = meshgrid(cos_x, cos_y)

        lat, lon = cls._compute_latlon_grid(
            (r_orb, r_eq, r_pol),
            (sin_x, sin_y),
            (cos_x, cos_y),
        )

        lat = cls._reconstruct_lat_grid(lat, odd_size)
        lon = cls._reconstruct_lon_grid(lon, odd_size)

        return lat.astype(float32), (lon + lambda_0).astype(float32)

    @staticmethod
    def _compute_latlon_grid(
        params: tuple[float64, float64, float64],
        sin_xy: tuple[NDArray[float64], NDArray[float64]],
        cos_xy: tuple[NDArray[float64], NDArray[float64]],
    ) -> tuple[NDArray[float64], NDArray[float64]]:
        # Based on NOAA/NESDIS/STAR Aerosols and Atmospheric Composition
        # Science Team's code found on [2], which is based on the GOES-R
        # Product User Guide (PUG) Volume 5 (L2 products) Section 4.2.8.
        # Retrieved at 2025-02-24.

        r_orb, r_eq, r_pol = params
        sin_x, sin_y = sin_xy
        cos_x, cos_y = cos_xy

        # Equations to calculate latitude and longitude
        a_var = power(sin_x, 2.0) + (
            power(cos_x, 2.0)
            * (
                power(cos_y, 2.0)
                + (((r_eq * r_eq) / (r_pol * r_pol)) * power(sin_y, 2.0))
            )
        )

        b_var = -2.0 * r_orb * cos_x * cos_y
        c_var = (r_orb**2.0) - (r_eq**2.0)
        r_s = (-1.0 * b_var - sqrt((b_var**2) - (4.0 * a_var * c_var))) / (
            2.0 * a_var
        )

        s_x = r_s * cos_x * cos_y
        s_y = -r_s * sin_x
        s_z = r_s * cos_x * sin_y

        abi_lat: NDArray[float64] = rad2deg(
            arctan(
                ((r_eq * r_eq) / (r_pol * r_pol))
                * (s_z / sqrt(((r_orb - s_x) * (r_orb - s_x)) + (s_y * s_y)))
            )
        )
        abi_lon: NDArray[float64] = rad2deg(arctan(s_y / (s_x - r_orb)))

        is_valid = ~(isnan(abi_lat) | isnan(abi_lon))

        abi_lat = where(is_valid, abi_lat, nan)
        abi_lon = where(is_valid, abi_lon, nan)

        return abi_lat, abi_lon

    @staticmethod
    def _reconstruct_lat_grid(
        northeast_grid: NDArray[float64], odd_size: bool
    ) -> NDArray[float64]:
        southeast_grid = (
            -northeast_grid[-2::-1, :]
            if odd_size
            else -northeast_grid[::-1, :]
        )
        east_grid = vstack((northeast_grid, southeast_grid))
        west_grid = east_grid[:, -1:0:-1] if odd_size else east_grid[:, ::-1]
        return hstack((west_grid, east_grid))

    @staticmethod
    def _reconstruct_lon_grid(
        northeast_grid: NDArray[float64], odd_size: bool
    ) -> NDArray[float64]:
        northwest_grid = (
            -northeast_grid[:, -1:0:-1]
            if odd_size
            else -northeast_grid[:, ::-1]
        )
        north_grid = hstack((northwest_grid, northeast_grid))
        south_grid = north_grid[-2::-1, :] if odd_size else north_grid[::-1, :]
        return vstack((north_grid, south_grid))
