from pathlib import Path

from .colormap import ContinuousColormap
from .cpt_utility import cpt_utility
from .eu_utility import eu_utility
from .shared import ColorTable, ContinuousColorTable


class ColormapTable(ContinuousColormap):
    """
    Represent a color enhancement color table.

    This class provides methods to load, parse, and process McIDAS and
    GMT enhancement color tables, creating color segments for Matplotlib
    colormaps.
    """

    def __init__(self, path: str | Path, ncolors: int = 256) -> None:

        color_table, name = self._from_file(path)

        listed_colors = self._make_color_list(color_table)

        super().__init__(name, listed_colors, ncolors)

    @classmethod
    def _from_file(cls, path: str | Path) -> tuple[ColorTable, str]:
        """
        Load a McIDAS or GMT enhancement colour table specification.

        Parse a McIDAS enhancement utility table (EU TABLE) or GMT
        colour palette table (CPT TABLE) text file and create colour
        dictionary for a Matplotlib colormap.

        Parameters
        ----------
        path : str or Path
            Path to the colour table specification text file.

        Returns
        -------
        tuple[ColorTable, str]
            Tuple of colour table and name values.

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
        with open(path, "r", encoding="utf-8") as file:
            lines = file.readlines()

        color_table, name = cls._parse_table(lines)

        return color_table, name

    @staticmethod
    def _make_color_list(color_table: ColorTable) -> ContinuousColorTable:
        gradient_table: ContinuousColorTable = []

        for j, b, g, r in color_table:
            gradient_row = j, (r, g, b)

            gradient_table.append(gradient_row)

        return gradient_table

    @staticmethod
    def _parse_table(lines: list[str]) -> tuple[ColorTable, str]:
        # Try parse a EU file first (if EU file detected)
        if eu_utility.is_eu_table(lines[0]):
            return eu_utility.parse_eu_table(lines)

        # Try parse a CPT file
        return cpt_utility.parse_cpt_table(lines)
