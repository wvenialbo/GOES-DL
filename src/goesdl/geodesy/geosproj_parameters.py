from typing import Protocol

from numpy import float64


class GeosProjParameters(Protocol):
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
