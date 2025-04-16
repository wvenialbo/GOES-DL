from collections.abc import Generator
from math import degrees
from typing import Literal, cast

CoordDomain = tuple[float, float, float, float]
CoordLimits = tuple[float, float]
ExtentType = tuple[float, float]
CenterType = tuple[float, float]


class RectangularRegion:

    domain: CoordDomain

    def __init__(self, domain: CoordDomain) -> None:
        self.domain = domain

    @classmethod
    def from_central_point(
        cls,
        extent: ExtentType,
        center_deg: CenterType,
        units: Literal["arcsec", "arcmin", "deg", "rad"] = "deg",
    ) -> "RectangularRegion":
        extent_deg: ExtentType | Generator[float]
        if units == "arcsec":
            extent_deg = (value / 3600.0 for value in extent)
        elif units == "arcmin":
            extent_deg = (value / 60.0 for value in extent)
        elif units == "rad":
            extent_deg = (degrees(value) for value in extent)
        else:
            extent_deg = extent

        width_deg, height_deg = extent_deg
        lon_cen, lat_cen = center_deg

        x_half = 0.5 * width_deg
        y_half = 0.5 * height_deg

        lons_deg = [lon_cen - x_half, lon_cen + x_half]
        lats_deg = [lat_cen - y_half, lat_cen + y_half]

        domain = tuple(lons_deg + lats_deg)

        return cls(cast(CoordDomain, domain))

    @property
    def extent(self) -> CoordDomain:
        return self.domain

    @property
    def lon_bounds(self) -> CoordLimits:
        return self.domain[:2]

    @property
    def lat_bounds(self) -> CoordLimits:
        return self.domain[2:]
