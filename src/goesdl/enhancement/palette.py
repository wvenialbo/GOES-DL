"""
Provide the EnhacementPalette class for handling color enhancement
palettes.
"""

from pathlib import Path

from .constants import UNNAMED_TABLE
from .cpt_table import cpt_utility
from .eu_table import eu_utility
from .shared import ColorTable, DomainData, PaletteData, PaletteItem


class EnhacementPalette:
    """
    Represent a color enhancement color palette.

    This class provides methods to load, parse, and process McIDAS and
    GMT enhancement color tables, creating color dictionaries for
    Matplotlib colormaps.

    Attributes
    ----------
    name : str
        The name of the enhancement color palette.
    extent : DomainData
        The palette extent containing the minimum and maximum defined
        values.
    table : PaletteData
        The palette data containing color segments.
    stock : ColorStock
        The stock color values.

    Methods
    -------
    create_file(path, name, table, extent, rgb)
        Create a file with the enhancement color palette.
    from_file(path)
        Load a McIDAS or GMT enhancement color palette specification and
        create an EnhacementPalette instance.
    reverse()
        Reverse the enhancement color palette.
    save_to_file(path, name, rgb)
        Save the enhancement color palette.
    """

    name: str
    extent: DomainData
    table: PaletteData
    stock: ColorTable

    def __init__(
        self, name: str, specs: PaletteItem, extent: DomainData
    ) -> None:
        self.name = name
        self.extent = extent
        self.table = specs[0]
        self.stock = specs[1]

    @classmethod
    def from_file(cls, path: str | Path) -> "EnhacementPalette":
        """
        Load a McIDAS or GMT enhancement color table specification.

        Parse a McIDAS enhancement utility table (EU TABLE) or GMT color
        palette table (CPT TABLE) text file and create color dictionary
        for a Matplotlib colormap.

        Parameters
        ----------
        path : str or Path
            Path to the color table specification text file.

        Returns
        -------
        ColorSpec
            Tuple of color table and stock color values.

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

        items, name, extent = cls._parse_table(lines)

        return cls(name, items, extent)

    def save_to_file(
        self, path: str | Path, name: str = "", rgb: bool = False
    ) -> None:
        """
        Save the color table.

        Save the color table to a McIDAS enhancement utility table (EU
        TABLE) or GMT color palette table (CPT TABLE) text file.

        Parameters
        ----------
        path : str or Path
            Path to the file where the color table will be saved.
        name : str
            Name of the color table. Override the actual name if provided.
        rgb : bool, optional
            Flag indicating if the color model is RGB, by default False.
        """
        if not name and self.name != UNNAMED_TABLE:
            name = self.name

        eu_utility.create_file(path, name, self.table, self.extent, rgb)

    @staticmethod
    def _parse_table(lines: list[str]) -> tuple[PaletteItem, str, DomainData]:
        # Try parse a EU file first (if EU file detected)
        if eu_utility.is_eu_table(lines[0]):
            return eu_utility.parse_eu_table(lines)

        # Try parse a CPT file
        return cpt_utility.parse_cpt_table(lines)
