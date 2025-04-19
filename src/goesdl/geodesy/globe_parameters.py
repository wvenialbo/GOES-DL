from typing import Protocol

from numpy import float64


class GlobeParameters(Protocol):
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
