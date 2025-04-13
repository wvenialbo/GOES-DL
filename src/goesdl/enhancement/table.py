"""
Provide the EnhacementTable class and related utilities for
creating and manipulating color enhancement tables.
"""

from pathlib import Path

from .palette import EnhacementPalette
from .shared import ColorEntry, DomainData, PaletteTable, RGBValue
from .stretching import EnhacementStretching

ColorSegment = tuple[float, float, float]
ColorStock = dict[str, RGBValue]
PaletteData = dict[str, list[ColorSegment]]


class EnhacementTable:
    """
    Represent a color enhancement table.

    This class provides methods to create an enhancement table from
    stretching and palette data, and to extract sub-palettes.

    Attributes
    ----------
    domain : DomainData
        The input domain containing the minimum and maximum input values.
    extent : DomainData
        The palette domain containing the minimum and maximum values.
    stock : ColorStock
        The stock color values.
    table : PaletteData
        The palette data containing color segments.
    palette : PaletteTable
        The palette table containing color entries.

    Methods
    -------
    extract(vmin, vmax)
        Extract a sub-palette from the color enhancement table.
    from_file(stretching_path, palette_path)
        Create an EnhacementTable instance from files.
    reverse()
        Reverse the enhancement color table.
    """

    name: str
    domain: DomainData
    extent: DomainData
    stock: ColorStock
    table: PaletteData
    palette: PaletteTable
    stretching_data: EnhacementStretching
    palette_data: EnhacementPalette

    def __init__(
        self, stretching: EnhacementStretching, palette: EnhacementPalette
    ) -> None:
        self.name = palette.name
        if stretching.name:
            self.name = f"{self.name} > {stretching.name}"

        self.domain = stretching.domain
        self.extent = palette.extent

        self.stock = self._make_stock(palette)
        self.palette = self._linearize_palette(stretching, palette)
        self.table = self._make_colortable(self.palette)

        self.stretching_data = stretching
        self.palette_data = palette

    def extract(self, vmin: float, vmax: float) -> PaletteData:
        """
        Extract a sub-palette from the color enhancement table.

        Parameters
        ----------
        vmin : float
            The minimum value for the sub-palette.
        vmax : float
            The maximum value for the sub-palette.

        Returns
        -------
        PaletteData
            The extracted sub-palette data.
        """
        tmin, tmax = self.domain
        trange = tmax - tmin

        vmin = (vmin - tmin) / trange
        vmax = (vmax - tmin) / trange
        cmin = self._interp_color(vmin)
        cmax = self._interp_color(vmax)

        sub_palette: PaletteTable = [cmin]
        for entry in self.palette:
            if entry[0] <= cmin[0] or entry[0] >= cmax[0]:
                continue
            sub_palette.append(entry)

        sub_palette.append(cmax)

        self._normalize_palette(vmin, vmax, sub_palette)

        return self._make_colortable(sub_palette)

    @classmethod
    def from_file(
        cls, palette_path: str | Path, stretching_path: str | Path = ""
    ) -> "EnhacementTable":
        """
        Create an EnhacementTable instance from files.

        Parameters
        ----------
        palette_path : str or Path
            Path to the file containing the enhancement palette data.
        stretching_path : str or Path
            Path to the file containing the enhancement stretching data.

        Returns
        -------
        EnhacementTable
            An instance of the EnhacementTable class.
        """
        palette = EnhacementPalette.from_file(palette_path)

        stretching = None
        if stretching_path:
            stretching = EnhacementStretching.from_file(stretching_path)

        if not stretching:
            table = [(0.0, 0.0), (1.0, 1.0)]
            scale_domain, palette_extent = palette.extent, palette.extent
            stretching = EnhacementStretching(
                "", table, scale_domain, palette_extent
            )

        return cls(stretching, palette)

    def reverse(self) -> "EnhacementTable":
        """
        Reverse the color enhancement table.

        Returns
        -------
        EnhacementTable
            A new instance of the EnhacementTable class with the color
            enhancement table reversed.
        """
        stretching = self.stretching_data.reverse()
        palette = self.palette_data.reverse()

        return EnhacementTable(stretching, palette)

    @staticmethod
    def _make_colortable(table: PaletteTable) -> PaletteData:
        blue: list[ColorSegment] = []
        green: list[ColorSegment] = []
        red: list[ColorSegment] = []

        _, bp, gp, rp = table[0]
        for i, (x, b, g, r) in enumerate(table):
            if i % 2 == 0 and i > 0:
                blue.append((x, bp, b))
                green.append((x, gp, g))
                red.append((x, rp, r))
            else:
                blue.append((x, b, b))
                green.append((x, g, g))
                red.append((x, r, r))
                bp, gp, rp = b, g, r

        return {
            "red": red,
            "green": green,
            "blue": blue,
        }

    def _interp_color(self, x: float) -> ColorEntry:
        if x < self.palette[0][0] or x > self.palette[-1][0]:
            raise ValueError("Value out of range")

        # Find the indices of the two closest points in x
        i = 0
        while i < len(self.palette) - 1 and x >= self.palette[i + 1][0]:
            i += 1

        x0, b0, g0, r0 = self.palette[i]
        if i + 1 < len(self.palette):
            x1, b1, g1, r1 = self.palette[i + 1]
        else:
            x1, b1, g1, r1 = x0 + 1, b0, g0, r0

        # Linear interpolation between the two points
        b, g, r = (
            self._interp_value(x, x0, x1, b0, b1),
            self._interp_value(x, x0, x1, g0, g1),
            self._interp_value(x, x0, x1, r0, r1),
        )

        return x, b, g, r

    @staticmethod
    def _interp_value(
        x: float, x0: float, x1: float, y0: float, y1: float
    ) -> float:
        slope = (y1 - y0) / (x1 - x0)
        return y0 + slope * (x - x0)

    @staticmethod
    def _linearize_palette(
        stretching: EnhacementStretching, palette: EnhacementPalette
    ) -> PaletteTable:
        x: tuple[float]
        y: tuple[float]
        y, x = zip(*stretching.table)
        linearized_table: PaletteTable = []
        for x_i, b, g, r in palette.table:
            # Find the indices of the two closest points in x
            i = 0
            while i < len(x) - 1 and x_i > x[i + 1]:
                i += 1

            # Linear interpolation between the two points
            slope = (y[i + 1] - y[i]) / (x[i + 1] - x[i])
            y_new = y[i] + slope * (x_i - x[i])

            print(y[i], y_new)
            linearized_table.append((y_new, b, g, r))

        return linearized_table

    @staticmethod
    def _make_stock(palette: EnhacementPalette) -> ColorStock:
        bg, fg, nn = palette.stock
        return {"background": bg, "foreground": fg, "nan": nn}

    @staticmethod
    def _normalize_palette(
        vmin: float, vmax: float, sub_palette: PaletteTable
    ) -> None:
        vrange = vmax - vmin
        for i, entry in enumerate(sub_palette):
            x, b, g, r = entry
            x = (x - vmin) / vrange
            sub_palette[i] = x, b, g, r
