from numpy import float64


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
