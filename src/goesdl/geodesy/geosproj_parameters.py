from numpy import float64


class GeosProjParameters:
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
