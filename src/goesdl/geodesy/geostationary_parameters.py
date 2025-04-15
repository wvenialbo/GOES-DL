from numpy import float64

from ..utils.array import ArrayFloat64
from .geosproj_parameters import GeosProjParameters
from .globe_parameters import GlobeParameters


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
    orbit: GeosProjParameters

    # Information about the globe
    globe: GlobeParameters

    # Information about the fixed grid
    x: ArrayFloat64
    y: ArrayFloat64

    def __init__(
        self,
        orbit: GeosProjParameters,
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
