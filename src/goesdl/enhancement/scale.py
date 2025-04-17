from collections.abc import Sequence
from pathlib import Path
from typing import Literal

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import (
    BoundaryNorm,
    Colormap,
    LinearSegmentedColormap,
    Normalize,
)
from numpy.typing import NDArray

from .colormap import EnhancementColormap
from .shared import DomainData, RGBValue
from .table import EnhacementTable
from .ticks import ColorbarTicks

ExtendMode = Literal["neither", "both", "min", "max"]


class EnhancementScale:

    cmap: Colormap
    cnorm: Normalize
    cticks: list[float]
    domain: DomainData
    extent: DomainData
    name: str
    ncolors: int
    offset: float

    def __init__(
        self,
        specs: EnhacementTable | EnhancementColormap,
        offset: float = 0.0,
        ncolors: int = 256,
        nticks: int = 16,
        mode: ExtendMode = "neither",
    ) -> None:
        if isinstance(specs, EnhacementTable):
            cmap, cnorm = self._create_from_table(specs, offset, ncolors, mode)
        else:
            cmap, cnorm = self._create_from_colormap(
                specs, offset, ncolors, mode
            )

        domain = self._actual_range(specs.domain, offset)
        extent = self._actual_range(specs.extent, offset)

        refs = ColorbarTicks(extent, nticks, step=0)

        self.cmap = cmap
        self.cnorm = cnorm
        self.cticks = refs.cticks
        self.domain = domain
        self.extent = extent
        self.name = specs.name
        self.ncolors = ncolors
        self.offset = offset

    def extend(self, mode: ExtendMode = "neither") -> None:
        self.cnorm = self._create_colorbar_norm(
            self.extent, self.ncolors, mode
        )

    @classmethod
    def from_colormap(
        cls,
        name: str,
        cmap_names: str | Sequence[str],
        keypoints: Sequence[float],
        offset: float = 0.0,
        ncolors: int = 256,
        nticks: int = 16,
        mode: ExtendMode = "neither",
    ) -> "EnhancementScale":
        cmap = EnhancementColormap(name, cmap_names, keypoints)

        return cls(cmap, offset, ncolors, nticks, mode)

    @classmethod
    def from_file(
        cls,
        palette_path: str | Path,
        stretching_path: str | Path = "",
        offset: float = 0.0,
        ncolors: int = 256,
        nticks: int = 16,
        mode: ExtendMode = "neither",
    ) -> "EnhancementScale":
        table = EnhacementTable.from_file(palette_path, stretching_path)

        return cls(table, offset, ncolors, nticks, mode)

    def set_ticks(self, nticks: int = 16, step: int = 0) -> None:
        refs = ColorbarTicks(self.extent, nticks, step)
        self.cticks = refs.cticks

    @staticmethod
    def _actual_range(extent: DomainData, offset: float) -> DomainData:
        return extent[0] + offset, extent[1] + offset

    @classmethod
    def _create_colorbar_norm(
        cls, extent: DomainData, ncolors: int, mode: ExtendMode
    ) -> BoundaryNorm:
        """
        Create a colorbar norm for the given temperature range.

        Creates BoundaryNorm with a list of levels evenly spaced between
        tmin and tmax.

        Parameters
        ----------
        extent: DomainData
            Tuple with minimum and maximum temperature.
        ncolors : int, optional
            Number of colormap levels.
        mode : ExtendMode
            Colorbar extend specification.

        Returns
        -------
        BoundaryNorm
            The colorbar norm.
        """
        tmin, tmax = extent
        vmin, vmax = round(tmin), round(tmax)

        nlevels = ncolors + 1
        levels = cls._linspace(vmin, vmax, nlevels)

        return BoundaryNorm(levels, ncolors=ncolors, clip=True, extend=mode)

    def _create_from_colormap(
        self,
        colormap: EnhancementColormap,
        offset: float,
        ncolors: int,
        mode: ExtendMode,
    ) -> tuple[LinearSegmentedColormap, BoundaryNorm]:
        extent = self._actual_range(colormap.extent, offset)

        cnorm = self._create_colorbar_norm(extent, ncolors, mode)

        tmin, tmax = extent
        total_range = tmax - tmin

        all_colors: list[NDArray[np.float64]] = []
        for i, name in enumerate(colormap.cmap_names):
            icmap = plt.get_cmap(name)
            start_keypoint = colormap.keypoints[i]
            end_keypoint = colormap.keypoints[i + 1]
            segment_range = end_keypoint - start_keypoint
            proportion = segment_range / total_range
            n_segment_colors = round(ncolors * proportion)
            colors = icmap(np.linspace(0, 1, n_segment_colors))
            all_colors.append(colors)

        colors = np.vstack(all_colors)

        cmap = LinearSegmentedColormap.from_list(
            colormap.name, colors, N=ncolors
        )

        icmap = plt.get_cmap(colormap.cmap_names[0])
        under_color = self._to_colortype(icmap.get_under())

        icmap = plt.get_cmap(colormap.cmap_names[-1])
        over_color = self._to_colortype(icmap.get_over())
        bad_color = self._to_colortype(icmap.get_bad())

        cmap.set_under(under_color)
        cmap.set_over(over_color)
        cmap.set_bad(bad_color)

        return cmap, cnorm

    def _create_from_table(
        self,
        table: EnhacementTable,
        offset: float,
        ncolors: int,
        mode: ExtendMode,
    ) -> tuple[LinearSegmentedColormap, BoundaryNorm]:
        extent = self._actual_range(table.extent, offset)

        cnorm = self._create_colorbar_norm(extent, ncolors, mode)

        cmap = LinearSegmentedColormap(
            table.name, table.color_table, N=ncolors
        )

        cmap.set_under(table.stock["background"])
        cmap.set_over(table.stock["foreground"])
        cmap.set_bad(table.stock["nan"])

        return cmap, cnorm

    @staticmethod
    def _linspace(start: float, stop: float, nlevels: int) -> list[float]:
        """
        Generates a list of evenly spaced numbers between start and stop.

        Parameters
        ----------
        start : float
            Initial value.
        stop : float
            Final value.
        nlevels : int
            Number of elements in the list.

        Returns
        -------
        list[float]
            A list with the generated numbers.
        """
        extent = stop - start
        nmax = nlevels - 1
        return [start + (i / nmax) * extent for i in range(nlevels)]

    @staticmethod
    def _to_colortype(color: NDArray[np.float64]) -> RGBValue:
        return color[0], color[1], color[2]
