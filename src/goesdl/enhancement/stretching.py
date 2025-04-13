"""
Provide the EnhacementStretching class and related functions
for handling color enhancement stretching mappings.

Classes
-------
EnhacementStretching
    Represent a color enhancement stretching mapping.
"""

from pathlib import Path
from typing import TextIO

from .constants import UNNAMED_TABLE
from .shared import DomainData, StretchingTable

ST_SIGNATURE = "ST TABLE"
ST_KEYWORD = (
    "ST",
    "TABLE",
    "Brightness",
    "Temperature",
    "Color",
    "Index",
    "---",
    "------",
)


class EnhacementStretching:
    """
    Represent a color enhancement stretching mapping.

    Provide methods to create an enhancement stretching instance from a
    file and to normalize the enhancement stretching table.

    Attributes
    ----------
    name : str
        The name of the enhancement stretching table.
    table : StretchingTable
        A list of tuples representing the enhancement stretching table.
        The stretching table containing pairs of (x, y) values.
    domain : tuple[DomainData, DomainData]
        The domain data for the x-axis and y-axis containing the minimum
        and maximum values.

    Methods
    -------
    create_file(path, name, table, domain_x, domain_y)
        Create a file with the enhancement stretching table.
    from_file(path)
        Load a enhancement stretching table specification and create an
        EnhacementStretching instance.
    reverse()
        Reverse the enhancement stretching table.
    save_to_file(path, name)
        Save the enhancement stretching table to a file.
    """

    name: str
    domain: DomainData
    extent: DomainData
    table: StretchingTable

    def __init__(
        self,
        name: str,
        table: StretchingTable,
        scale_domain: DomainData,
        palette_extent: DomainData,
    ) -> None:
        self.name = name
        self.domain = scale_domain
        self.extent = palette_extent
        self.table = table

    @classmethod
    def create_file(
        cls,
        path: str | Path,
        name: str,
        table: StretchingTable,
        domain_x: DomainData,
        domain_y: DomainData,
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
        domain_x : DomainData
            The domain data for the x-axis containing the minimum and
            maximum values.
        domain_y : DomainData
            The domain data for the y-axis containing the minimum and
            maximum values.
        """
        lines: list[str] = []

        cls._add_stretching_table_header(lines, name)
        cls._create_stretching_table(lines, table, domain_x, domain_y)

        with open(path, "w", encoding="utf-8", newline="\n") as file:
            cls._write_stretching_table_file(file, lines)

    @classmethod
    def from_file(cls, path: str | Path) -> "EnhacementStretching":
        """
        Create an EnhacementStretching instance from a file.

        Parameters
        ----------
        path : str or Path
            Path to the file containing the enhancement stretching data.

        Returns
        -------
        EnhacementStretching
            An instance of the EnhacementStretching class.
        """
        with open(path, "r", encoding="utf-8") as file:
            lines = file.readlines()

        table, name = cls._parse_table(lines)

        scale_domain, palette_extent = cls._normalize_table(table)

        return cls(name, table, scale_domain, palette_extent)

    def save_to_file(self, path: str | Path, name: str = "") -> None:
        """
        Save the enhancement stretching table to a file.

        Parameters
        ----------
        path : str or Path
            Path to the file where the enhancement stretching table will
            be saved.
        name : str
            The name of the enhancement stretching table. Override the
            actual name if provided.
        """
        if not name and self.name != UNNAMED_TABLE:
            name = self.name

        self.create_file(path, name, self.table, self.domain, self.extent)

    @staticmethod
    def _add_stretching_table_header(lines: list[str], name: str) -> None:
        lines.extend(
            (
                f"{ST_SIGNATURE} {name.upper()}",
                f" {ST_KEYWORD[3]} {ST_KEYWORD[4]}",
                f"{ST_KEYWORD[2]}  {ST_KEYWORD[5]}",
                f"{ST_KEYWORD[6]:>8}{ST_KEYWORD[6]:>9}",
            )
        )

    @staticmethod
    def _create_stretching_table(
        lines: list[str],
        table: StretchingTable,
        domain_x: DomainData,
        domain_y: DomainData,
    ) -> None:
        x_min, x_max = domain_x
        y_min, y_max = domain_y

        x_range = x_max - x_min
        y_range = y_max - y_min

        for x_i, y_i in table:
            x = round(x_min + x_i * x_range)
            y = round(y_min + y_i * y_range)

            lines.append(f"{x:>8}{y:>9}")

    @classmethod
    def _normalize_table(
        cls, table: StretchingTable
    ) -> tuple[DomainData, DomainData]:
        x_min, y_min = table[0]
        x_max, y_max = table[-1]
        x_scl, y_scl = x_max - x_min, y_max - y_min

        for i, (x, y) in enumerate(table):
            table[i] = ((x - x_min) / x_scl, (y - y_min) / y_scl)

        return (x_min, x_max), (y_min, y_max)

    @staticmethod
    def _parse_table(lines: list[str]) -> tuple[StretchingTable, str]:
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
    def _write_stretching_table_file(file: TextIO, lines: list[str]) -> None:
        for line in lines:
            file.write(f"{line:<85}\n")
