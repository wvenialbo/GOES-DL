from collections.abc import Callable, Sequence
from pathlib import Path
from typing import Any, cast

from matplotlib.colors import Colormap, LinearSegmentedColormap, Normalize
from numpy import interp

from .palette import EnhacementPalette
from .shared import (
    ColorSegments,
    ContinuousColorList,
    ContinuousColorTable,
    DiscreteColorList,
    DomainData,
    GKeypointList,
    GSegmentData,
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

        self.barticks = cbarticks or ColorbarTicks(self.stretching.domain)

    @classmethod
    def combined_from_stock(
        cls,
        colormap_names: str | Sequence[str],
        keypoints: GKeypointList,
        name: str = "",
    ) -> "EnhancementScale":
        cpal = EnhacementPalette.combined_from_stock(
            colormap_names, keypoints, name
        )
        return cls(cpal)

    @classmethod
    def continuous(
        cls,
        name: str,
        listed_colors: ContinuousColorList | ContinuousColorTable,
        ncolors: int = 256,
    ) -> "EnhancementScale":
        cpal = EnhacementPalette.continuous(name, listed_colors, ncolors)
        return cls(cpal)

    @classmethod
    def discrete(
        cls,
        name: str,
        listed_colors: DiscreteColorList,
        ncolors: int | None = None,
    ) -> "EnhancementScale":
        cpal = EnhacementPalette.discrete(name, listed_colors, ncolors)
        return cls(cpal)

    @classmethod
    def from_stock(cls, name: str, ncolors: int = 256) -> "EnhancementScale":
        cpal = EnhacementPalette.from_stock(name, ncolors)
        return cls(cpal)

    @classmethod
    def load(cls, path: str | Path, ncolors: int = 256) -> "EnhancementScale":
        """
        Load a McIDAS or GMT enhancement color table specification.

        Parse a McIDAS enhancement utility table (EU TABLE) or GMT color
        palette table (CPT TABLE) text file and create color dictionary
        for a Matplotlib colormap.

        Parameters
        ----------
        path : str or Path
            Path to the color table specification text file.

        Returns
        -------
        EnhacementPalette
            A EnhacementPalette object.

        Notes
        -----
        The Man computer Interactive Data Access System (McIDAS) is a
        research quality suite of applications used for decoding,
        analyzing, and displaying meteorological data developed by the
        University of Wisconsin-Madison Space Science and Engineering
        Center (UWisc/SSEC).

        - https://www.ssec.wisc.edu/mcidas/
        - https://www.unidata.ucar.edu/software/mcidas/

        The Generic Mapping Tools (GMT) is an open-source collection of
        tools for manipulating geographic and Cartesian data sets and
        producing PostScript illustrations ranging from simple x-y plots
        through maps to complex 3D perspective views.

        - https://www.generic-mapping-tools.org/
        """
        cpal = EnhacementPalette.load(path, ncolors)
        return cls(cpal)

    @classmethod
    def segmented(
        cls, name: str, segment_data: GSegmentData, ncolors: int = 256
    ) -> "EnhancementScale":
        cpal = EnhacementPalette.segmented(name, segment_data, ncolors)
        return cls(cpal)

    def save(self, path: str | Path, rgb: bool = False) -> None:
        """
        Save the color table.

        Save the color table to a McIDAS enhancement utility table (EU
        TABLE) text file.

        Parameters
        ----------
        path : str or Path
            Path to the file where the color table will be saved.
        rgb : bool, optional
            Flag indicating if the color model is RGB, by default False.
        """
        self.palette.save(path, rgb)

    def get_ticklabels(
        self, offset: float = 0.0, format: Callable[[float], Any] | None = None
    ) -> list[Any]:
        label_values = self.barticks.get_ticklabels(offset)
        return list(map(format, label_values)) if format else label_values

    def set_ticks(
        self, nticks: int | None = None, tickstep: int | None = None
    ) -> None:
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
        vmin, vmax = self.stretching.domain
        return Normalize(vmin=vmin, vmax=vmax, clip=False)

    @property
    def cticks(self) -> KeypointList:
        return self.barticks.cticks

    @property
    def domain(self) -> DomainData:
        return self.stretching.domain

    @property
    def name(self) -> str:
        return f"{self.palette.name}({self.stretching.name})"

    @property
    def ncolors(self) -> int:
        return self.palette.ncolors
