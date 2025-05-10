from pathlib import Path
from typing import TextIO

from .constants import UNNAMED_TABLE
from .shared import StretchingTable

ST_KEYWORD = (
    "SU",
    "TABLE",
    "Input",
    "Output",
    "-----",
    "------",
)

ST_SIGNATURE = f"{ST_KEYWORD[0]} {ST_KEYWORD[1]}"


class st_utility:

    @classmethod
    def create_file(
        cls, path: str | Path, name: str, table: StretchingTable
    ) -> None:
        """
        Create a file with the enhancement stretching table.

        Parameters
        ----------
        path : str or Path
            Path to the file where the enhancement stretching table will
            be saved.
        name : str
            The name of the enhancement stretching table.
        table : StretchingTable
            A list of tuples representing the enhancement stretching
            table.
        """
        lines = cls._build_lines(name, table)

        cls._save_to_file(path, lines)

    @classmethod
    def _build_lines(cls, name: str, table: StretchingTable) -> list[str]:
        lines: list[str] = []

        cls._add_stretching_table_header(lines, name)

        cls._create_stretching_table(lines, table)

        return lines

    @classmethod
    def _save_to_file(cls, path: str | Path, lines: list[str]) -> None:
        with open(path, "w", encoding="utf-8", newline="\n") as file:
            cls._write_stretching_table_file(file, lines)

    @classmethod
    def parse_table(cls, lines: list[str]) -> tuple[StretchingTable, str]:
        if ST_SIGNATURE not in lines[0]:
            raise ValueError("Invalid stretching table")

        name = UNNAMED_TABLE

        if len(lines[0]) > len(ST_SIGNATURE):
            name = lines[0][len(ST_SIGNATURE) + 1 :]
            name = name.strip()

        table: StretchingTable = []

        for line in lines:
            ls = line.split()

            if ls[0] in ST_KEYWORD:
                continue

            x, y = map(float, ls)

            table.append((x, y))

        return table, name

    @staticmethod
    def _add_stretching_table_header(lines: list[str], name: str) -> None:
        lines.extend(
            (
                f"{ST_SIGNATURE} {name}",
                f"{ST_KEYWORD[2]:>7}{ST_KEYWORD[3]:>9}",
                f"{ST_KEYWORD[4]:>8}{ST_KEYWORD[5]:>8}",
            )
        )

    @staticmethod
    def _create_stretching_table(
        lines: list[str], table: StretchingTable
    ) -> None:
        lines.extend(f"{x:>8.2f}{round(y):>8d}" for x, y in table)

    @staticmethod
    def _write_stretching_table_file(file: TextIO, lines: list[str]) -> None:
        file.write("".join(f"{line:<85}\n" for line in lines))
