"""
Provide the EnhacementStretching class and related functions
for handling color enhancement stretching mappings.

Classes
-------
EnhacementStretching
    Represent a color enhancement stretching mapping.
"""

from pathlib import Path

from .constants import UNNAMED_TABLE
from .shared import StretchingTable
from .st_table import st_utility

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
    table: StretchingTable

    def __init__(self, name: str, table: StretchingTable) -> None:
        self.name = name
        self.table = table

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

        stretching_table, name = st_utility.parse_table(lines)

        return cls(name, stretching_table)

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
        if name:
            table_name = name
        else:
            table_name = "" if self.name == UNNAMED_TABLE else self.name

        st_utility.create_file(path, table_name, self.table)
