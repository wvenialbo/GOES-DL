"""
Provide the EnhacementPalette class for handling colour enhancement
palettes.
"""

from collections.abc import Sequence
from pathlib import Path

from .colormap import (
    BaseColormap,
    CombinedColormap,
    ContinuousColormap,
    DiscreteColormap,
    NamedColormap,
    SegmentedColormap,
    UniformColormap,
)
from .colortable import (
    ColormapTable,
    CPTColorTable,
    ETColorTable,
    EUColorTable,
)
from .constants import UNNAMED_COLORMAP
from .eu_utility import eu_utility
from .shared import (
    ColorList,
    ColorTable,
    DiscreteColorList,
    GKeypointList,
    GSegmentData,
    UniformColorList,
)


class EnhancementPalette(BaseColormap):
    """
    Represent a enhancement colour palette.
    """

    def __init__(self, colormap: BaseColormap) -> None:
        super().__init__(
            colormap.name,
            colormap.color_table,
            colormap.keypoints,
            colormap.ncolors,
        )

        self.set_domain(colormap.domain)
        self.set_stock_colors(colormap.under, colormap.over, colormap.bad)

    @classmethod
    def combined_from_stock(
        cls,
        colormap_names: str | Sequence[str],
        keypoints: GKeypointList,
        name: str = "",
        ncolors: int = 256,
    ) -> "EnhancementPalette":
        return cls(CombinedColormap(name, colormap_names, keypoints, ncolors))

    @classmethod
    def continuous(
        cls, name: str, color_table: ColorTable, ncolors: int = 256
    ) -> "EnhancementPalette":
        return cls(ContinuousColormap(name, color_table, ncolors))

    @classmethod
    def discrete(
        cls, name: str, listed_colors: DiscreteColorList
    ) -> "EnhancementPalette":
        return cls(DiscreteColormap(name, listed_colors))

    @classmethod
    def from_stock(cls, name: str, ncolors: int = 256) -> "EnhancementPalette":
        return cls(NamedColormap(name, ncolors))

    @classmethod
    def load(
        cls, path: str | Path, ncolors: int = 256, invert: bool = False
    ) -> "EnhancementPalette":
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
        return cls(ColormapTable(path, ncolors, invert))

    @classmethod
    def load_cpt(
        cls, path: str | Path, ncolors: int = 256, invert: bool = False
    ) -> "EnhancementPalette":
        return cls(CPTColorTable(path, ncolors, invert))

    @classmethod
    def load_et(
        cls, path: str | Path, ncolors: int = 256, invert: bool = False
    ) -> "EnhancementPalette":
        return cls(ETColorTable(path, ncolors, invert))

    @classmethod
    def load_eu(
        cls, path: str | Path, ncolors: int = 256, invert: bool = False
    ) -> "EnhancementPalette":
        return cls(EUColorTable(path, ncolors, invert))

    @classmethod
    def segmented(
        cls, name: str, segment_data: GSegmentData, ncolors: int = 256
    ) -> "EnhancementPalette":
        return cls(SegmentedColormap(name, segment_data, ncolors))

    def save(
        self, path: str | Path, rgb: bool = False, invert: bool = False
    ) -> None:
        """
        Save the colour table.

        Save the colour table to a McIDAS enhancement utility table (EU
        TABLE) text file.

        Parameters
        ----------
        path : str or Path
            Path to the file where the colour table will be saved.
        rgb : bool, optional
            Flag indicating if the colour model is RGB, by default False.
        """
        name = "" if self.name == UNNAMED_COLORMAP else self.name

        color_list = self._make_color_list(self.color_table, invert)

        eu_utility.create_file(path, name, color_list, self.domain, rgb)

    @classmethod
    def uniform(
        cls, name: str, color_list: UniformColorList, ncolors: int = 256
    ) -> "EnhancementPalette":
        return cls(UniformColormap(name, color_list, ncolors))

    @classmethod
    def _make_color_list(
        cls, color_table: ColorTable, invert: bool
    ) -> ColorList:
        if invert:
            return [(1 - j, r, g, b) for j, (r, g, b) in reversed(color_table)]
        else:
            return [(j, r, g, b) for j, (r, g, b) in color_table]
