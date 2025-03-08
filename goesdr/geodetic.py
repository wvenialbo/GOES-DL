"""
GOES precomputed latitude and longitude grids data extraction.

This module provides classes to extract and represent latitude and
longitude grids information from GOES satellite netCDF data files.

Classes
-------
GOESGeodeticGrid
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

from re import match
from typing import Any, cast

from netCDF4 import Dataset  # pylint: disable=no-name-in-module
from numpy import errstate, float32, nan
from numpy.ma import masked_invalid

from .array import ArrayBool, ArrayFloat32, ArrayFloat64, MaskedFloat32
from .grid import (
    ProjectionParameters,
    calculate_latlon_grid_cartopy,
    calculate_latlon_grid_goesdr,
    calculate_latlon_grid_pyproj,
    calculate_pixel_edges,
)
from .netcdf import DatasetView, HasStrHelp, dimension, variable
from .projection import GOESProjection


class GOESLatLonGridData:
    """
    Represent GOES satellite latitude or longitude grid data.

    Attributes
    ----------
    data : ArrayFloat32
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

    data: ArrayFloat32
    mask: ArrayBool
    fill_value: float32


def _latlon_data(
    name: str, record: Dataset, step: tuple[int, int] | None
) -> GOESLatLonGridData:
    latlon = variable(name)

    def _subsample(x: Any) -> Any:
        return x[:] if step is None else x[:: step[0], :: step[1]]

    class _GOESLatLonGridData(DatasetView):
        data: ArrayFloat32 = latlon.data(filter=_subsample)
        mask: ArrayBool = latlon.mask(filter=_subsample)
        fill_value: float32 = latlon.fill_value()

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
        self.latitude = _latlon_data("latitude", record, None)
        self.longitude = _latlon_data("longitude", record, None)


class GOESLatLonGridMetadataType:
    """
    Represent a GOES satellite latitude or longitude metadata.

    Attributes
    ----------
    long_name : str
        A descriptive name for the variable.
    valid_range : ArrayFloat64
        The valid range of values for the variable.
    units : str
        The units of measurement for the variable.
    comment : str
        Additional comments or information about the variable.
    """

    long_name: str
    valid_range: ArrayFloat64
    units: str
    comment: str


def _latlon_metadata(name: str, record: Dataset) -> GOESLatLonGridMetadataType:
    latlon = variable(name)

    class _GOESLatLonGridMetadata(DatasetView):
        long_name: str = latlon.attribute()
        valid_range: ArrayFloat64 = latlon.attribute()
        units: str = latlon.attribute()
        comment: str = latlon.attribute()

    _GOESLatLonGridMetadata.__module__ = GOESLatLonGridMetadataType.__module__
    _GOESLatLonGridMetadata.__name__ = GOESLatLonGridMetadataType.__name__
    _GOESLatLonGridMetadata.__qualname__ = (
        GOESLatLonGridMetadataType.__qualname__
    )

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


class GOESLatLonGridInfo(DatasetView):
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
    rows: int = dimension.size()
    columns: int = dimension.size()


FILL_VALUE = -999.99


class GOESGeodeticGrid(HasStrHelp):
    """
    Hold GOES satellite geodetic grids data.

    Notes
    -----
    For information on GOES Imager Projection and GOES orbit geometry,
    see [1]_ and Section 4.2. of [2]_. GOES-R use the Geodetic Reference
    System 1980 (GRS80).

    Attributes
    ----------
    latitude : GOESLatLonGridData
        The GRS80 latitude grid data.
    longitude : GOESLatLonGridData
        The GRS80 longitude grid data.

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

    def __init__(
        self, latitude: GOESLatLonGridData, logitude: GOESLatLonGridData
    ) -> None:
        """
        Initialize a GOESGrid object from a precomputed netCDF dataset.

        Parameters
        ----------
        latitude : GOESLatLonGridData
            The GRS80 latitude grid data.
        longitude : GOESLatLonGridData
            The GRS80 longitude grid data
        """
        self.latitude = latitude
        self.longitude = logitude

    @classmethod
    def calculate(
        cls,
        record: Dataset,
        algorithm: str = "goesdr",
        step: int | tuple[int, int] = 1,
    ) -> "GOESGeodeticGrid":
        """
        Compute the geodetic grids and initialize a GOESGrid object.

        Calculate the latitude and longitude grid arrays on the fly from
        the GOES Imager Projection information in ABI Level 2 files.

        Notes
        -----
        For information on GOES Imager Projection and GOES orbit
        geometry, see [1]_ and Section 4.2. of [3]_. For a Python
        demonstration on calculating latitude and longitude from GOES
        Imager Projection information, see [2]_. The code snippet in
        this class is an optimized version based on the code from [2]_.

        Parameters
        ----------
        record : Dataset
            The netCDF dataset containing ABI Level 2 data.
        algorithm : str, optional
            The algorithm to use to calculate the latitude and longitude
            grid data. Choose 'cartopy', 'goesdr', or 'pyproj'.
            'cartopy' or 'pyproj' requires the respective Python package
            to be installed.  'goesdr' is the default algorithm and does
            not require any additional packages.
        step : int or tuple[int, int], optional
            The step size to subsample the latitude and longitude grid
            data. If an integer is provided, the step size is the same
            for both rows and columns. If a tuple is provided, the first
            value is the step size for grid rows and the second value is
            the step size for grid columns. The default is 1.

        Returns
        -------
        GOESLatLonGrid
            The latitude and longitude grid data.

        References
        ----------
        .. [1] STAR Atmospheric Composition Product Training, "GOES
            Imager Projection (ABI Fixed Grid)", NOAA/NESDIS/STAR, 2024.
            https://www.star.nesdis.noaa.gov/atmospheric-composition-training/satellite_data_goes_imager_projection.php.
        .. [2] Aerosols and Atmospheric Composition Science Team,
            "Python Short Demo: Calculate Latitude and Longitude from
            GOES Imager Projection (ABI Fixed Grid) Information",
            NOAA/NESDIS/STAR, 2024.
            https://www.star.nesdis.noaa.gov/atmospheric-composition-training/python_abi_lat_lon.php
        .. [3] GOES-R, " GOES-R Series Product Definition and User’s
            Guide (PUG), Volume 5: Level 2+ Products", Version 2.4,
            NASA/NOAA/NESDIS, 2022.
            https://www.ospo.noaa.gov/Organization/Documents/PUG/GS%20Series%20416-R-PUG-L2%20Plus-0349%20Vol%205%20v2.4.pdf
        """
        algorithm, corners = cls._parse_algorithm(algorithm)

        step = cls._parse_step(step)

        abi_lat, abi_lon = cls._initialize_calculated(
            record, algorithm, corners, step
        )

        return GOESGeodeticGrid(abi_lat, abi_lon)

    @staticmethod
    def from_file(
        record: Dataset, step: int | tuple[int, int] | None = None
    ) -> "GOESGeodeticGrid":
        """
        Initialize a GOESGrid object from a precomputed netCDF dataset.

        Notes
        -----
        For information on GOES Imager Projection and GOES orbit
        geometry, see [1]_ and Section 4.2. of [2]_. For information on
        getting the precomputed latitude and longitude grids dataset,
        see [1]_.

        Parameters
        ----------
        record : Dataset
            The netCDF dataset containing precomputed latitude and
            longitude grid data.
        step : int or tuple[int, int], optional
            The step size to subsample the latitude and longitude grid
            data. If an integer is provided, the step size is the same
            for both rows and columns. If a tuple is provided, the first
            value is the step size for grid rows and the second value is
            the step size for grid columns. The default is None.

        Returns
        -------
        GOESLatLonGrid
            The latitude and longitude grid data.

        References
        ----------
        .. [1] STAR Atmospheric Composition Product Training, "GOES
            Imager Projection (ABI Fixed Grid)", NOAA/NESDIS/STAR, 2024.
            https://www.star.nesdis.noaa.gov/atmospheric-composition-training/satellite_data_goes_imager_projection.php.
        .. [2] GOES-R, " GOES-R Series Product Definition and User’s
            Guide (PUG), Volume 5: Level 2+ Products", Version 2.4,
            NASA/NOAA/NESDIS, 2022.
            https://www.ospo.noaa.gov/Organization/Documents/PUG/GS%20Series%20416-R-PUG-L2%20Plus-0349%20Vol%205%20v2.4.pdf
        """
        if isinstance(step, int):
            step = (step, step)

        abi_lat = _latlon_data("latitude", record, step)
        abi_lon = _latlon_data("longitude", record, step)

        abi_lat.data[abi_lat.mask] = nan
        abi_lon.data[abi_lon.mask] = nan

        return GOESGeodeticGrid(abi_lat, abi_lon)

    @classmethod
    def _initialize_calculated(
        cls,
        record: Dataset,
        algorithm: str,
        corners: bool,
        step: tuple[int, int],
    ) -> tuple[GOESLatLonGridData, GOESLatLonGridData]:
        projection_info = GOESProjection(record)

        if corners:
            x_r = calculate_pixel_edges(projection_info.x)
            y_r = calculate_pixel_edges(projection_info.y)
        else:
            x_r = projection_info.x
            y_r = projection_info.y

        if step[0] > 1:
            y_r = y_r[:: step[0]]

        if step[1] > 1:
            x_r = x_r[:: step[1]]

        orbit_parameters = (
            projection_info.longitude_of_projection_origin,
            projection_info.perspective_point_height,
            projection_info.sweep_angle_axis,
        )
        globe_parameters = (
            projection_info.semi_major_axis,
            projection_info.semi_minor_axis,
            projection_info.inverse_flattening,
        )
        xy_grid = (x_r, y_r)

        parameters = ProjectionParameters(
            orbit_parameters, globe_parameters, xy_grid
        )

        lat, lon = cls._calculate_latlon_grid(parameters, algorithm)

        abi_lat = GOESLatLonGridData(lat)
        abi_lon = GOESLatLonGridData(lon)

        return abi_lat, abi_lon

    @staticmethod
    def _calculate_latlon_grid(
        parameters: ProjectionParameters,
        algorithm: str,
    ) -> tuple[MaskedFloat32, MaskedFloat32]:
        # Ignore numpy errors for `sqrt` of negative number; reference
        # [2] states that this "occurs for GOES-16 ABI CONUS sector
        # data", however I found it also occurs for Full Disk sector.
        with errstate(invalid="ignore"):
            if algorithm == "goesdr":
                lat, lon = calculate_latlon_grid_goesdr(parameters)
            elif algorithm == "pyproj":
                lat, lon = calculate_latlon_grid_pyproj(parameters)
            elif algorithm == "cartopy":
                lat, lon = calculate_latlon_grid_cartopy(parameters)
            else:
                raise ValueError(
                    f"Invalid algorithm '{algorithm}'. Expected pattern: "
                    "'<algorithm>' or '<algorithm>[<option>]'. "
                    "Choose 'precomputed', 'noaa', 'opti' (default), "
                    "'pyproj', or 'cartopy' for '<algorithm>'. Choose "
                    "'center' (default) or 'corner' for '<option>'. "
                    "'precomputed' cannot be used with options."
                )

        latitude: MaskedFloat32 = masked_invalid(lat)  # type: ignore
        longitude: MaskedFloat32 = masked_invalid(lon)  # type: ignore

        latitude.fill_value = FILL_VALUE
        longitude.fill_value = FILL_VALUE

        return latitude, longitude

    @staticmethod
    def _parse_algorithm(algorithm: str) -> tuple[str, bool]:
        pattern = r"^(\w+)(?:\[(\w+)\])?$"
        match_ = match(pattern, algorithm)

        if not match_:
            raise ValueError(
                f"Invalid algorithm '{algorithm}'. Expected pattern: "
                "'<algorithm>' or '<algorithm>[<option>]'. "
                "Choose 'cartopy', 'goesdr' (default), or 'pyproj' for "
                "'<algorithm>'. Choose 'center' (default) or 'corner' "
                "for '<option>'."
            )

        name = match_[1]

        if name not in {"cartopy", "goesdr", "pyproj"}:
            raise ValueError(
                f"Invalid algorithm '{name}'. Choose 'cartopy', 'goesdr', "
                "or 'pyproj'."
            )

        option = match_[2]

        if option not in {None, "center", "corner"}:
            raise ValueError(
                f"Invalid option '{option}'. Choose 'center' or 'corner'."
            )

        corner: bool = option == "corner"

        return name, corner

    @staticmethod
    def _parse_step(step: int | tuple[int, int]) -> tuple[int, int]:
        if isinstance(step, int):
            step = (step, step)

        if step[0] <= 0 or step[1] <= 0:
            raise ValueError(f"Step size must be greater than 0, got {step}.")

        return step
