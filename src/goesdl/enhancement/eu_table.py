from pathlib import Path
from typing import TextIO

from .clr_table import clr_utility
from .constants import CLR_MAX, CM_BGR, CM_RGB, UNNAMED_TABLE
from .shared import (
    ColorEntry,
    DomainData,
    PaletteData,
    PaletteItem,
    RGBValue,
    ValueTables,
)

MCIDAS_EU_SIGNATURE = "EU TABLE"
MCIDAS_EU_KEYWORD = (
    "EU",
    "TABLE",
    "Brightness",
    "Red",
    "Green",
    "Blue",
    "min",
    "max",
    "---",
    "------",
)


class eu_utility(clr_utility):

    @staticmethod
    def add_color_table_header(lines: list[str], name: str, rgb: bool) -> None:
        lines.append(f"{MCIDAS_EU_SIGNATURE} {name.upper()}")
        i, j, k = (3, 4, 5) if rgb else (5, 4, 3)
        lines.append(
            f" {MCIDAS_EU_KEYWORD[2]}"
            f"{MCIDAS_EU_KEYWORD[i]:>6}"
            f"{MCIDAS_EU_KEYWORD[j]:>11}"
            f"{MCIDAS_EU_KEYWORD[k]:>9}"
        )
        hdr = f"{MCIDAS_EU_KEYWORD[6]} {MCIDAS_EU_KEYWORD[7]}"
        lines.append(f"{hdr:>9}{hdr:>10}{hdr:>10}{hdr:>10}")
        hdr = f"{MCIDAS_EU_KEYWORD[8]} {MCIDAS_EU_KEYWORD[8]}"
        lines.append(f"{hdr:>9}{hdr:>10}{hdr:>10}{hdr:>10}")

    @classmethod
    def create_file(
        cls,
        path: str | Path,
        name: str,
        table: PaletteData,
        extent: DomainData,
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
        extent : DomainData
            The palette extent containing the minimum and maximum
            defined values.
        rgb : bool, optional
            Flag indicating if the color model is RGB, by default False.
        """
        lines: list[str] = []

        eu_utility.add_color_table_header(lines, name, rgb)
        cls._create_color_table(lines, table, extent, rgb)

        with open(path, "w", encoding="utf-8", newline="\n") as file:
            cls._write_color_table_file(file, lines)

    @staticmethod
    def is_eu_table(header: str) -> bool:
        return MCIDAS_EU_SIGNATURE in header

    @classmethod
    def _create_color_table(
        cls,
        lines: list[str],
        table: PaletteData,
        extent: DomainData,
        rgb: bool,
    ) -> None:
        x_min, x_max = extent
        x_range = x_max - x_min

        if rgb:
            table = [(x, r, g, b) for x, b, g, r in table]

        for i in range(0, len(table), 2):
            x_lo, b_lo, g_lo, r_lo = cls._get_color_entry(
                table[i],
                x_min,
                x_range,
            )

            x_hi, b_hi, g_hi, r_hi = cls._get_color_entry(
                table[i + 1],
                x_min,
                x_range,
            )

            line = (
                f"{x_lo:>5}{x_hi:>4}{b_lo:>6}{b_hi:>4}"
                f"{g_lo:>6}{g_hi:>4}{r_lo:>6}{r_hi:>4}"
            )

            lines.append(line)

    @classmethod
    def _get_color_entry(
        cls, entry: ColorEntry, x_min: float, x_range: float
    ) -> ColorEntry:
        x_lo, b_lo, g_lo, r_lo = entry

        x_lo = round(x_min + x_lo * x_range)
        b_lo = round(b_lo * CLR_MAX)
        g_lo = round(g_lo * CLR_MAX)
        r_lo = round(r_lo * CLR_MAX)

        return x_lo, b_lo, g_lo, r_lo

    @classmethod
    def parse_eu_table(
        cls, lines: list[str]
    ) -> tuple[PaletteItem, str, DomainData]:
        j: list[float] = []
        b: list[float] = []
        g: list[float] = []
        r: list[float] = []

        color_model = CM_BGR

        for line in lines:
            # Split line into list of strings of keywords or values
            ls = line.split()

            # Check for alternative color model
            if ls[0] == MCIDAS_EU_KEYWORD[2] and ls[1] == MCIDAS_EU_KEYWORD[3]:
                color_model = CM_RGB

            # Ignore header lines
            if ls[0] in MCIDAS_EU_KEYWORD:
                continue

            j.extend((float(ls[0]), float(ls[1])))
            b.extend((float(ls[2]), float(ls[3])))
            g.extend((float(ls[4]), float(ls[5])))
            r.extend((float(ls[6]), float(ls[7])))

        bg = b[0], g[0], r[0]
        fg = b[-1], g[-1], r[-1]
        nn = 1.0, 0.0, 1.0

        b, g, r = cls._process_eu_colors(color_model, b, g, r)

        extent = j[0], j[-1]

        entries = cls._make_color_entries(j, b, g, r)
        stock = cls._process_eu_stock(color_model, bg, fg, nn)

        name = UNNAMED_TABLE
        if len(lines[0]) > len(MCIDAS_EU_SIGNATURE):
            name = lines[0][len(MCIDAS_EU_SIGNATURE) + 1 :]
            name = name.strip()

        return (entries, stock), name, extent

    @classmethod
    def _process_eu_colors(
        cls,
        color_model: str,
        b: list[float],
        g: list[float],
        r: list[float],
    ) -> ValueTables:
        # Normalize color values
        b = list(map(cls._normalize_color, b))
        g = list(map(cls._normalize_color, g))
        r = list(map(cls._normalize_color, r))

        # Convert color model if necessary
        if color_model == CM_RGB:
            r, b = b, r

        return b, g, r

    @classmethod
    def _process_eu_stock(
        cls,
        color_model: str,
        bg: RGBValue,
        fg: RGBValue,
        nn: RGBValue,
    ) -> list[RGBValue]:
        packed = (bg, fg, nn)
        u, v, w = zip(*packed)
        b, g, r = list(u), list(v), list(w)

        b, g, r = cls._process_eu_colors(color_model, b, g, r)

        return list(zip(r, g, b))

    @staticmethod
    def _write_color_table_file(file: TextIO, lines: list[str]) -> None:
        for line in lines:
            file.write(f"{line:<85}\n")
