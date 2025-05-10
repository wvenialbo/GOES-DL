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
from .shared import DomainData, KeypointList, StretchingTable
from .st_stock import st_names, st_stock
from .st_utility import st_utility

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


class EnhancementStretching:
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
    def load(cls, path: str | Path) -> "EnhancementStretching":
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

    def save(self, path: str | Path) -> None:
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
        name = "" if self.name == UNNAMED_TABLE else self.name

        st_utility.create_file(path, name, self.table)

    @property
    def domain(self) -> DomainData:
        first_input = self.table[0][0]
        last_input = self.table[-1][0]
        return (
            (first_input, last_input)
            if first_input < last_input
            else (last_input, first_input)
        )

    @property
    def is_reversed(self) -> bool:
        first_output = self.table[0][1]
        last_output = self.table[-1][1]
        return first_output > last_output

    @property
    def keypoints(self) -> tuple[KeypointList, KeypointList]:
        y_v, x_v = zip(*self.table)

        x_min, x_max = self.range
        xp = [(x_i - x_min) / (x_max - x_min) for x_i in x_v]

        y_min, y_max = self.domain
        yp = [(y_i - y_min) / (y_max - y_min) for y_i in y_v]

        return yp, xp

    @property
    def range(self) -> DomainData:
        first_output = self.table[0][1]
        last_output = self.table[-1][1]
        return (
            (first_output, last_output)
            if first_output < last_output
            else (last_output, first_output)
        )


def get_stmap(stretching_name: str) -> EnhancementStretching:
    if stretching_name not in st_names:
        supported_smaps = "', '".join(st_names)
        raise ValueError(
            f"'{stretching_name}' is not a valid stretching table name, "
            f"supported values are: '{supported_smaps}'"
        )

    stretching_table = st_stock[stretching_name]

    return EnhancementStretching(stretching_name, stretching_table)
