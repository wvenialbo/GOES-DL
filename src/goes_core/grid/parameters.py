from numpy import ceil, float64, linspace, pi

from ..array import ArrayFloat64


class GlobeParameters:
    """
    A class to store the globe parameters.

    Attributes
    ----------
    semi_major_axis : float64
        The semi-major axis of the ellipsoid in meters.
    semi_minor_axis : float64
        The semi-minor axis of the ellipsoid in meters.
    inverse_flattening : float64
        The inverse flattening of the ellipsoid.
    """

    semi_major_axis: float64
    semi_minor_axis: float64
    inverse_flattening: float64

    def __init__(
        self,
        semi_major_axis: float64,
        semi_minor_axis: float64,
        inverse_flattening: float64,
    ) -> None:
        """
        Initialize the GlobeParameters object.

        Parameters
        ----------
        semi_major_axis : float64
            The semi-major axis of the ellipsoid in meters.
        semi_minor_axis : float64
            The semi-minor axis of the ellipsoid in meters.
        inverse_flattening : float64
            The inverse flattening of the ellipsoid.
        """
        self.semi_major_axis = semi_major_axis
        self.semi_minor_axis = semi_minor_axis
        self.inverse_flattening = inverse_flattening

    @property
    def flattening(self) -> float64:
        """
        Get the flattening of the globe.

        Returns
        -------
        np.float64
            The flattening of the globe.
        """
        return 1.0 / self.inverse_flattening


class OrbitParameters:
    """
    A class to store the geostationary projection parameters.

    Attributes
    ----------
    longitude_of_projection_origin : float64
        The longitude of the projection origin in East degrees.
    perspective_point_height : float64
        The height of the perspective point in meters.
    sweep_angle_axis : str
        The axis of the sweep angle.
    """

    # Information about the projection
    longitude_of_projection_origin: float64
    perspective_point_height: float64
    sweep_angle_axis: str

    def __init__(
        self,
        longitude_of_projection_origin: float64,
        perspective_point_height: float64,
        sweep_angle_axis: str,
    ) -> None:
        """
        Initialize the GeostationaryParameters object.

        Parameters
        ----------
        longitude_of_projection_origin : float64
            The longitude of the projection origin in East degrees.
        perspective_point_height : float64
            The height of the perspective point in meters.
        sweep_angle_axis : str
            The axis of the sweep angle.
        """
        self.longitude_of_projection_origin = longitude_of_projection_origin
        self.perspective_point_height = perspective_point_height
        self.sweep_angle_axis = sweep_angle_axis


class GeostationaryParameters:
    """
    A class to store the geostationary grid and projection parameters.

    Attributes
    ----------
    orbit : GeostationaryParameters
        The parameters of the geostationary orbit.
    globe : GlobeParameters
        The parameters of the globe.
    x : ArrayFloat64
        The x-coordinate grid in radians.
    y : ArrayFloat64
        The y-coordinate grid in radians.
    """

    # Information about the projection
    orbit: OrbitParameters

    # Information about the globe
    globe: GlobeParameters

    # Information about the fixed grid
    x: ArrayFloat64
    y: ArrayFloat64

    def __init__(
        self,
        orbit: OrbitParameters,
        globe: GlobeParameters,
        xy_grid: tuple[ArrayFloat64, ArrayFloat64],
    ) -> None:
        """
        Initialize the class.

        Parameters
        ----------
        orbit : GeostationaryParameters
            The parameters of the geostationary orbit.
        globe : GlobeParameters
            The parameters of the globe.
        xy_grid : tuple[ArrayFloat64, ArrayFloat64]
            The x and y grid data in radians.
        """
        self.orbit = orbit
        self.globe = globe
        self.x = xy_grid[0]
        self.y = xy_grid[1]

    @property
    def orbital_radius(self) -> float64:
        """
        Calculate the orbital radius of the GOES satellite in meters.

        Returns
        -------
        np.float64
            The orbital radius of the GOES satellite in meters.
        """
        return self.orbit.perspective_point_height + self.globe.semi_major_axis

    @property
    def x_m(self) -> ArrayFloat64:
        """
        Calculate the x-coordinate fixed grid in meters.

        Returns
        -------
        ArrayFloat64
            The x-coordinate fixed grid in meters.
        """
        return self.orbit.perspective_point_height * self.x

    @property
    def y_m(self) -> ArrayFloat64:
        """
        Calculate the y-coordinate fixed grid in meters.

        Returns
        -------
        ArrayFloat64
            The y-coordinate fixed grid in meters.
        """
        return self.orbit.perspective_point_height * self.y


class AeqdProjectionParameters:
    """
    A class to store Azimuthal Equidistant projection parameters.

    Attributes
    ----------
    longitude_of_projection_origin : float64
        The longitude of the projection origin in East degrees.
    latitude_of_projection_origin : float64
        The latitude of the projection origin in North degrees.
    extent_size : tuple[float64, float64, str]
        The size of the extent in the specified unit of measurement:
        - The width of the extent in the specified unit of measurement.
        - The height of the extent in the specified unit of measurement.
        - The unit of measurement; e.g., 'm' for meters, 'km' for
          kilometers, 'arcsec' for arc-seconds, 'arcmin' for arc-
          minutes, or 'deg' for degrees.
    """

    # Information about the projection
    longitude_of_projection_origin: float64
    latitude_of_projection_origin: float64
    extent_size: tuple[float64, float64, str]

    def __init__(
        self,
        longitude_of_projection_origin: float64,
        latitude_of_projection_origin: float64,
        extent_size: tuple[float64, float64, str],
    ) -> None:
        """
        Initialize the class.

        Parameters
        ----------
        longitude_of_projection_origin : float64
            The longitude of the projection origin in East degrees.
        latitude_of_projection_origin : float64
            The latitude of the projection origin in North degrees.
        extent_size : tuple[float64, float64, str]
            The size of the extent in the specified unit of measurement.
            The first element is the width, the second is the height,
            and the third is the unit of measurement; e.g. 'm' for
            meters, 'km' for kilometers, 'arcsec' for arc seconds,
            'arcmin' for arc minutes, or 'deg' for degrees.
        """
        self.longitude_of_projection_origin = longitude_of_projection_origin
        self.latitude_of_projection_origin = latitude_of_projection_origin
        self.extent_size = extent_size

        units = extent_size[2]
        if units not in {"m", "km", "arcsec", "arcmin", "deg"}:
            raise ValueError(
                f"Invalid unit of measurement: {units}. "
                "Valid options are 'm', 'km', 'arcsec', 'arcmin', or 'deg'."
            )


class AzimuthalEquidistantParameters:
    """
    A class to store Azimuthal Equidistant projection parameters.

    Attributes
    ----------
    projection : AeqdProjectionParameters
        The parameters of the Azimuthal Equidistant projection.
    globe : GlobeParameters
        The parameters of the globe.
    x : ArrayFloat64
        The x-coordinate grid in meters.
    y : ArrayFloat64
        The y-coordinate grid in meters.
    """

    # Information about the projection
    projection: AeqdProjectionParameters

    # Information about the globe
    globe: GlobeParameters

    # Information about the fixed grid
    x: ArrayFloat64
    y: ArrayFloat64

    def __init__(
        self,
        projection: AeqdProjectionParameters,
        globe: GlobeParameters,
        xy_grid: tuple[ArrayFloat64, ArrayFloat64],
    ) -> None:
        """
        Initialize the class.

        Parameters
        ----------
        projection : AeqdProjectionParameters
            The parameters of the Azimuthal Equidistant projection.
        globe : GlobeParameters
            The parameters of the globe.
        xy_grid : tuple[ArrayFloat64, ArrayFloat64]
            The x and y grid data in meters.
        """
        self.projection = projection
        self.globe = globe
        self.x = xy_grid[0]
        self.y = xy_grid[1]

    @classmethod
    def create(
        cls,
        projection: AeqdProjectionParameters,
        globe: GlobeParameters,
        resolution: float64,
    ) -> "AzimuthalEquidistantParameters":
        horizontal_extent_m, vertical_extent_m = cls._get_size(
            projection, globe
        )

        width_px: float64 = ceil(horizontal_extent_m / resolution)
        height_px: float64 = ceil(vertical_extent_m / resolution)

        n_cols = int(width_px)
        n_rows = int(height_px)

        x_m = linspace(
            -horizontal_extent_m / 2.0,
            horizontal_extent_m / 2.0,
            n_cols,
            dtype=float64,
        )
        y_m = linspace(
            vertical_extent_m / 2.0,
            -vertical_extent_m / 2.0,
            n_rows,
            dtype=float64,
        )

        return AzimuthalEquidistantParameters(
            projection,
            globe,
            (x_m, y_m),
        )

    @classmethod
    def _get_size(
        cls, projection: AeqdProjectionParameters, globe: GlobeParameters
    ) -> tuple[float64, float64]:
        """
        Calculate the size of the projection.

        Parameters
        ----------
        projection : AeqdProjectionParameters
            The parameters of the Azimuthal Equidistant projection.
        resolution : float64
            The resolution in meters.

        Returns
        -------
        tuple[float64, float64]
            The width and height of the projection in kilometers.
        """
        width, height = projection.extent_size[:2]
        units = projection.extent_size[2]

        if units in {"arcsec", "arcmin", "deg"}:
            return cls._get_size_from_angle(
                width, height, units, globe.semi_major_axis
            )

        return cls._get_size_from_length(width, height, units)

    @staticmethod
    def _get_size_from_length(
        width: float64, height: float64, units: str
    ) -> tuple[float64, float64]:
        """
        Calculate the size of the projection from lengths.

        Parameters
        ----------
        width : float64
            The width of the projection in the specified unit of
            measurement.
        height : float64
            The height of the projection in the specified unit of
            measurement.
        units : str
            The unit of measurement for the width and height. It can be
            'm', or 'km'.

        Returns
        -------
        tuple[float64, float64]
            The width and height of the projection in meters.
        """
        if units == "km":
            width *= 1000.0
            height *= 1000.0

        return width, height

    @staticmethod
    def _get_size_from_angle(
        width: float64, height: float64, units: str, semi_major_axis: float64
    ) -> tuple[float64, float64]:
        """
        Calculate the size of the projection from angles.

        Parameters
        ----------
        width : float64
            The width of the projection in the specified unit of
            measurement.
        height : float64
            The height of the projection in the specified unit of
            measurement.
        units : str
            The unit of measurement for the width and height. It can be
            'arcsec', 'arcmin', or 'deg'.
        semi_major_axis : float64
            The semi-major axis of the globe in meters.

        Returns
        -------
        tuple[float64, float64]
            The width and height of the projection in meters.
        """
        deg_to_m = pi * semi_major_axis / 180.0

        if units == "arcsec":
            width /= 3600.0
            height /= 3600.0
        elif units == "arcmin":
            width /= 60.0
            height /= 60.0

        return width * deg_to_m, height * deg_to_m

    @property
    def x_km(self) -> ArrayFloat64:
        """
        Calculate the x-coordinate fixed grid in kilometers.

        Returns
        -------
        ArrayFloat64
            The x-coordinate fixed grid in kilometers.
        """
        return self.x / 1000.0

    @property
    def y_km(self) -> ArrayFloat64:
        """
        Calculate the y-coordinate fixed grid in kilometers.

        Returns
        -------
        ArrayFloat64
            The y-coordinate fixed grid in kilometers.
        """
        return self.y / 1000.0
