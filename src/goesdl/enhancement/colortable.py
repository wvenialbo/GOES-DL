from abc import ABC, abstractmethod
from contextlib import suppress
from pathlib import Path

from .colormap import BaseColormap
from .constants import NO_DATA_RGB
from .cpt_utility import cpt_utility
from .et_utility import et_utility
from .eu_utility import eu_utility
from .pt_utility import pt_utility
from .shared import ColorList, ColorTable, DomainData

INVALID_ET_FILE = "Invalid McIDAS enhancement table (.ET) file"
INVALID_EU_FILE = "Invalid McIDAS enhancement utility (.EU) file"


class _ColorTable(ABC, BaseColormap):

    def __init__(
        self, path: str | Path, ncolors: int = 256, invert: bool = False
    ) -> None:
        color_list, stock_table, domain, name = self._from_file(path)

        color_table = self._make_color_table(color_list, invert)

        name = name or Path(path).stem

        super().__init__(name, color_table, [], ncolors)

        self.set_domain(domain)

        under, over, bad = (entry[1:] for entry in stock_table)

        self.set_stock_colors(under, over, bad)

    @classmethod
    @abstractmethod
    def _from_file(
        cls, path: str | Path
    ) -> tuple[ColorList, ColorList, DomainData, str]: ...

    @staticmethod
    def _make_color_table(color_list: ColorList, invert: bool) -> ColorTable:
        if invert:
            return [(1 - j, (r, g, b)) for j, r, g, b in reversed(color_list)]
        else:
            return [(j, (r, g, b)) for j, r, g, b in color_list]

    @staticmethod
    def _create_stock_colors(color_table: ColorList) -> ColorList:
        return [color_table[0], color_table[-1], NO_DATA_RGB]


class _BinaryColorTable(_ColorTable):

    @classmethod
    def _from_file(
        cls, path: str | Path
    ) -> tuple[ColorList, ColorList, DomainData, str]:
        with open(path, "rb") as file:
            data = file.read()

        return cls._parse_binary_file(data)

    @classmethod
    @abstractmethod
    def _parse_binary_file(
        cls, data: bytes
    ) -> tuple[ColorList, ColorList, DomainData, str]: ...


class _TextBasedColorTable(_ColorTable):

    @classmethod
    def _from_file(
        cls, path: str | Path
    ) -> tuple[ColorList, ColorList, DomainData, str]:
        with open(path, "r", encoding="utf-8") as file:
            lines = file.readlines()

        return cls._parse_text_file(lines)

    @classmethod
    @abstractmethod
    def _parse_text_file(
        cls, lines: list[str]
    ) -> tuple[ColorList, ColorList, DomainData, str]: ...


class CPTColorTable(_TextBasedColorTable):
    """
    Represent a GMT text based colour palette table.

    This class provides methods to load, parse, and process GMT text
    based colour palette tables (CPT).

    Notes
    -----
    The Generic Mapping Tools (GMT) is an open-source collection of
    tools for manipulating geographic and Cartesian data sets and
    producing PostScript illustrations ranging from simple x-y plots
    through maps to complex 3D perspective views.

    - https://www.generic-mapping-tools.org/
    """

    @classmethod
    def _parse_text_file(
        cls, lines: list[str]
    ) -> tuple[ColorList, ColorList, DomainData, str]:
        return cls.parse_cpt_table(lines)

    @staticmethod
    def parse_cpt_table(
        lines: list[str],
    ) -> tuple[ColorList, ColorList, DomainData, str]:
        try:
            # Try parse a .CPT file
            return *cpt_utility.parse_cpt_table(lines), ""

        except (ValueError, IndexError, TypeError) as error:
            raise ValueError(
                "Invalid GMT colour palette table (.CPT) file"
            ) from error


class ETColorTable(_BinaryColorTable):
    """
    Represent a McIDAS binary enhancement colour table.

    This class provides methods to load, parse, and process McIDAS
    enhancement utility binary colour table (.ET) files.

    Notes
    -----
    The Man computer Interactive Data Access System (McIDAS) is a
    research quality suite of applications used for decoding, analyzing,
    and displaying meteorological data developed by the University of
    Wisconsin-Madison Space Science and Engineering Center (UWisc/SSEC).

    - https://www.ssec.wisc.edu/mcidas/
    - https://www.unidata.ucar.edu/software/mcidas/
    """

    @classmethod
    def _parse_binary_file(
        cls, data: bytes
    ) -> tuple[ColorList, ColorList, DomainData, str]:
        if not et_utility.is_et_table(
            data[:4]
        ) or not et_utility.has_expected_size(data):
            raise ValueError(INVALID_ET_FILE)

        return cls.parse_et_table(data)

    @classmethod
    def parse_et_table(
        cls, data: bytes
    ) -> tuple[ColorList, ColorList, DomainData, str]:
        try:
            # Try parse a .ET file
            color_list, domain = et_utility.parse_et_table(data)
            stock_list = cls._create_stock_colors(color_list)
            return color_list, stock_list, domain, ""

        except (ValueError, IndexError, TypeError) as error:
            raise ValueError(INVALID_ET_FILE) from error


class EUColorTable(_TextBasedColorTable):
    """
    Represent a McIDAS text based enhancement colour table.

    This class provides methods to load, parse, and process McIDAS text
    based enhancement utility colour tables (EU TABLE).

    Notes
    -----
    The Man computer Interactive Data Access System (McIDAS) is a
    research quality suite of applications used for decoding, analyzing,
    and displaying meteorological data developed by the University of
    Wisconsin-Madison Space Science and Engineering Center (UWisc/SSEC).

    - https://www.ssec.wisc.edu/mcidas/
    - https://www.unidata.ucar.edu/software/mcidas/
    """

    @classmethod
    def _parse_text_file(
        cls, lines: list[str]
    ) -> tuple[ColorList, ColorList, DomainData, str]:
        if not eu_utility.is_eu_table(lines[0]):
            raise ValueError(INVALID_EU_FILE)

        return cls.parse_eu_table(lines)

    @classmethod
    def parse_eu_table(
        cls, lines: list[str]
    ) -> tuple[ColorList, ColorList, DomainData, str]:
        try:
            # Try parse a .EU file
            color_list, domain, name = eu_utility.parse_eu_table(lines)
            stock_list = cls._create_stock_colors(color_list)
            return color_list, stock_list, domain, name

        except (ValueError, IndexError, TypeError) as error:
            raise ValueError(INVALID_EU_FILE) from error


class PlainColorTable(_TextBasedColorTable):
    """
    Represent a plaint text based colour palette table.
    """

    @classmethod
    def _parse_text_file(
        cls, lines: list[str]
    ) -> tuple[ColorList, ColorList, DomainData, str]:
        return cls.parse_plain_table(lines)

    @classmethod
    def parse_plain_table(
        cls,
        lines: list[str],
    ) -> tuple[ColorList, ColorList, DomainData, str]:
        try:
            # Try parse a .TXT file
            color_list, domain = pt_utility.parse_plain_text(lines)
            stock_list = cls._create_stock_colors(color_list)
            return color_list, stock_list, domain, ""

        except (ValueError, IndexError, TypeError) as error:
            raise ValueError("Invalid plain-text colour table file") from error


class ColormapTable(_ColorTable):
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

    @classmethod
    def _parse_binary_file(
        cls, data: bytes
    ) -> tuple[ColorList, ColorList, DomainData, str]:
        return ETColorTable.parse_et_table(data)

    @classmethod
    def _parse_text_file(
        cls, lines: list[str]
    ) -> tuple[ColorList, ColorList, DomainData, str]:
        # Try parse a .EU file first (if EU file detected)
        if eu_utility.is_eu_table(lines[0]):
            return EUColorTable.parse_eu_table(lines)

        # Try parse a .CPT file
        with suppress(ValueError):
            return CPTColorTable.parse_cpt_table(lines)

        # Try parse a .TXT file
        try:
            return PlainColorTable.parse_plain_table(lines)

        except ValueError as error:
            raise ValueError(
                "Invalid or unsupported colour table file"
            ) from error
