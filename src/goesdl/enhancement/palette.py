"""
Provide the EnhacementPalette class for handling color enhancement
palettes.
"""

from collections.abc import Sequence
from pathlib import Path

from .colormap import (
    ColormapBase,
    CombinedColormap,
    ContinuousColormap,
    DiscreteColormap,
    NamedColormap,
    SegmentedColormap,
)
from .colortable import ColormapTable
from .constants import COLOR_COMPONENTS, UNNAMED_COLORMAP
from .eu_table import eu_utility
from .shared import (
    ColorSegments,
    ColorTable,
    ColorValueList,
    ContinuousColorList,
    ContinuousColorTable,
    DiscreteColorList,
    GKeypointList,
    GSegmentData,
    KeypointList,
    SegmentData,
    ValueTable,
)


class EnhacementPalette(ColormapBase):
    """
    Represent a enhancement color palette.

    Methods
    -------
    from_file(path)
        Load a McIDAS or GMT enhancement color palette specification and
        create an EnhacementPalette instance.
    save_to_file(path, name, rgb)
        Save the enhancement color palette.
    """

    def __init__(self, colormap: ColormapBase) -> None:
        super().__init__(
            colormap.name, colormap.segment_data, colormap.keypoints, False
        )

    @classmethod
    def combined_from_stock(
        cls,
        colormap_names: str | Sequence[str],
        keypoints: GKeypointList,
        name: str = "",
    ) -> ColormapBase:
        return cls(CombinedColormap(name, colormap_names, keypoints))

    @classmethod
    def continuous(
        cls,
        name: str,
        listed_colors: ContinuousColorList | ContinuousColorTable,
    ) -> ColormapBase:
        return cls(ContinuousColormap(name, listed_colors))

    @classmethod
    def discrete(
        cls, name: str, listed_colors: DiscreteColorList
    ) -> ColormapBase:
        return cls(DiscreteColormap(name, listed_colors))

    @classmethod
    def from_stock(cls, name: str) -> ColormapBase:
        return cls(NamedColormap(name))

    @classmethod
    def load(cls, path: str | Path, name: str = "") -> ColormapBase:
        """
        Load a McIDAS or GMT enhancement color table specification.

        Parse a McIDAS enhancement utility table (EU TABLE) or GMT color
        palette table (CPT TABLE) text file and create color dictionary
        for a Matplotlib colormap.

        Parameters
        ----------
        path : str or Path
            Path to the color table specification text file.
        name : str
            The name for the palette.

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
        return cls(ColormapTable(path, name))

    @classmethod
    def segmented(cls, name: str, segment_data: GSegmentData) -> ColormapBase:
        return cls(SegmentedColormap(name, segment_data))

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
        name = "" if self.name == UNNAMED_COLORMAP else self.name

        color_table = self._create_color_table(self.full_segment_data)

        eu_utility.create_file(path, name, color_table, rgb)

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
    def _cleanup_color_table(cls, color_table: ColorTable) -> None:
        color_table.pop(-1)
        color_table.pop(0)

    @classmethod
    def _create_color_table(cls, segment_data: SegmentData) -> ColorTable:
        packed_segments = cls._pack_segment_data(segment_data)

        unpacked_segment_valuess = cls._unpack_segment_values(packed_segments)

        value_tables = cls._build_value_tables(unpacked_segment_valuess)

        color_table = eu_utility.make_color_table(value_tables)

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
