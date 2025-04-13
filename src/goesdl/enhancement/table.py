"""
Provide the EnhacementTable class and related utilities for
creating and manipulating color enhancement tables.
"""

from pathlib import Path

from .palette import EnhacementPalette
from .shared import ColorEntry, DomainData, PaletteTable, RGBValue
from .stretching import EnhacementStretching
from .utility import interp, interpx

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
        self.palette = self._stretch_palette(stretching, palette)
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
        x_pal, b_pal, g_pal, r_pal = zip(*self.palette)

        # Linear interpolation between the two points
        b, g, r = (
            interp(x, x_pal, b_pal),
            interp(x, x_pal, g_pal),
            interp(x, x_pal, r_pal),
        )

        return x, b, g, r

    @staticmethod
    def _stretch_palette(
        stretching: EnhacementStretching, palette: EnhacementPalette
    ) -> PaletteTable:
        x_stretch: tuple[float]
        y_stretch: tuple[float]
        y_stretch, x_stretch = zip(*stretching.table)

        linearized_table: PaletteTable = []
        for x, b, g, r in palette.table:
            y = interpx(x, x_stretch, y_stretch)
            linearized_table.append((y, b, g, r))

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
