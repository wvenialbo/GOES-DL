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
GOESABIFixedGrid
    Represent GOES-R series satellite ABI Fixed Grid projection data.
GOESProjection
    Represent GOES-R series satellite projection information.
"""

from collections.abc import Callable
from typing import Any, Protocol

from netCDF4 import Dataset  # pylint: disable=no-name-in-module
from numpy import float64

from ..netcdf import DatasetView, HasStrHelp, variable
from ..protocols.geodetic import IndexRange
from ..utils.array import ArrayFloat32, ArrayFloat64

BoxLimits = tuple[int, int, int, int]


_imager_proj = variable("goes_imager_projection")


class GeostationaryGrid(Protocol):
    x: ArrayFloat64
    y: ArrayFloat64


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
        The longitude of the ideal satellite sub-point in East degrees.
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
    latitude_of_projection_origin: float64 = _imager_proj.attribute()
    longitude_of_projection_origin: float64 = _imager_proj.attribute()
    perspective_point_height: float64 = _imager_proj.attribute()
    sweep_angle_axis: str = _imager_proj.attribute()


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
        The semi-major axis of the globe in meters.
    semi_minor_axis : np.float64
        The semi-minor axis of the globe in meters.
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
    semi_major_axis: float64 = _imager_proj.attribute()
    semi_minor_axis: float64 = _imager_proj.attribute()
    inverse_flattening: float64 = _imager_proj.attribute()


class GOESImagerProjection(GOESOrbitGeometry, GOESGlobe):
    """
    Represent GOES-R series satellite Imager Projection information.

    The GOES Imager Projection, also called the ABI Fixed Grid, is the
    projection information included in all ABI Level 1b radiance data
    files and most ABI Level 2 derived product data files. It is a map
    projection based on the geostationary viewing perspective of the
    GOES-East or GOES-West satellite.

    Notes
    -----
    For information on GOES Imager Projection and GOES orbit geometry,
    see [1]_ and Section 4.2.8 of [2]_

    References
    ----------
    .. [1] STAR Atmospheric Composition Product Training, "GOES Imager
        Projection (ABI Fixed Grid)", NOAA/NESDIS/STAR, 2024.
        https://www.star.nesdis.noaa.gov/atmospheric-composition-training/satellite_data_goes_imager_projection.php.
    .. [2] GOES-R, "GOES-R Series Product Definition and User’s Guide
        (PUG), Volume 5: Level 2+ Products", Version 2.4,
        NASA/NOAA/NESDIS, 2022.
        https://www.ospo.noaa.gov/Organization/Documents/PUG/GS%20Series%20416-R-PUG-L2%20Plus-0349%20Vol%205%20v2.4.pdf
    """


def _to_float64(array: ArrayFloat32) -> ArrayFloat64:
    """
    Convert a float32 array to a float64 array.

    Parameters
    ----------
    array : ArrayFloat32
        The float32 array to convert.

    Returns
    -------
    ArrayFloat64
        The float64 array.
    """
    return array.astype(float64)


class GOESGeostationaryGrid(HasStrHelp):

    geometry: GOESOrbitGeometry
    globe: GOESGlobe
    grid: tuple[ArrayFloat64, ArrayFloat64]

    def __init__(
        self, dataframe: Dataset, delta: int, limits: BoxLimits | None
    ) -> None:
        # Validate delta parameter (subsampling increment step)
        if not 1 <= delta <= 10:
            raise ValueError(
                "'delta' must be an integer between 1 and 10, inclusive"
            )

        lon_limits = limits[:2] if limits else None
        lat_limits = limits[2:4] if limits else None

        grid, geom, globe = self._extract_geos_grid(
            dataframe, delta, lon_limits, lat_limits
        )

        self.geometry = geom
        self.globe = globe
        self.grid = (grid.x, grid.y)

    @staticmethod
    def _extract_geos_grid(
        dataframe: Dataset,
        step: int | None,
        lon_limits: IndexRange | None,
        lat_limits: IndexRange | None,
    ) -> tuple[GeostationaryGrid, GOESOrbitGeometry, GOESGlobe]:
        def subsample(limits: IndexRange | None) -> Callable[[Any], Any]:
            def closure(x: Any) -> Any:
                begin, end = limits or (None, None)
                skip = step or None
                return x[begin:end:skip]

            return closure

        class _FixedGrid(DatasetView):
            x: ArrayFloat64 = variable("x").data(
                filter=subsample(lon_limits), convert=_to_float64
            )
            y: ArrayFloat64 = variable("y").data(
                filter=subsample(lat_limits), convert=_to_float64
            )

        grid = _FixedGrid(dataframe)
        geom = GOESOrbitGeometry(dataframe)
        globe = GOESGlobe(dataframe)

        return grid, geom, globe
