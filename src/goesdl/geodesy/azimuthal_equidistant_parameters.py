from typing import cast

from numpy import ceil, float64, linspace, pi

from ..utils.array import ArrayFloat64
from .aeqdproj_parameters import AeqdProjParameters
from .globe_parameters import GlobeParameters


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
    projection: AeqdProjParameters

    # Information about the globe
    globe: GlobeParameters

    # Information about the fixed grid
    x: ArrayFloat64
    y: ArrayFloat64

    def __init__(
        self,
        projection: AeqdProjParameters,
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
        projection: AeqdProjParameters,
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
        cls, projection: AeqdProjParameters, globe: GlobeParameters
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
    def extent(self) -> tuple[float64, float64, float64, float64]:
        """
        Calculate the extent of the projection.

        Returns
        -------
        tuple[float64, float64, float64, float64]
            The extent of the projection in kilometers.
            - The minimum x-coordinate.
            - The maximum x-coordinate.
            - The minimum y-coordinate.
            - The maximum y-coordinate.
        """
        return (
            self.x[0] / 1000.0,
            self.x[-2] / 1000.0,
            self.y[0] / 1000.0,
            self.y[-1] / 1000.0,
        )

    @property
    def x_km(self) -> ArrayFloat64:
        """
        Calculate the x-coordinate fixed grid in kilometers.

        Returns
        -------
        ArrayFloat64
            The x-coordinate fixed grid in kilometers.
        """
        return cast(ArrayFloat64, self.x / 1000.0)

    @property
    def y_km(self) -> ArrayFloat64:
        """
        Calculate the y-coordinate fixed grid in kilometers.

        Returns
        -------
        ArrayFloat64
            The y-coordinate fixed grid in kilometers.
        """
        return cast(ArrayFloat64, self.y / 1000.0)
