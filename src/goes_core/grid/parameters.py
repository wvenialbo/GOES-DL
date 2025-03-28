from numpy import float64

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
            The x and y grid data.
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
