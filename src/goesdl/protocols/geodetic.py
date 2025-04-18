from typing import Protocol

from ..utils.array import ArrayFloat32

CoordRange = tuple[float, float]
IndexRange = tuple[int, int]
RegionDomain = tuple[CoordRange, CoordRange]
RegionExtent = tuple[float, float, float, float]


class GeodeticRegion(Protocol):

    domain: RegionDomain

    xticks: ArrayFloat32
    yticks: ArrayFloat32

    extent: RegionExtent

    lat_bounds: CoordRange

    lon_bounds: CoordRange
