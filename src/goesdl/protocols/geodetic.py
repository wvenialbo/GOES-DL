from typing import Protocol

from cartopy.crs import Projection

from ..utils.array import ArrayFloat32

CoordRange = tuple[float, float]
IndexRange = tuple[int, int]
RegionDomain = tuple[CoordRange, CoordRange]
RegionExtent = tuple[float, float, float, float]


class GeodeticRegion(Protocol):
    """
    A protocol for geodetic region of interest (ROI).

    The region of interest is defined by a pair of coordinate ranges,
    e.g. a rectangular region defined by latitude and longitude limits.
    The region is used to slice the data.

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

    @property
    def extent(self) -> RegionExtent:
        """
        The extent of the region of interest as a tuple of (min_lon,
        max_lon, min_lat, max_lat).
        """

    @property
    def lat_bounds(self) -> CoordRange:
        """
        The latitude bounds of the region of interest as a tuple of
        (min_lat, max_lat).
        """

    @property
    def lon_bounds(self) -> CoordRange:
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


class GeodeticGrid(Protocol):
    """
    A protocol for geodetic grid data.

    Holds the grid data extracted from the satellite dataset, the region
    of interest (ROI) to slice the data, and a projection containing the
    original coordinate reference system (CRS) to transform the data.

    Attributes
    ----------
    crs : Projection
        The projection of the data. The projection is used to transform
        the data.
    lat : ArrayFloat32
        A 2D array containing the sliced values of the latitude grid
        data.
    lat_limits : IndexRange
        A tuple of two integers containing the indices of the minimum
        and maximum latitude values of the grid data. The limits are
        used to slice the data.
    lon : ArrayFloat32
        A 2D array containing the sliced values of the longitude grid
        data.
    lon_limits : IndexRange
        A tuple of two integers containing the indices of the minimum
        and maximum longitude values of the grid data. The limits are
        used to slice the data.
    region : GeodeticRegion
        The region of interest. The region is used to find the array
        indices to slice the data.
    """

    crs: Projection
    """
    The projection of the data. The projection is used to transform
    the data.
    """

    lat: ArrayFloat32
    """
    A 2D array containing the sliced values of the latitude grid
    data.
    """

    lat_limits: IndexRange
    """
    A tuple of two integers containing the indices of the minimum
    and maximum latitude values of the grid data. The limits are
    used to slice the data.
    """

    lon: ArrayFloat32
    """
    A 2D array containing the sliced values of the longitude grid
    data.
    """

    lon_limits: IndexRange
    """
    A tuple of two integers containing the indices of the minimum
    and maximum longitude values of the grid data. The limits are
    used to slice the data.
    """

    @property
    def region(self) -> GeodeticRegion:
        """
        The region of interest. The region is used to find the array
        indices to slice the data.
        """
