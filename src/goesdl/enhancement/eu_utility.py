from pathlib import Path
from typing import TextIO

from .clr_utility import clr_utility
from .constants import CM_BGR, CM_RGB
from .shared import (
    ColorList,
    DomainData,
    KeypointList,
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
        color_list: ColorList,
        domain: DomainData,
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
        lines = cls._build_lines(name, color_list, domain, rgb)

        cls._save_to_file(path, lines)

    @staticmethod
    def is_eu_table(header: str) -> bool:
        return EU_SIGNATURE in header

    @classmethod
    def parse_eu_table(
        cls, lines: list[str]
    ) -> tuple[ColorList, DomainData, str]:
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

            # Ignore other header lines
            if ls[0] in EU_KEYWORD:
                continue

            lv = list(map(float, ls))

            j.extend(lv[:2])
            b.extend(lv[2:4])
            g.extend(lv[4:6])
            r.extend(lv[6:8])

        # Adjust colour component ordering if necessary
        if color_model == CM_RGB:
            r, b = b, r

        input_table = cls._make_color_list((j, r, g, b))

        fill_table = cls._fill_in(j)

        full_table = cls._combine_lists(input_table, fill_table)

        color_table, domain = cls._normalize_color_table(full_table)

        name = ""
        if len(lines[0]) > len(EU_SIGNATURE):
            name = lines[0][len(EU_SIGNATURE) + 1 :]
            name = name.strip()

        return color_table, domain, name

    @classmethod
    def to_string(cls, name: str, color_list: ColorList) -> str:
        lines = cls._build_lines(name, color_list, (0.0, 255.0), False)

        return "\n".join(f"{line:<85}" for line in lines)

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

    @staticmethod
    def _adjust_domain(domain: DomainData) -> DomainData:
        xmin, xmax = domain
        return 0, min(xmax - xmin, 255)

    @classmethod
    def _build_lines(
        cls, name: str, color_list: ColorList, domain: DomainData, rgb: bool
    ) -> list[str]:
        lines: list[str] = []

        cls._add_eu_table_header(lines, name, rgb)

        domain = cls._adjust_domain(domain)

        color_list = cls._scale_color_list(color_list, domain)

        cls._create_eu_table(lines, color_list, rgb)

        return lines

    @classmethod
    def _create_eu_table(
        cls, lines: list[str], color_list: ColorList, rgb: bool
    ) -> None:
        if not rgb:
            color_list = [(x, b, g, r) for x, r, g, b in color_list]

        for i in range(0, len(color_list), 2):
            x_lo, b_lo, g_lo, r_lo = map(round, color_list[i])

            x_hi, b_hi, g_hi, r_hi = map(round, color_list[i + 1])

            line = (
                f"{x_lo:>5}{x_hi:>4}{b_lo:>6}{b_hi:>4}"
                f"{g_lo:>6}{g_hi:>4}{r_lo:>6}{r_hi:>4}"
            )

            lines.append(line)

    @classmethod
    def _fill_out(
        cls, original: KeypointList
    ) -> tuple[KeypointList, ColorList]:
        if offset := 255 - original[-1]:
            original = [a + offset for a in original]
        fill_table = cls._fill_in(original)
        return original, fill_table

    @staticmethod
    def _fill_in(original: KeypointList) -> ColorList:
        # Get the actual segment bounds
        actual = [int(j) for j in original]

        # Create the full range of values
        complete = set(range(actual[-1] + 1))

        # Get the actual segments full range
        filled: set[int] = set()
        for i in range(1, len(actual), 2):
            filled.update(range(actual[i - 1], actual[i] + 1))

        # Find the missing indices
        missing = sorted(complete - filled)

        # Group consecutive sequences
        groups: list[list[int]] = []
        current_group: list[int] = []
        for index in missing:
            if not current_group or index == current_group[-1] + 1:
                current_group.append(index)
            else:
                groups.append(current_group)
                current_group = [index]

        if current_group:
            groups.append(current_group)

        # Get each new segment bounds
        new_segments = []
        for segment in groups:
            new_segments.append(segment[0])
            if len(segment) > 1:
                new_segments.append(segment[-1])
            else:
                new_segments.append(segment[0])

        # Create the grayscale tuples for each segment bound
        return [(float(i), float(i), float(i), float(i)) for i in new_segments]

    @classmethod
    def _normalize_color_table(
        cls, color_list: ColorList
    ) -> tuple[ColorList, DomainData]:
        j, r, g, b = cls._make_value_table(color_list)

        # Normalise scale keypoints values
        cls._validate_monotonic_keypoints(j)

        x, domain = cls._normalize_keypoint_values(j)

        # Normalise colour component values
        r, g, b = map(cls._normalize_color_values, (r, g, b))

        color_table = cls._make_color_list((x, r, g, b))

        return color_table, domain

    @classmethod
    def _save_to_file(cls, path: str | Path, lines: list[str]) -> None:
        with open(path, "w", encoding="utf-8", newline="\n") as file:
            cls._write_color_table_file(file, lines)

    @classmethod
    def _scale_color_list(
        cls, color_list: ColorList, domain: DomainData
    ) -> ColorList:
        x, r, g, b = map(list[float], zip(*color_list))

        # Rescale scale keypoints values
        cls._validate_monotonic_keypoints(x)

        j = cls._scale_keypoint_values(x, domain)

        # Rescale colour component values
        r, g, b = map(cls._scale_color_values, (r, g, b))

        # Set the default EU TABLE colour component ordering (BGR)
        return cls._make_color_list((j, r, g, b))

    @staticmethod
    def _write_color_table_file(file: TextIO, lines: list[str]) -> None:
        file.write("".join(f"{line:<85}\n" for line in lines))
