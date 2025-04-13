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

ExtendMode = Literal["neither", "both", "min", "max"]


class EnhancementScale:

    cmap: Colormap
    cnorm: Normalize
    cticks: list[float]
    domain: DomainData
    extent: DomainData
    name: str
    ncolors: int

    def __init__(
        self,
        specs: EnhacementTable | EnhancementColormap,
        ncolors: int = 256,
        nticks: int = 16,
        mode: ExtendMode = "neither",
    ) -> None:
        if isinstance(specs, EnhacementTable):
            cmap, cnorm = self._create_from_table(specs, ncolors, mode)
        else:
            cmap, cnorm = self._create_from_colormap(specs, ncolors, mode)

        cticks = self._create_colorbar_ticks(specs.extent, nticks, step=0)

        self.cmap = cmap
        self.cnorm = cnorm
        self.cticks = cticks
        self.domain = specs.domain
        self.extent = specs.extent
        self.name = specs.name
        self.ncolors = ncolors

    def extend(self, mode: ExtendMode = "neither") -> None:
        self.cnorm = self._create_colorbar_norm(
            self.extent, self.ncolors, mode
        )

    def ticks(self, nticks: int = 16, step: int = 0) -> None:
        self.cticks = self._create_colorbar_ticks(self.extent, nticks, step)

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

    @classmethod
    def _create_colorbar_ticks(
        cls, extent: DomainData, nticks: int, step: int
    ) -> list[float]:
        """
        Create a list of colorbar ticks for the given temperature range.

        Creates a list of ticks evenly spaced between tmin and tmax,
        with a minimum step of 5.

        Parameters
        ----------
        extent: DomainData
            Tuple with minimum and maximum temperature.
        nticks : int
            Maximum number of ticks.
        step : int, optional
            Tick step, by default 0 (automatic).

        Returns
        -------
        list[float]
            List of colorbar ticks.
        """
        tmin, tmax = extent

        if step < 5:
            step = cls._find_tick_step(
                tmin, tmax, max_ticks=nticks, min_step=5
            )

        cbmin = cls._find_tick_min(tmin, step)
        cbmax = cls._find_tick_max(tmax, step) + 1

        return [float(tick) for tick in range(cbmin, cbmax, step)]

    def _create_from_colormap(
        self, colormap: EnhancementColormap, ncolors: int, mode: ExtendMode
    ) -> tuple[LinearSegmentedColormap, BoundaryNorm]:
        cnorm = self._create_colorbar_norm(colormap.extent, ncolors, mode)

        tmin, tmax = colormap.extent
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
        self, table: EnhacementTable, ncolors: int, mode: ExtendMode
    ) -> tuple[LinearSegmentedColormap, BoundaryNorm]:
        cnorm = self._create_colorbar_norm(table.extent, ncolors, mode)

        cmap = LinearSegmentedColormap(
            table.name, table.color_table, N=ncolors
        )

        cmap.set_under(table.stock["background"])
        cmap.set_over(table.stock["foreground"])
        cmap.set_bad(table.stock["nan"])

        return cmap, cnorm

    @staticmethod
    def _find_tick_max(vmax: float, step: int) -> int:
        """
        Finds the last multiple of `step` that is less or equal to `vmax`.

        Parameters
        ----------
        vmax : float
            The number from which the last multiple less or equal will be
            searched.
        step : int
            The number of which we want to find the multiples.

        Returns
        -------
        int
            The last multiple of `step` that is less or equal to `vmax`.
        """
        cociente = vmax // step
        return int(cociente) * step

    @staticmethod
    def _find_tick_min(vmin: float, step: int) -> int:
        """
        Finds the first multiple of `step` that is greater or equal to
        `vmin`.

        Parameters
        ----------
        vmin : float
            The number from which the first multiple greater or equal will
            be searched.
        step : int
            The number of which we want to find the multiples.

        Returns
        -------
        int
            The first multiple of `step` that is greater or equal to `vmin`.
        """
        quotient, remainder = divmod(vmin, step)
        return int(quotient + 1 if remainder else quotient) * step

    @classmethod
    def _find_tick_step(
        cls, tmin: float, tmax: float, max_ticks: int, min_step: int
    ) -> int:
        """
        Finds the step that divides the range [tmin, tmax] into `ticks`
        intervals.

        Parameters
        ----------
        tmin : float
            The minimum value of the range.
        tmax : float
            The maximum value of the range.
        max_ticks : int, optional
            The maximum number of intervals to divide the range.
        min_step : int, optional
            The minimum tick step to consider. Larger steps will be
            multiple of this value.

        Returns
        -------
        float
            The step that divides the range [tmin, tmax] into up
            to `max_ticks` intervals.
        """
        return cls._find_tick_min((tmax - tmin) / max_ticks, min_step)

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
