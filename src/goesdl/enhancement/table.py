"""
Provide the EnhacementTable class and related utilities for
creating and manipulating color enhancement tables.
"""

from collections.abc import Sequence
from pathlib import Path
from typing import Literal

from .palette import EnhacementPalette
from .shared import ColorEntry, ColorSegment, DomainData, PaletteData, RGBValue
from .stretching import EnhacementStretching
from .utility import interp, interpx

ColorKey = Literal["red", "green", "blue", "alpha"]
ColorStock = dict[str, RGBValue]
PaletteTable = dict[ColorKey, Sequence[ColorSegment]]


class EnhacementTable:
    """
    Represent a color enhancement table.

    This class provides methods to create an enhancement table from
    stretching and palette data, and to extract sub-palettes.

    Attributes
    ----------
    name : str
        The name or identifier of the enhancement table.
    stock : ColorStock
        The stock color values.
    table : PaletteData
        The palette data containing color segments.
    palette : PaletteTable
        The palette table containing color entries.

    Properties
    ----------
    domain : DomainData
        The input domain containing the minimum and maximum input values.
    extent : DomainData
        The palette domain containing the minimum and maximum values.

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
    stock: ColorStock
    color_table: PaletteTable
    color_data: PaletteData
    palette: EnhacementPalette
    stretching: EnhacementStretching

    def __init__(
        self, palette: EnhacementPalette, stretching: EnhacementStretching
    ) -> None:
        self.name = palette.name
        if stretching.name:
            self.name = f"{self.name} > {stretching.name}"

        self.stock = self._make_stock(palette)
        self.color_data = self._stretch_palette(stretching, palette)
        self.color_table = self._make_colortable(self.color_data)

        self.stretching = stretching
        self.palette = palette

    def extract(self, vmin: float, vmax: float) -> PaletteTable:
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
        tmin, tmax = self.stretching.domain
        trange = tmax - tmin

        vmin = (vmin - tmin) / trange
        vmax = (vmax - tmin) / trange
        cmin = self._interp_color(vmin, self.color_data)
        cmax = self._interp_color(vmax, self.color_data)

        sub_palette: PaletteData = [cmin]
        for entry in self.color_data:
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
            table = [(x, x) for x, _, _, _ in palette.table]
            scale_domain, palette_extent = palette.extent, palette.extent
            stretching = EnhacementStretching(
                "", table, scale_domain, palette_extent
            )

        return cls(palette, stretching)

    @staticmethod
    def _interp_color(x: float, color_data: PaletteData) -> ColorEntry:
        x_pal, b_pal, g_pal, r_pal = zip(*color_data)

        # Linear interpolation between the two points
        b, g, r = (
            interp(x, x_pal, b_pal),
            interp(x, x_pal, g_pal),
            interp(x, x_pal, r_pal),
        )

        return x, b, g, r

    @staticmethod
    def _make_colortable(table: PaletteData) -> PaletteTable:
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

    @staticmethod
    def _make_stock(palette: EnhacementPalette) -> ColorStock:
        bg, fg, nn = palette.stock
        return {"background": bg, "foreground": fg, "nan": nn}

    @staticmethod
    def _normalize_palette(
        vmin: float, vmax: float, sub_palette: PaletteData
    ) -> None:
        vrange = vmax - vmin
        for i, entry in enumerate(sub_palette):
            x, b, g, r = entry
            x = (x - vmin) / vrange
            sub_palette[i] = x, b, g, r

    @staticmethod
    def _stretch_palette(
        stretching: EnhacementStretching, palette: EnhacementPalette
    ) -> PaletteData:
        x_stretch: tuple[float]
        y_stretch: tuple[float]
        y_stretch, x_stretch = zip(*stretching.table)

        linearized_table: PaletteData = []
        for x, b, g, r in palette.table:
            y = interpx(x, x_stretch, y_stretch)
            linearized_table.append((y, b, g, r))

        return linearized_table

    @property
    def domain(self) -> DomainData:
        return self.stretching.domain

    @property
    def extent(self) -> DomainData:
        return self.palette.extent
