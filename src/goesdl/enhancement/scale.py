from typing import cast

from matplotlib.colors import Colormap, LinearSegmentedColormap, Normalize
from numpy import interp

from .constants import CBTICKS_N, CBTICKS_STEP
from .palette import EnhacementPalette
from .shared import (
    ColorSegments,
    DomainData,
    KeypointList,
    MSegmentData,
    SegmentData,
)
from .st_stock import st_default, st_stock
from .stretching import EnhacementStretching
from .ticks import ColorbarTicks


class EnhancementScale:

    barticks: ColorbarTicks
    palette: EnhacementPalette
    stretching: EnhacementStretching

    def __init__(
        self,
        palette: EnhacementPalette,
        stretching: EnhacementStretching | None = None,
        cbarticks: ColorbarTicks | None = None,
    ) -> None:
        self.palette = palette
        self.stretching = stretching or EnhacementStretching(
            st_default, st_stock[st_default]
        )

        self.barticks = cbarticks or ColorbarTicks(
            self.stretching.domain, CBTICKS_N, tickstep=CBTICKS_STEP
        )

    def set_offset(self, offset: float) -> None:
        self.stretching.offset = offset
        self.set_ticks(self.barticks.nticks, self.barticks.tickstep)

    def set_ticks(self, nticks: int = CBTICKS_N, tickstep: int = 0) -> None:
        self.barticks = ColorbarTicks(self.stretching.domain, nticks, tickstep)

    def _transform_color_segment(
        self, segment: ColorSegments, xp: KeypointList, yp: KeypointList
    ) -> ColorSegments:
        new_segment: ColorSegments = []

        for x0, y0, y1 in segment:
            x1 = self._transform_keypoint(x0, xp, yp)

            new_segment.append((x1, y0, y1))

        return new_segment

    def _transform_keypoint(
        self, x: float, xp: KeypointList, yp: KeypointList
    ) -> float:
        y_scaled = interp(x, xp, yp, left=0.0, right=1.0)

        return cast(float, y_scaled)

    def _transform_segment_data(self) -> MSegmentData:
        yp, xp = self.stretching.keypoints

        new_segment_data: SegmentData = {
            component: self._transform_color_segment(segment, xp, yp)
            for component, segment in self.palette.segment_data.items()
        }

        return cast(MSegmentData, new_segment_data)

    @property
    def cmap(self) -> Colormap:
        transformed_segment_data = self._transform_segment_data()

        return LinearSegmentedColormap(
            self.name, transformed_segment_data, N=self.palette.ncolors
        )

    @property
    def cnorm(self) -> Normalize:
        vmin, vmax = self.stretching.extent
        return Normalize(vmin=vmin, vmax=vmax, clip=False)

    @property
    def cticks(self) -> KeypointList:
        return self.barticks.cticks

    @property
    def domain(self) -> DomainData:
        return self.stretching.domain

    @property
    def extent(self) -> DomainData:
        return self.stretching.extent

    @property
    def name(self) -> str:
        return f"{self.palette.name}({self.stretching.name})"

    @property
    def ncolors(self) -> int:
        return self.palette.ncolors
