from typing import Protocol

from ..utils.array import ArrayFloat32

CoordRange = tuple[float, float]
IndexRange = tuple[int, int]
RegionDomain = tuple[CoordRange, CoordRange]
RegionExtent = tuple[float, float, float, float]


class GeodeticRegion(Protocol):
    """
    A protocol for geodetic region of interest (ROI).

    The region of interest is defined by a pair of coordinate ranges
    (longitude and latitude).  The region is used to slice the data.

    Attributes
    ----------
    domain : RegionDomain
        The domain of the region of interest as a pair of coordinate
        ranges.  The first coordinate range is the longitude range
        (min_lon, max_lon) and the second coordinate range is the
        latitude range (min_lat, max_lat).
    extent : RegionExtent
        The extent of the region of interest as a tuple of (min_lon,
        max_lon, min_lat, max_lat).
    lat_bounds : CoordRange
        The latitude bounds of the region of interest as a tuple of
        (min_lat, max_lat).
    lon_bounds : CoordRange
        The longitude bounds of the region of interest as a tuple of
        (min_lon, max_lon).
    xticks : ArrayFloat32
        The x-ticks of the region of interest. Helper for plotting.  The
        x-ticks are the longitude values of the region of interest.
    yticks : ArrayFloat32
        The y-ticks of the region of interest. Helper for plotting.  The
        y-ticks are the latitude values of the region of interest.
    """

    domain: RegionDomain
    """
    The domain of the region of interest as a pair of coordinate
    ranges.  The first coordinate range is the longitude range
    (min_lon, max_lon) and the second coordinate range is the
    latitude range (min_lat, max_lat).
    """

    extent: RegionExtent
    """
    The extent of the region of interest as a tuple of (min_lon,
    max_lon, min_lat, max_lat).
    """

    lat_bounds: CoordRange
    """
    The latitude bounds of the region of interest as a tuple of
    (min_lat, max_lat).
    """

    lon_bounds: CoordRange
    """
    The longitude bounds of the region of interest as a tuple of
    (min_lon, max_lon).
    """

    xticks: ArrayFloat32
    """
    The x-ticks of the region of interest. Helper for plotting.
    The x-ticks are the longitude values of the region of interest.
    """

    yticks: ArrayFloat32
    """
    The y-ticks of the region of interest. Helper for plotting.
    The y-ticks are the latitude values of the region of interest.
    """
