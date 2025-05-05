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
from .constants import COLOR_COMPONENTS, UNNAMED_COLORMAP
from .eu_utility import eu_utility
from .shared import (
    ColorList,
    ColorSegments,
    ColorTable,
    ColorValueList,
    DiscreteColorList,
    GKeypointList,
    GSegmentData,
    KeypointList,
    SegmentData,
    UniformColorList,
    ValueTable,
)


class EnhancementPalette(BaseColormap):
    """
    Represent a enhancement colour palette.
    """

    def __init__(self, colormap: BaseColormap) -> None:
        super().__init__(
            colormap.name,
            colormap.segment_data,
            colormap.keypoints,
            colormap.ncolors,
            False,
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

    def save(self, path: str | Path, rgb: bool = False) -> None:
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

        color_table = self._create_color_table(self.full_segment_data)

        eu_utility.create_file(path, name, color_table, rgb)

    @classmethod
    def uniform(
        cls, name: str, color_list: UniformColorList, ncolors: int = 256
    ) -> "EnhancementPalette":
        return cls(UniformColormap(name, color_list, ncolors))

    @classmethod
    def _build_value_tables(
        cls, unpacked_segment_values: list[tuple[float, ...]]
    ) -> ValueTable:
        x: KeypointList = []
        r: ColorValueList = []
        g: ColorValueList = []
        b: ColorValueList = []

        for xi, r0, r1, g0, g1, b0, b1 in unpacked_segment_values:
            x.extend((xi, xi))
            r.extend((r0, r1))
            g.extend((g0, g1))
            b.extend((b0, b1))

        return x, b, g, r

    @classmethod
    def _cleanup_color_table(cls, color_table: ColorList) -> None:
        color_table.pop(-1)
        color_table.pop(0)

    @classmethod
    def _create_color_table(cls, segment_data: SegmentData) -> ColorList:
        packed_segments = cls._pack_segment_data(segment_data)

        unpacked_segment_valuess = cls._unpack_segment_values(packed_segments)

        value_tables = cls._build_value_tables(unpacked_segment_valuess)

        color_table = eu_utility._scale_color_table(value_tables)

        cls._cleanup_color_table(color_table)

        return color_table

    @staticmethod
    def _pack_segment_data(segment_data: SegmentData) -> list[ColorSegments]:
        packed_segments: list[ColorSegments] = []

        packed_segments.extend(
            segment_data[component] for component in COLOR_COMPONENTS
        )

        return packed_segments

    @classmethod
    def _unpack_segment_values(
        cls, packed_segments: list[ColorSegments]
    ) -> list[tuple[float, ...]]:
        return [
            (*red, *green[1:], *blue[1:])
            for red, green, blue in zip(*packed_segments)
        ]
