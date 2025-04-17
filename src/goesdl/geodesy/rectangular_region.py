from collections.abc import Generator
from math import degrees, floor
from typing import Literal, cast

from numpy import arange, float32

from ..utils.array import ArrayFloat32

CoordDomain = tuple[float, float, float, float]
CoordLimits = tuple[float, float]
ExtentType = tuple[float, float]
CenterType = tuple[float, float]
StepType = tuple[float, float]

DEFAULT_STEP = (2.0, 2.0)


class RectangularRegion:

    domain: CoordDomain

    xticks: ArrayFloat32
    yticks: ArrayFloat32

    def __init__(self, domain: CoordDomain) -> None:
        self.domain = domain

        self.xticks, self.yticks = self._create_grid_ticks(
            domain, DEFAULT_STEP
        )

    def set_ticks(
        self, domain: CoordDomain | None = None, step: StepType = DEFAULT_STEP
    ) -> None:
        domain = self.domain if domain is None else domain
        self.xticks, self.yticks = self._create_grid_ticks(domain, step)

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

    @staticmethod
    def _create_grid_ticks(
        domain: CoordDomain, step: StepType
    ) -> tuple[ArrayFloat32, ArrayFloat32]:
        dx, dy = step
        lon_min = dx * floor(domain[0] / dx)
        lon_max = dx * floor(domain[1] / dx) + dx
        xticks = arange(lon_min, lon_max, dx).astype(float32)

        lat_min = dy * floor(domain[2] / dy)
        lat_max = dy * floor(domain[3] / dy) + dy
        yticks = arange(lat_min, lat_max, dy).astype(float32)

        return cast(ArrayFloat32, xticks), cast(ArrayFloat32, yticks)

    @property
    def extent(self) -> CoordDomain:
        return self.domain

    @property
    def lon_bounds(self) -> CoordLimits:
        return self.domain[:2]

    @property
    def lat_bounds(self) -> CoordLimits:
        return self.domain[2:]
