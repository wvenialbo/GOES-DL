import contextlib
from pathlib import Path

from .colortable import (
    CPTColorTable,
    ETColorTable,
    EUColorTable,
    PlainColorTable,
)
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
        self, path: str | Path, prec: int = 6, invert: bool = False
    ) -> None:
        generated_code = self._generate_listed_colormap_code(prec, invert)

        self._save_generated_code(path, generated_code)

    def save_as_segmented_colormap(
        self, path: str | Path, prec: int = 6, invert: bool = False
    ) -> None:
        generated_code = self._generate_segmented_colormap_code(prec, invert)

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

    def _generate_listed_colormap_code(self, prec: int, invert: bool) -> str:
        color_list = self._make_color_list(
            self.color_table, self.domain, invert
        )

        listed_colors = [
            f"({', '.join((f'{c:{prec+2}.{prec}f}' for c in rgb))})"
            for rgb in color_list
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

    def _generate_segmented_colormap_code(
        self, prec: int, invert: bool
    ) -> str:
        color_segment = self._make_color_segment(self.color_table, invert)

        segmented_colors = [
            f"({x:{prec+2}.{prec}f}, "
            f"({', '.join((f'{c:{prec+2}.{prec}f}' for c in rgb))}))"
            for x, rgb in color_segment
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
    name: EnhancementPalette.continuous(name=name, color_table=data)
    for name, data in zip(_colormap_names, _colormap_data)
}}
"""

    @staticmethod
    def _make_color_list(
        color_list: ColorList, domain: DomainData, invert: bool
    ) -> UniformColorList:
        not_a_listed_color_table = "Not a proper listed colour table"

        # Verify that the colour list have an even number of entries
        if len(color_list) % 2:
            raise ValueError(not_a_listed_color_table)

        vmin, vmax = domain
        length = vmax - vmin
        cp = [round(vmin + k * length) for k, _, _, _ in color_list]

        # Verify that all segments have the same separation
        separation: set[int] = set()
        for i in range(2, len(cp), 2):
            j = cp[i - 2]
            k = cp[i]
            separation.add(k - j)

        if len(separation) > 1 or list(separation)[0] != 1:
            raise ValueError(not_a_listed_color_table)

        # Verify that all segments have the same width
        width: set[float] = set()
        for i in range(1, len(cp), 2):
            j = cp[i - 1]
            k = cp[i]
            width.add(k - j)

        if len(width) > 1:
            raise ValueError(not_a_listed_color_table)

        listed_color = (
            [(r, g, b) for _, r, g, b in reversed(color_list)]
            if invert
            else [(r, g, b) for _, r, g, b in color_list]
        )

        # Create the colour list
        uniform_list: UniformColorList = []

        for i in range(0, len(listed_color), 2):
            current_clr = listed_color[i]
            next_clr = listed_color[i + 1]
            # Verify that the segment is not a colour gradient
            if current_clr != next_clr:
                raise ValueError(not_a_listed_color_table)
            uniform_list.append(current_clr)

        return uniform_list

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
        # Try parse a .EU file first (if EU file detected)
        if eu_utility.is_eu_table(lines[0]):
            return EUColorTable.parse_eu_table(lines)

        # Try parse a .CPT file
        with contextlib.suppress(ValueError):
            return CPTColorTable.parse_cpt_table(lines)

        # Try parse a .TXT file
        try:
            return PlainColorTable.parse_plain_table(lines)

        except ValueError as error:
            raise ValueError(
                "Invalid or unsupported colour table file"
            ) from error

    @staticmethod
    def _save_generated_code(path: str | Path, generated_code: str) -> None:
        with open(path, "w", encoding="utf-8") as file:
            file.write(generated_code)

        print(f"Code generated in '{path}'!")
