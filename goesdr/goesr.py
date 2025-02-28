"""
This module provides classes to extract and represent information from
GOES satellite netCDF data files. The classes dynamically set attributes
based on the annotations defined in the class and the corresponding
attributes or variables present in the provided netCDF data object.
"""

from typing import cast

from netCDF4 import Dataset  # pylint: disable=no-name-in-module
from numpy import bool_, float32, float64, int8, int16, int32, meshgrid, uint16
from numpy.typing import NDArray

from .datarecord import DataRecord
from .fields import (
    VariableType,
    computed,
    dimension,
    make_variable,
    scalar,
    variable,
)
from .fragment import netcdf_fragment

imager_proj = make_variable("goes_imager_projection")


@netcdf_fragment
class GOESOrbitGeometry:
    """
    Represent GOES-R series satellite orbit geometry information.

    Attributes
    ----------
    longitude_of_projection_origin : np.float64
        The longitude of the ideal satellite sub-point.
    perspective_point_height : np.float64
        The height of the perspective point, or the height above the
        Earth's surface the ideal satellite sub-point.
    sweep_angle_axis : str
        The sweep angle axis.
    """

    # Information about the projection
    longitude_of_projection_origin: float64 = imager_proj()
    perspective_point_height: float64 = imager_proj()
    sweep_angle_axis: str = imager_proj()


@netcdf_fragment
class GOESGlobe:
    """
    Represent GOES-R series satellite globe definition.

    Attributes
    ----------
    semi_major_axis : np.float64
        The semi-major axis of the globe.
    semi_minor_axis : np.float64
        The semi-minor axis of the globe.
    inverse_flattening : np.float64
        The inverse flattening of the globe.
    """

    # Information about the globe
    semi_major_axis: float64 = imager_proj()
    semi_minor_axis: float64 = imager_proj()
    inverse_flattening: float64 = imager_proj()


class GOESProjection(GOESOrbitGeometry, GOESGlobe):
    """
    Represent GOES-R series satellite projection information.

    Properties
    ----------
    orbital_radius : np.float64
        The orbital radius of the GOES satellite.
    """

    @property
    def orbital_radius(self) -> float64:
        """
        Calculate the orbital radius of the GOES satellite.

        Returns
        -------
        np.float64
            The orbital radius of the GOES satellite.
        """
        return self.perspective_point_height + self.semi_major_axis


@netcdf_fragment
class GOESABIFixedGrid:
    """
    Represent GOES-R series satellite ABI fixed grid projection data.

    The GOES Imager Projection, also called the ABI Fixed Grid, is the
    projection information included in all ABI Level 1b radiance data
    files and most ABI Level 2 derived product data files. It is a map
    projection based on the geostationary viewing perspective of the
    GOES-East or GOES-West satellite.

    Attributes
    ----------
    x_coordinate_1d : NDArray[float32]
        1D array of E/W scanning angles in radians.
    y_coordinate_1d : NDArray[float32]
        1D array of N/S elevation angles in radians.
    x_coordinate_2d : NDArray[float32]
        2D array of E/W scanning angles in radians.
    y_coordinate_2d : NDArray[float32]
        2D array of N/S elevation angles in radians.
    """

    x_coordinate_1d: NDArray[float32] = variable("x")
    y_coordinate_1d: NDArray[float32] = variable("y")
    x_coordinate_2d: NDArray[float32] = computed()
    y_coordinate_2d: NDArray[float32] = computed()

    def __post_init__(self, _: Dataset) -> None:
        """
        Initialize the GOESABIFixedGrid object.

        Parameters
        ----------
        record : Dataset
            The netCDF dataset containing the GOES ABI fixed grid
            projection variables.
        """
        # Create 2D coordinate matrices from 1D coordinate vectors
        self.x_coordinate_2d, self.y_coordinate_2d = meshgrid(
            self.x_coordinate_1d, self.y_coordinate_1d
        )


cmip: VariableType = make_variable("CMI", array=True)


@netcdf_fragment
class GOESImage:
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


@netcdf_fragment
class GOESImageMetadata:
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


@netcdf_fragment
class GOESDatasetInfo:
    """
    Hold GOES dataset metadata information.

    Attributes
    ----------
    institution : str
        The institution responsible for the dataset.
    project : str
        The project under which the dataset was created.
    production_site : str
        The site where the dataset was produced.
    production_environment : str
        The environment where the dataset was produced.
    spatial_resolution : str
        The spatial resolution of the dataset.
    orbital_slot : str
        The orbital slot of the satellite.
    platform_ID : str
        The platform identifier of the satellite.
    instrument_type : str
        The type of instrument used to collect the data.
    scene_id : str
        The identifier for the scene.
    instrument_ID : str
        The identifier for the instrument.
    dataset_name : str
        The name of the dataset.
    title : str
        The title of the dataset.
    summary : str
        A summary of the dataset.
    keywords : str
        Keywords associated with the dataset.
    keywords_vocabulary : str
        The vocabulary used for the keywords.
    license : str
        The license under which the dataset is released.
    processing_level : str
        The processing level of the dataset.
    cdm_data_type : str
        The CDM data type of the dataset.
    date_created : str
        The date the dataset was created.
    time_coverage_start : str
        The start time of the data coverage.
    time_coverage_end : str
        The end time of the data coverage.
    timeline_id : str
        The identifier for the timeline.
    production_data_source : str
        The data source used to produce the dataset.
    y : int
        The number of rows in the dataset.
    x : int
        The number of columns in the dataset.
    """

    institution: str
    project: str
    production_site: str
    production_environment: str
    spatial_resolution: str
    orbital_slot: str
    platform_ID: str  # NOSONAR
    instrument_type: str
    scene_id: str
    instrument_ID: str  # NOSONAR
    dataset_name: str
    title: str
    summary: str
    keywords: str
    keywords_vocabulary: str
    license: str
    processing_level: str
    cdm_data_type: str
    date_created: str
    time_coverage_start: str
    time_coverage_end: str
    timeline_id: str
    production_data_source: str
    y: int = dimension()
    x: int = dimension()


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

    data: NDArray[float32]
    mask: NDArray[bool_]
    fill_value: float32


def _latlon_data(name: str, record: Dataset) -> GOESLatLonGridData:
    latlon: VariableType = make_variable(name, array=True)

    class _GOESLatLonGridData(DataRecord):
        data: NDArray[float32] = latlon()
        mask: NDArray[bool_] = latlon()
        fill_value: float32 = latlon()

    _GOESLatLonGridData.__module__ = GOESLatLonGridData.__module__
    _GOESLatLonGridData.__name__ = GOESLatLonGridData.__name__
    _GOESLatLonGridData.__qualname__ = GOESLatLonGridData.__qualname__

    data = _GOESLatLonGridData(record)

    return cast(GOESLatLonGridData, data)


class GOESLatLonGrid:
    """
    Represent GOES satellite precomputed latitude and longitude data.

    Note
    ----
    For information on getting the precomputed latitude and longitude
    grid dataset, see
    https://www.star.nesdis.noaa.gov/atmospheric-composition-training/satellite_data_goes_imager_projection.php.

    Attributes
    ----------
    latitude : GOESLatLonGridData
        The latitude metadata.
    longitude : GOESLatLonGridData
        The longitude metadata.
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

    def __str__(self) -> str:
        # Returns a string representation of the DataRecord object.
        lines = [str(self.__class__)]
        lines += [f"    {line}" for line in str(self.latitude).split("\n")]
        lines += [f"    {line}" for line in str(self.longitude).split("\n")]
        return "\n".join(lines)


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

    class _GOESLatLonGridMetadata(DataRecord):
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


class GOESLatLonGridMetadata:
    """
    Represent a GOES satellite latitude and longitude metadata.

    Attributes
    ----------
    latitude : GOESLatLonMetadataType
        The latitude metadata.
    longitude : GOESLatLonMetadataType
        The longitude metadata.
    """

    def __init__(self, record: Dataset) -> None:
        self.latitude = _latlon_metadata("latitude", record)
        self.longitude = _latlon_metadata("longitude", record)

    def __str__(self) -> str:
        # Returns a string representation of the DataRecord object.
        lines = [str(self.__class__)]
        lines += [f"    {line}" for line in str(self.latitude).split("\n")]
        lines += [f"    {line}" for line in str(self.longitude).split("\n")]
        return "\n".join(lines)


@netcdf_fragment
class GOESLatLonGridInfo:
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


class GOESGeodeticGrid:
    """
    Represent latitude and longitude grid data computed on the fly.

    Calculate the latitude and longitude grid arrays on the fly from the
    GOES Imager Projection information in the ABI Level 2 file.

    Attributes
    ----------
    latitude : GOESLatLonGridData
        The latitude metadata.
    longitude : GOESLatLonGridData
        The longitude metadata.
    """

    latitude: GOESLatLonGridData
    longitude: GOESLatLonGridData
