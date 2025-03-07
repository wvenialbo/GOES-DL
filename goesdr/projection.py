"""
GOES Imager Projection data extraction.

This module provides classes to extract and represent GOES Imager
Projection information from GOES satellite netCDF data files.

Classes
-------
GOESOrbitGeometry
    Represent GOES-R series satellite orbit geometry information.
GOESGlobe
    Represent GOES-R series satellite globe definition.
GOESProjection
    Represent GOES-R series satellite projection information.
GOESABIFixedGridArray
    Represent GOES-R series satellite ABI Fixed Grid projection data.
GOESABIFixedGrid
    Represent GOES-R series satellite ABI Fixed Grid projection data.
"""

from netCDF4 import Dataset  # pylint: disable=no-name-in-module
from numpy import float32, float64, meshgrid
from numpy.typing import NDArray

from .netcdf import DatasetView, computed, data, variable

imager_proj = variable("goes_imager_projection")


class GOESOrbitGeometry(DatasetView):
    """
    Represent GOES-R series satellite orbit geometry information.

    Note
    ----
    For information on GOES orbit geometry, see [1]_ and Section 4.2. of
    [2]_

    Attributes
    ----------
    longitude_of_projection_origin : np.float64
        The longitude of the ideal satellite sub-point, in East degrees.
    perspective_point_height : np.float64
        The height of the perspective point, or the height above the
        Earth's surface the ideal satellite sub-point, in meters.
    sweep_angle_axis : str
        The sweep angle axis.

    References
    ----------
    .. [1] STAR Atmospheric Composition Product Training, "GOES Imager
        Projection (ABI Fixed Grid)", NOAA/NESDIS/STAR, 2024.
        https://www.star.nesdis.noaa.gov/atmospheric-composition-training/satellite_data_goes_imager_projection.php.
    .. [2] GOES-R, " GOES-R Series Product Definition and User’s Guide
        (PUG), Volume 5: Level 2+ Products", Version 2.4,
        NASA/NOAA/NESDIS, 2022.
        https://www.ospo.noaa.gov/Organization/Documents/PUG/GS%20Series%20416-R-PUG-L2%20Plus-0349%20Vol%205%20v2.4.pdf
    """

    # Information about the projection
    longitude_of_projection_origin: float64 = imager_proj.attribute()
    perspective_point_height: float64 = imager_proj.attribute()
    sweep_angle_axis: str = imager_proj.attribute()


class GOESGlobe(DatasetView):
    """
    Represent GOES-R series satellite globe definition.

    Note
    ----
    For information on GOES orbit geometry and Earth globe definition,
    see [1]_ and Section 4.2. of [2]_

    Attributes
    ----------
    semi_major_axis : np.float64
        The semi-major axis of the globe.
    semi_minor_axis : np.float64
        The semi-minor axis of the globe.
    inverse_flattening : np.float64
        The inverse flattening of the globe.

    References
    ----------
    .. [1] STAR Atmospheric Composition Product Training, "GOES Imager
        Projection (ABI Fixed Grid)", NOAA/NESDIS/STAR, 2024.
        https://www.star.nesdis.noaa.gov/atmospheric-composition-training/satellite_data_goes_imager_projection.php.
    .. [2] GOES-R, " GOES-R Series Product Definition and User’s Guide
        (PUG), Volume 5: Level 2+ Products", Version 2.4,
        NASA/NOAA/NESDIS, 2022.
        https://www.ospo.noaa.gov/Organization/Documents/PUG/GS%20Series%20416-R-PUG-L2%20Plus-0349%20Vol%205%20v2.4.pdf
    """

    # Information about the globe
    semi_major_axis: float64 = imager_proj.attribute()
    semi_minor_axis: float64 = imager_proj.attribute()
    inverse_flattening: float64 = imager_proj.attribute()


class GOESProjection(GOESOrbitGeometry, GOESGlobe):
    """
    Represent GOES-R series satellite projection information.

    The GOES Imager Projection, also called ABI Fixed Grid Projection,
    is a map projection relative to the GOES satellite point of view.
    Units: latitude in °N (°S < 0), longitude in °E (°W < 0)

    Note
    ----
    For information on GOES Imager Projection, see [1]_ and Section
    4.2.8 of [2]_

    Properties
    ----------
    orbital_radius : np.float64
        The orbital radius of the GOES satellite.

    References
    ----------
    .. [1] STAR Atmospheric Composition Product Training, "GOES Imager
        Projection (ABI Fixed Grid)", NOAA/NESDIS/STAR, 2024.
        https://www.star.nesdis.noaa.gov/atmospheric-composition-training/satellite_data_goes_imager_projection.php.
    .. [2] GOES-R, " GOES-R Series Product Definition and User’s Guide
        (PUG), Volume 5: Level 2+ Products", Version 2.4,
        NASA/NOAA/NESDIS, 2022.
        https://www.ospo.noaa.gov/Organization/Documents/PUG/GS%20Series%20416-R-PUG-L2%20Plus-0349%20Vol%205%20v2.4.pdf
    """

    @property
    def orbital_radius(self) -> float64:
        """
        Calculate the orbital radius of the GOES satellite.

        Returns
        -------
        np.float64
            The orbital radius of the GOES satellite.
        """
        return self.perspective_point_height + self.semi_major_axis


def to_float64(array: NDArray[float32]) -> NDArray[float64]:
    """
    Convert a float32 array to a float64 array.

    Parameters
    ----------
    array : NDArray[float32]
        The float32 array to convert.

    Returns
    -------
    NDArray[float64]
        The float64 array.
    """
    return array.astype(float64)


class GOESABIFixedGridArray(DatasetView):
    """
    Represent GOES-R series satellite ABI Fixed Grid projection data.

    The GOES Imager Projection, also called the ABI Fixed Grid, is the
    projection information included in all ABI Level 1b radiance data
    files and most ABI Level 2 derived product data files. It is a map
    projection based on the geostationary viewing perspective of the
    GOES-East or GOES-West satellite.

    Notes
    -----
    For information on GOES Imager Projection and GOES orbit geometry,
    see [1]_ and Section 4.2. of [2]_

    Attributes
    ----------
    x_coordinate_1d : NDArray[float32]
        1D array of E/W scanning angles in radians.
    y_coordinate_1d : NDArray[float32]
        1D array of N/S elevation angles in radians.

    References
    ----------
    .. [1] STAR Atmospheric Composition Product Training, "GOES Imager
        Projection (ABI Fixed Grid)", NOAA/NESDIS/STAR, 2024.
        https://www.star.nesdis.noaa.gov/atmospheric-composition-training/satellite_data_goes_imager_projection.php.
    .. [2] GOES-R, " GOES-R Series Product Definition and User’s Guide
        (PUG), Volume 5: Level 2+ Products", Version 2.4,
        NASA/NOAA/NESDIS, 2022.
        https://www.ospo.noaa.gov/Organization/Documents/PUG/GS%20Series%20416-R-PUG-L2%20Plus-0349%20Vol%205%20v2.4.pdf
    """

    x: NDArray[float64] = data(convert=to_float64)
    y: NDArray[float64] = data(convert=to_float64)
