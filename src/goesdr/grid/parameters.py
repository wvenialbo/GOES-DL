from numpy import float64

from ..array import ArrayFloat64


class ProjectionParameters:
    """
    A class to store the projection parameters.

    Attributes
    ----------
    longitude_of_projection_origin : float64
        The longitude of the projection origin in East degrees.
    perspective_point_height : float64
        The height of the perspective point in meters.
    sweep_angle_axis : str
        The axis of the sweep angle.
    semi_major_axis : float64
        The semi-major axis of the globe in meters.
    semi_minor_axis : float64
        The semi-minor axis of the globe in meters.
    inverse_flattening : float64
        The inverse flattening of the globe.
    x : ArrayFloat64
        The x-coordinate grid in radians.
    y : ArrayFloat64
        The y-coordinate grid in radians.
    """

    # Information about the projection
    longitude_of_projection_origin: float64
    perspective_point_height: float64
    sweep_angle_axis: str

    # Information about the globe
    semi_major_axis: float64
    semi_minor_axis: float64
    inverse_flattening: float64

    # Information about the fixed grid
    x: ArrayFloat64
    y: ArrayFloat64

    def __init__(
        self,
        orbit_parameters: tuple[float64, float64, str],
        globe_parameters: tuple[float64, float64, float64],
        xy_grid: tuple[ArrayFloat64, ArrayFloat64],
    ) -> None:
        """
        Initialize the class.

        Parameters
        ----------
        orbit_parameters : tuple[float64, float64, str]
            The parameters of the orbit geometry and satellite attitude:
            - The longitude of the projection origin in East degrees.
            - The height of the perspective point in meters.
            - The axis of the sweep.
        globe_parameters : tuple[float64, float64, float64]
            The parameters of the reference ellipsoid:
            - The semi-major axis of the globe in meters.
            - The semi-minor axis of the globe in meters.
            - The inverse flattening of the globe.
        xy_grid : tuple[ArrayFloat64, ArrayFloat64]
            The x and y grid data.
        """
        self.longitude_of_projection_origin = orbit_parameters[0]
        self.perspective_point_height = orbit_parameters[1]
        self.sweep_angle_axis = orbit_parameters[2]
        self.semi_major_axis = globe_parameters[0]
        self.semi_minor_axis = globe_parameters[1]
        self.inverse_flattening = globe_parameters[2]
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
        return self.perspective_point_height + self.semi_major_axis

    @property
    def x_m(self) -> ArrayFloat64:
        """
        Calculate the x-coordinate fixed grid in meters.

        Returns
        -------
        ArrayFloat64
            The x-coordinate fixed grid in meters.
        """
        return self.perspective_point_height * self.x

    @property
    def y_m(self) -> ArrayFloat64:
        """
        Calculate the y-coordinate fixed grid in meters.

        Returns
        -------
        ArrayFloat64
            The y-coordinate fixed grid in meters.
        """
        return self.perspective_point_height * self.y
