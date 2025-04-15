from numpy import float64


class AeqdProjParameters:
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
