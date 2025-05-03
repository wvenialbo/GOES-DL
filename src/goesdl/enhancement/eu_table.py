from pathlib import Path
from typing import TextIO

from .clr_table import clr_utility
from .constants import CM_BGR, CM_RGB, UNNAMED_COLORMAP
from .shared import (
    ColorTable,
    ValueTable,
    ValueTableColumn,
)

EU_KEYWORD = (
    "EU",
    "TABLE",
    "Brightness",
    "Red",
    "Green",
    "Blue",
    "min",
    "max",
    "---",
)

EU_SIGNATURE = f"{EU_KEYWORD[0]} {EU_KEYWORD[1]}"


class eu_utility(clr_utility):

    @classmethod
    def create_file(
        cls,
        path: str | Path,
        name: str,
        table: ColorTable,
        rgb: bool = False,
    ) -> None:
        """
        Create a file with the color table.

        Parameters
        ----------
        path : str or Path
            Path to the file where the color table will be saved.
        name : str
            The name of the color table.
        table : PaletteTable
            The color table data.
        rgb : bool, optional
            Flag indicating if the color model is RGB, by default False.
        """
        lines: list[str] = []

        cls._add_eu_table_header(lines, name, rgb)

        cls._create_eu_table(lines, table, rgb)

        with open(path, "w", encoding="utf-8", newline="\n") as file:
            cls._write_color_table_file(file, lines)

    @staticmethod
    def is_eu_table(header: str) -> bool:
        return EU_SIGNATURE in header

    @classmethod
    def scale_color_table(cls, values: ValueTable) -> ColorTable:
        x, b, g, r = values

        # Scale keypoints values
        x = cls._scale_keypoint_values(x)

        # Normalise colour component values
        b = cls._scale_color_values(b)
        g = cls._scale_color_values(g)
        r = cls._scale_color_values(r)

        return list(zip(x, b, g, r))

    @classmethod
    def parse_eu_table(cls, lines: list[str]) -> tuple[ColorTable, str]:
        j: ValueTableColumn = []

        b: ValueTableColumn = []
        g: ValueTableColumn = []
        r: ValueTableColumn = []

        color_model = CM_BGR

        for line in lines:
            # Split line into list of strings of keywords or values
            ls = line.split()

            # Check for alternative colour model
            if ls[0] == EU_KEYWORD[2] and ls[1] == EU_KEYWORD[3]:
                color_model = CM_RGB

            # Ignore header lines
            if ls[0] in EU_KEYWORD:
                continue

            j.extend((float(ls[0]), float(ls[1])))
            b.extend((float(ls[2]), float(ls[3])))
            g.extend((float(ls[4]), float(ls[5])))
            r.extend((float(ls[6]), float(ls[7])))

        # Convert color model if necessary
        if color_model == CM_RGB:
            r, b = b, r

        color_table = cls._normalize_color_table((j, b, g, r))

        name = UNNAMED_COLORMAP
        if len(lines[0]) > len(EU_SIGNATURE):
            name = lines[0][len(EU_SIGNATURE) + 1 :]
            name = name.strip()

        return color_table, name

    @staticmethod
    def _add_eu_table_header(lines: list[str], name: str, rgb: bool) -> None:
        lines.append(f"{EU_SIGNATURE} {name}")
        i, j, k = (3, 4, 5) if rgb else (5, 4, 3)
        lines.append(
            f" {EU_KEYWORD[2]}"
            f"{EU_KEYWORD[i]:>6}"
            f"{EU_KEYWORD[j]:>11}"
            f"{EU_KEYWORD[k]:>9}"
        )
        hdr = f"{EU_KEYWORD[6]} {EU_KEYWORD[7]}"
        lines.append(f"{hdr:>9}{hdr:>10}{hdr:>10}{hdr:>10}")
        hdr = f"{EU_KEYWORD[8]} {EU_KEYWORD[8]}"
        lines.append(f"{hdr:>9}{hdr:>10}{hdr:>10}{hdr:>10}")

    @classmethod
    def _create_eu_table(
        cls, lines: list[str], table: ColorTable, rgb: bool
    ) -> None:
        if rgb:
            table = [(x, r, g, b) for x, b, g, r in table]

        for i in range(0, len(table), 2):
            x_lo, b_lo, g_lo, r_lo = map(round, table[i])

            x_hi, b_hi, g_hi, r_hi = map(round, table[i + 1])

            if x_lo == x_hi:
                continue

            line = (
                f"{x_lo:>5}{x_hi:>4}{b_lo:>6}{b_hi:>4}"
                f"{g_lo:>6}{g_hi:>4}{r_lo:>6}{r_hi:>4}"
            )

            lines.append(line)

    @classmethod
    def _normalize_color_table(cls, values: ValueTable) -> ColorTable:
        x, b, g, r = values

        # Normalise keypoints values
        x = cls._normalize_keypoint_values(x)

        # Normalise colour component values
        b = cls._normalize_color_values(b)
        g = cls._normalize_color_values(g)
        r = cls._normalize_color_values(r)

        return cls._make_color_table((x, b, g, r))

    @staticmethod
    def _write_color_table_file(file: TextIO, lines: list[str]) -> None:
        file.write("".join(f"{line:<85}\n" for line in lines))
