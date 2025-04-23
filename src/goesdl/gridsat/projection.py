from numpy import float32

from ..netcdf import DatasetView, HasStrHelp, attribute, scalar
from .databook_gc import (
    GRS80_INVERSE_FLATTENING,
    GRS80_SEMI_MAJOR_AXIS,
    GRS80_SEMI_MINOR_AXIS,
)


class GSOrbitGeometry(DatasetView):
    """
    Represent GOES series satellite orbit geometry information.
    """

    # Information about the projection

    projection: str = attribute("Projection")
    """
    Projection type.
    """

    sub_satellite_latitude: float32 = scalar("satlat")
    """
    Sub-satellite latitude in degrees (North positive).

    valid_range: [-20.  20.]
    """

    sub_satellite_longitude: float32 = scalar("satlon")
    """
    Sub-satellite longitude in degrees (East positive).

    valid_range: [-180.  360.]
    """

    sub_satellite_orbital_radius: float32 = scalar("satrad")
    """
    Sub-satellite orbital radius in km.
    valid_range: [38000. 44000.]
    """


class GSGlobe(HasStrHelp):

    # Information about the globe

    semi_major_axis: float = GRS80_SEMI_MAJOR_AXIS
    """
    Semi-major axis of the ellipsoid in metres.
    """

    semi_minor_axis: float = GRS80_SEMI_MINOR_AXIS
    """
    Semi-minor axis of the ellipsoid in metres.
    """

    inverse_flattening: float = GRS80_INVERSE_FLATTENING
    """
    Inverse flattening (a / (a - b)) of the ellipsoid.
    """
