from pathlib import Path

from .colortable import CPTColorTable, ETColorTable, EUColorTable
from .et_utility import et_utility
from .eu_utility import eu_utility
from .shared import (
    ColorList,
    ColorTable,
    DomainData,
    RGBValue,
    UniformColorList,
)


class ColormapGenerator:
    """
    Represent a enhancement colour table.

    This class provides methods to load, parse, and process McIDAS and
    GMT enhancement colour table files.

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

    color_table: ColorList
    stock_table: ColorList
    domain: DomainData
    name: str

    under: RGBValue
    over: RGBValue
    bad: RGBValue

    def __init__(self, path: str | Path) -> None:
        color_table, stock_table, domain, name = self._from_file(path)

        self.color_table = color_table
        self.stock_table = stock_table
        self.domain = domain
        self.name = name or Path(path).stem

        under, over, bad = (entry[1:] for entry in stock_table)

        self.under = under
        self.over = over
        self.bad = bad

    def save_as_listed_colormap(
        self, path: str | Path, invert: bool = False
    ) -> None:
        generated_code = self._generate_listed_colormap_code(invert)

        self._save_generated_code(path, generated_code)

    def save_as_segmented_colormap(
        self, path: str | Path, invert: bool = False
    ) -> None:
        generated_code = self._generate_segmented_colormap_code(invert)

        self._save_generated_code(path, generated_code)

    @classmethod
    def _from_file(
        cls, path: str | Path
    ) -> tuple[ColorList, ColorList, DomainData, str]:
        with open(path, "rb") as file:
            data = file.read()

        if et_utility.is_et_table(data[:4]) and et_utility.has_expected_size(
            data
        ):
            return cls._parse_binary_file(data)

        with open(path, "r", encoding="utf-8") as file:
            lines = file.readlines()

        return cls._parse_text_file(lines)

    def _generate_listed_colormap_code(self, invert: bool) -> str:
        color_list = self._make_color_list(self.color_table, invert)

        listed_colors = [
            f"({r:.6f}, {g:.6f}, {b:.6f})" for r, g, b in color_list
        ]

        listed_color_array = ",\n    ".join(listed_colors)

        return f"""\
from goesdl.enhancement import EnhancementPalette

_{self.name}_data = [
    {listed_color_array}
]

_colormap_names = [
    '{self.name}',
]

_colormap_data = [
    _{self.name}_data,
]

palette = {{
    name: EnhancementPalette.discrete(name=name, listed_colors=data)
    for name, data in zip(_colormap_names, _colormap_data)
}}
"""

    def _generate_segmented_colormap_code(self, invert: bool) -> str:
        color_segment = self._make_color_segment(self.color_table, invert)

        segmented_colors = [
            f"({x:.6f}, ({r:.6f}, {g:.6f}, {b:.6f}))"
            for x, (r, g, b) in color_segment
        ]

        segmented_colors_array = ",\n    ".join(segmented_colors)

        return f"""\
from goesdl.enhancement import EnhancementPalette

_{self.name}_data = [
    {segmented_colors_array}
]

_colormap_names = [
    '{self.name}',
]

_colormap_data = [
    _{self.name}_data,
]

palette = {{
    name: EnhancementPalette.continuous(name=name, color_table=data, ncolors=256)
    for name, data in zip(_colormap_names, _colormap_data)
}}
"""

    @staticmethod
    def _make_color_list(
        color_table: ColorList, invert: bool
    ) -> UniformColorList:
        not_a_listed_color_table = "Not a proper listed colour table"

        if len(color_table) % 2:
            raise ValueError(not_a_listed_color_table)

        listed_color = (
            [(r, g, b) for _, r, g, b in reversed(color_table)]
            if invert
            else [(r, g, b) for _, r, g, b in color_table]
        )

        color_list: UniformColorList = []

        for i in range(0, len(listed_color), 2):
            current_clr = listed_color[i]
            next_clr = listed_color[i + 1]
            color_list.append(current_clr)
            if current_clr != next_clr:
                raise ValueError(not_a_listed_color_table)

        return color_list

    @staticmethod
    def _make_color_segment(
        color_table: ColorList, invert: bool
    ) -> ColorTable:
        return (
            [(1 - j, (r, g, b)) for j, r, g, b in reversed(color_table)]
            if invert
            else [(j, (r, g, b)) for j, r, g, b in color_table]
        )

    @staticmethod
    def _parse_binary_file(
        data: bytes,
    ) -> tuple[ColorList, ColorList, DomainData, str]:
        return ETColorTable.parse_et_table(data)

    @staticmethod
    def _parse_text_file(
        lines: list[str],
    ) -> tuple[ColorList, ColorList, DomainData, str]:
        # Try parse a EU file first (if EU file detected)
        if eu_utility.is_eu_table(lines[0]):
            return EUColorTable.parse_eu_table(lines)

        # Try parse a CPT file
        return CPTColorTable.parse_cpt_table(lines)

    @staticmethod
    def _save_generated_code(path: str | Path, generated_code: str) -> None:
        with open(path, "w", encoding="utf-8") as file:
            file.write(generated_code)

        print(f"Code generated in '{path}'!")
