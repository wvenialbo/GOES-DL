from typing import cast

from matplotlib.colors import Colormap, LinearSegmentedColormap, Normalize
from numpy import interp

from goesdl.enhancement import EnhacementPalette, EnhacementStretching

from .shared import (
    ColorSegments,
    KeypointList,
    MSegmentData,
    SegmentData,
)
from .ticks import ColorbarTicks


class EnhancementScale:

    barticks: ColorbarTicks
    palette: EnhacementPalette
    stretching: EnhacementStretching

    def __init__(
        self,
        palette: EnhacementPalette,
        stretching: EnhacementStretching,
        nticks: int = 16,
    ) -> None:
        self.palette = palette
        self.stretching = stretching
        self.barticks = ColorbarTicks(stretching.domain, nticks, step=0)

    def set_offset(self, offset: float) -> None:
        self.stretching.offset = offset

    def set_ticks(self, nticks: int = 16, step: int = 0) -> None:
        self.barticks = ColorbarTicks(self.stretching.domain, nticks, step)

    def _transform_color_segment(
        self, segment: ColorSegments
    ) -> ColorSegments:
        new_segment: ColorSegments = []

        for x0, y0, y1 in segment:
            x1 = self._transform_keypoint(x0)

            new_segment.append((x1, y0, y1))

        return new_segment

    def _transform_keypoint(self, x: float) -> float:
        y_v, x_v = zip(*self.stretching.table)

        x_min, x_max = self.stretching.range
        xp = [(x_i - x_min) / (x_max - x_min) for x_i in x_v]

        y_min, y_max = self.stretching.extent
        yp = [(y_i - y_min) / (y_max - y_min) for y_i in y_v]

        y_scaled = interp(x, xp, yp, left=0.0, right=1.0)

        return cast(float, y_scaled)

    def _transform_segment_data(self) -> MSegmentData:
        new_segment_data: SegmentData = {}

        for channel_name, channel_data in self.palette.segment_data.items():
            new_segment = self._transform_color_segment(channel_data)

            new_segment_data[channel_name] = new_segment

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
    def name(self) -> str:
        return f"{self.palette.name}({self.stretching.name})"
