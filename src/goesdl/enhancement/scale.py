from collections.abc import Sequence
from pathlib import Path
from typing import Any, cast

from matplotlib.colors import (
    Colormap,
    FuncNorm,
    LinearSegmentedColormap,
    Normalize,
)
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
    StretchingTable,
)
from .st_stock import st_default, st_stock
from .stretching import EnhacementStretching
from .ticks import ColorbarTicks


class EnhancementScale:

    palette: EnhacementPalette
    stretching: EnhacementStretching

    cmap: Colormap
    cnorm: Normalize

    ticker: ColorbarTicks

    def __init__(
        self,
        palette: EnhacementPalette,
        stretching: EnhacementStretching | None = None,
    ) -> None:
        self.palette = palette

        self.stretching = stretching or EnhacementStretching(
            st_default, st_stock[st_default]
        )

        self._stretching_updated()

    @classmethod
    def combined_from_stock(
        cls,
        colormap_names: str | Sequence[str],
        keypoints: GKeypointList,
        name: str = "",
        ncolors: int = 256,
    ) -> "EnhancementScale":
        cpal = EnhacementPalette.combined_from_stock(
            colormap_names, keypoints, name, ncolors
        )
        return cls(cpal)

    @classmethod
    def continuous(
        cls, name: str, color_table: ContinuousColorTable, ncolors: int = 256
    ) -> "EnhancementScale":
        cpal = EnhacementPalette.continuous(name, color_table, ncolors)
        return cls(cpal)

    def create_stretching(self, name: str, table: StretchingTable) -> None:
        self.stretching = EnhacementStretching(name, table)
        self._stretching_updated()

    @classmethod
    def discrete(
        cls, name: str, listed_colors: DiscreteColorList
    ) -> "EnhancementScale":
        cpal = EnhacementPalette.discrete(name, listed_colors)
        return cls(cpal)

    @classmethod
    def from_stock(cls, name: str, ncolors: int = 256) -> "EnhancementScale":
        cpal = EnhacementPalette.from_stock(name, ncolors)
        return cls(cpal)

    @classmethod
    def load(
        cls, path: str | Path, ncolors: int = 256, invert: bool = False
    ) -> "EnhancementScale":
        """
        Load a McIDAS or GMT enhancement colour table specification.

        Parse a McIDAS binary and text based enhancement utility colour
        tables (EU TABLE and .ET files) or GMT colour palette table
        (.CPT files).

        Parameters
        ----------
        path : str | Path
            Path to the colour table specification text file.
        ncolors : int
            Number of colours to instantiate. Default: 256.

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
        cpal = EnhacementPalette.load(path, ncolors, invert)
        return cls(cpal)

    @classmethod
    def load_cpt(
        cls, path: str | Path, ncolors: int = 256, invert: bool = False
    ) -> "EnhancementScale":
        cpal = EnhacementPalette.load_cpt(path, ncolors, invert)
        return cls(cpal)

    @classmethod
    def load_et(
        cls, path: str | Path, ncolors: int = 256, invert: bool = False
    ) -> "EnhancementScale":
        cpal = EnhacementPalette.load_et(path, ncolors, invert)
        return cls(cpal)

    @classmethod
    def load_eu(
        cls, path: str | Path, ncolors: int = 256, invert: bool = False
    ) -> "EnhancementScale":
        cpal = EnhacementPalette.load_eu(path, ncolors, invert)
        return cls(cpal)

    def load_stretching(self, path: str | Path) -> None:
        """
        Create an EnhacementStretching instance from a file.

        Parameters
        ----------
        path : str or Path
            Path to the file containing the enhancement stretching data.

        Returns
        -------
        EnhacementStretching
            An instance of the EnhacementStretching class.
        """
        self.stretching = EnhacementStretching.load(path)
        self._stretching_updated()

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

    def save_stretching(self, path: str | Path) -> None:
        """
        Save the enhancement stretching table to a file.

        Parameters
        ----------
        path : str or Path
            Path to the file where the enhancement stretching table will
            be saved.
        name : str
            The name of the enhancement stretching table. Override the
            actual name if provided.
        """
        self.stretching.save(path)

    def set_ticks(
        self,
        nticks: int | None = None,
        tickstep: int | None = None,
        offset: float = 0.0,
        scale: float = 1.0,
    ) -> None:
        self.ticker = ColorbarTicks(
            self.stretching.domain, nticks, tickstep, offset, scale
        )

    @classmethod
    def uniform(
        cls,
        name: str,
        listed_colors: ContinuousColorList | ContinuousColorTable,
        ncolors: int = 256,
    ) -> "EnhancementScale":
        cpal = EnhacementPalette.continuous(name, listed_colors, ncolors)
        return cls(cpal)

    def update_palette(self, palette: EnhacementPalette) -> None:
        self.palette = palette
        self.cmap = self._get_cmap()

    def update_stretching(self, stretching: EnhacementStretching) -> None:
        self.stretching = stretching
        self._stretching_updated()

    def _get_cmap(self) -> Colormap:
        segment_data = cast(MSegmentData, self.palette.segment_data)
        return LinearSegmentedColormap(
            self.name, segment_data, N=self.palette.ncolors
        )

    def _get_cnorm(self) -> Normalize:
        fx: tuple[float, ...]
        fy: tuple[float, ...]
        fx, fy = zip(*self.stretching.table)

        ymin, ymax = self.stretching.range
        fy = tuple((y - ymin) / (ymax - ymin) for y in fy)

        if self.stretching.is_reversed:
            fp = fy[::-1]
            fq = fx[::-1]
        else:
            fp = fy
            fq = fx

        def forward_mapping(x: Any) -> Any:
            return interp(x, fx, fy, left=fy[0], right=fy[-1])

        def inverse_mapping(p: Any) -> Any:
            return interp(p, fp, fq, left=fq[0], right=fq[-1])

        class _Normalize(Normalize):
            def __call__(self, x: Any) -> Any:  # type: ignore
                return forward_mapping(x)

            def inverse(self, y: Any) -> Any:  # type: ignore
                return inverse_mapping(y)

        return _Normalize()

    def _stretching_updated(self):
        self.ticker = ColorbarTicks(self.stretching.domain)
        self.cmap = self._get_cmap()
        self.cnorm = self._get_cnorm()

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
    def domain(self) -> DomainData:
        return self.stretching.domain

    @property
    def name(self) -> str:
        return f"{self.palette.name}({self.stretching.name})"

    @property
    def ncolors(self) -> int:
        return self.palette.ncolors

    @property
    def range(self) -> DomainData:
        return self.stretching.range

    @property
    def tmap(self) -> Colormap:
        transformed_segment_data = self._transform_segment_data()
        return LinearSegmentedColormap(
            self.name, transformed_segment_data, N=self.palette.ncolors
        )

    @property
    def tnorm(self) -> Normalize:
        ymin, ymax = self.stretching.range
        xmin, xmax = self.stretching.domain

        if ymin < ymax:
            return Normalize(vmin=xmin, vmax=xmax, clip=False)

        def forward_mapping(x: float) -> float:
            return (x - xmax) / (xmin - xmax)

        def inverse_mapping(v: float) -> float:
            return v * xmin + (1 - v) * xmax

        return FuncNorm(
            (forward_mapping, inverse_mapping),
            vmin=xmin,
            vmax=xmax,
            clip=False,
        )
