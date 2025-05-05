from abc import abstractmethod
from pathlib import Path

from .colormap import ContinuousColormap
from .cpt_utility import cpt_utility
from .et_utility import et_utility
from .eu_utility import eu_utility
from .shared import ColorTable, ContinuousColorTable, DomainData

INVALID_ET_FILE = "Invalid McIDAS enhancement table (.ET) file"
INVALID_EU_FILE = "Invalid McIDAS enhancement utility (.EU) file"


class _ColorTable(ContinuousColormap):

    def __init__(self, path: str | Path, ncolors: int = 256) -> None:
        color_table, stock_table, domain, name = self._from_file(path)

        color_list = self._make_color_list(color_table)

        name = name or Path(path).stem

        super().__init__(name, color_list, ncolors)

        self.set_domain(domain)

        under, over, bad = (entry[1:] for entry in stock_table)

        self.set_stock_colors(under, over, bad)

    @abstractmethod
    @classmethod
    def _from_file(
        cls, path: str | Path
    ) -> tuple[ColorTable, ColorTable, DomainData, str]: ...

    @classmethod
    def _from_binary_file(
        cls, path: str | Path
    ) -> tuple[ColorTable, ColorTable, DomainData, str]:
        with open(path, "rb") as file:
            data = file.read()

        return cls._parse_binary_file(data)

    @classmethod
    def _from_text_file(
        cls, path: str | Path
    ) -> tuple[ColorTable, ColorTable, DomainData, str]:
        with open(path, "r", encoding="utf-8") as file:
            lines = file.readlines()

        return cls._parse_text_file(lines)

    @staticmethod
    def _make_color_list(color_table: ColorTable) -> ContinuousColorTable:
        return [(j, (r, g, b)) for j, b, g, r in color_table]

    @abstractmethod
    @staticmethod
    def _parse_binary_file(
        data: bytes,
    ) -> tuple[ColorTable, ColorTable, DomainData, str]: ...

    @abstractmethod
    @staticmethod
    def _parse_text_file(
        lines: list[str],
    ) -> tuple[ColorTable, ColorTable, DomainData, str]: ...


class CPTColorTable(_ColorTable):
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

    def __init__(self, path: str | Path, ncolors: int = 256) -> None:
        color_table, stock_table, domain, _ = self._from_text_file(path)

        color_list = self._make_color_list(color_table)

        name = Path(path).stem

        super().__init__(name, color_list, ncolors)

        self.set_domain(domain)

        under, over, bad = (entry[1:] for entry in stock_table)

        self.set_stock_colors(under, over, bad)

    @staticmethod
    def _parse_text_file(
        lines: list[str],
    ) -> tuple[ColorTable, ColorTable, DomainData, str]:
        try:
            # Try parse a .CPT file
            return *cpt_utility.parse_cpt_table(lines), ""

        except (ValueError, IndexError, TypeError) as error:
            raise ValueError(
                "Invalid GMT colour palette table (.CPT) file"
            ) from error


class ETColorTable(_ColorTable):
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

    def __init__(self, path: str | Path, ncolors: int = 256) -> None:
        color_table, stock_table, domain, _ = self._from_binary_file(path)

        color_list = self._make_color_list(color_table)

        name = Path(path).stem

        super().__init__(name, color_list, ncolors)

        self.set_domain(domain)

        under, over, bad = (entry[1:] for entry in stock_table)

        self.set_stock_colors(under, over, bad)

    @staticmethod
    def _parse_binary_file(
        data: bytes,
    ) -> tuple[ColorTable, ColorTable, DomainData, str]:
        if not et_utility.is_et_table(
            data[:4]
        ) or not et_utility.has_expected_size(data):
            raise ValueError(INVALID_ET_FILE)
        try:
            # Try parse a .ET file
            return *et_utility.parse_et_table(data), ""

        except (ValueError, IndexError, TypeError) as error:
            raise ValueError(INVALID_ET_FILE) from error


class EUColorTable(_ColorTable):
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

    def __init__(self, path: str | Path, ncolors: int = 256) -> None:
        color_table, stock_table, domain, name = self._from_text_file(path)

        color_list = self._make_color_list(color_table)

        name = name or Path(path).stem

        super().__init__(name, color_list, ncolors)

        self.set_domain(domain)

        under, over, bad = (entry[1:] for entry in stock_table)

        self.set_stock_colors(under, over, bad)

    @staticmethod
    def _parse_text_file(
        lines: list[str],
    ) -> tuple[ColorTable, ColorTable, DomainData, str]:
        if not eu_utility.is_eu_table(lines[0]):
            raise ValueError(INVALID_EU_FILE)
        try:
            # Try parse a .EU file
            return eu_utility.parse_eu_table(lines)

        except (ValueError, IndexError, TypeError) as error:
            raise ValueError(INVALID_EU_FILE) from error


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

    def __init__(self, path: str | Path, ncolors: int = 256) -> None:
        color_table, stock_table, domain, name = self._from_text_file(path)

        color_list = self._make_color_list(color_table)

        name = name or Path(path).stem

        super().__init__(name, color_list, ncolors)

        self.set_domain(domain)

        under, over, bad = (entry[1:] for entry in stock_table)

        self.set_stock_colors(under, over, bad)

    @classmethod
    def _from_file(
        cls, path: str | Path
    ) -> tuple[ColorTable, ColorTable, DomainData, str]:
        with open(path, "rb") as file:
            data = file.read()

        if et_utility.is_et_table(data[:4]) and et_utility.has_expected_size(
            data
        ):
            return cls._parse_binary_file(data)

        with open(path, "r", encoding="utf-8") as file:
            lines = file.readlines()

        return cls._parse_text_file(lines)

    @staticmethod
    def _parse_binary_file(
        data: bytes,
    ) -> tuple[ColorTable, ColorTable, DomainData, str]:
        try:
            # Try parse a .ET file
            return *et_utility.parse_et_table(data), ""

        except (ValueError, IndexError, TypeError) as error:
            raise ValueError(INVALID_ET_FILE) from error

    @staticmethod
    def _parse_text_file(
        lines: list[str],
    ) -> tuple[ColorTable, ColorTable, DomainData, str]:
        # Try parse a EU file first (if EU file detected)
        if eu_utility.is_eu_table(lines[0]):
            try:
                # Try parse a .EU file
                return eu_utility.parse_eu_table(lines)

            except (ValueError, IndexError, TypeError) as error:
                raise ValueError(INVALID_EU_FILE) from error

        # Try parse a CPT file
        try:
            # Try parse a .CPT file
            return *cpt_utility.parse_cpt_table(lines), ""

        except (ValueError, IndexError, TypeError) as error:
            raise ValueError(
                "Invalid GMT colour palette table (.CPT) file"
            ) from error
