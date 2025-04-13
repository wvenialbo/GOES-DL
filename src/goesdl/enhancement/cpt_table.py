import colorsys
import math

from .clr_table import clr_utility
from .constants import (
    BRG_MAX,
    CM_CMYK,
    CM_GRAY,
    CM_HSV,
    CM_RGB,
    CMYK_MAX,
    HSV_MAX,
    HUE_MAX,
    UNNAMED_TABLE,
)
from .shared import CMYKValue, DomainData, PaletteItem, RGBValue, ValueTables

GMT_CPT_KEYWORD = (
    "#",
    "COLOR_MODEL",
    "B",
    "F",
    "N",
    CM_CMYK,
    CM_GRAY,
    CM_HSV,
    CM_RGB,
)
GMT_CPT_COMMENT = GMT_CPT_KEYWORD[0]
GMT_CPT_COLOR_MODEL = {CM_CMYK, CM_GRAY, CM_HSV, CM_RGB}


class cpt_utility(clr_utility):

    @classmethod
    def parse_cpt_table(
        cls, lines: list[str]
    ) -> tuple[PaletteItem, str, DomainData]:
        j: list[float] = []

        r: list[float] = []
        g: list[float] = []
        b: list[float] = []
        k: list[float] = []

        clr_values = r, g, b, k

        cl_nan = float("nan")
        bg: CMYKValue = (cl_nan, cl_nan, cl_nan, cl_nan)
        fg: CMYKValue = (cl_nan, cl_nan, cl_nan, cl_nan)
        nn: CMYKValue = 1.0, 0.0, 1.0, cl_nan

        color_model = CM_RGB

        for line in lines:
            # Split line into list of strings of keywords or values
            ls = line.split()

            # Check for alternative color model
            if line[0] == GMT_CPT_COMMENT and ls[-1] in GMT_CPT_COLOR_MODEL:
                color_model = ls[-1]

            # Extract stock colors
            bg, fg, nn = cls._extract_stock_color(color_model, bg, fg, nn, ls)

            # Ignore header lines
            if ls[0] in GMT_CPT_KEYWORD:
                continue

            cls._extract_color_range(j, clr_values, color_model, ls)

        bg, fg = cls._finalize_stock_colors(clr_values, bg, fg, color_model)

        # The `r`, `g`, and `b` lists are modified in place and contain
        # the normalized color component intensity values corresponding
        # to the blue, green, and red color components, respectively;
        # the `n` list is left unchanged since it is used only for CMYK
        # to RGB colorspace conversion.
        r, g, b = cls._process_cpt_colors(color_model, r, g, b, k)

        extent = j[0], j[-1]

        entries = cls._make_color_entries(j, b, g, r)
        stock = cls._process_cpt_stock(color_model, bg, fg, nn)

        return (entries, stock), UNNAMED_TABLE, extent

    @staticmethod
    def _cmyk_to_rgb(c: float, m: float, y: float, k: float) -> RGBValue:
        b = 1.0 - k / CMYK_MAX
        return (
            (1.0 - c / CMYK_MAX) * b,
            (1.0 - m / CMYK_MAX) * b,
            (1.0 - y / CMYK_MAX) * b,
        )

    @classmethod
    def _extract_color_range(
        cls,
        j: list[float],
        clr_values: ValueTables,
        color_model: str,
        ls: list[str],
    ) -> None:
        r, g, b, k = clr_values

        if color_model == CM_GRAY:
            j.extend((float(ls[0]), float(ls[2])))
            r.extend((float(ls[1]), float(ls[3])))

        elif color_model == CM_CMYK:
            j.extend((float(ls[0]), float(ls[5])))
            r.extend((float(ls[1]), float(ls[6])))
            g.extend((float(ls[2]), float(ls[7])))
            b.extend((float(ls[3]), float(ls[8])))
            k.extend((float(ls[4]), float(ls[9])))

        else:
            j.extend((float(ls[0]), float(ls[4])))
            r.extend((float(ls[1]), float(ls[5])))
            g.extend((float(ls[2]), float(ls[6])))
            b.extend((float(ls[3]), float(ls[7])))

    @classmethod
    def _extract_stock_color(
        cls,
        color_model: str,
        bg: CMYKValue,
        fg: CMYKValue,
        nn: CMYKValue,
        ls: list[str],
    ) -> tuple[CMYKValue, CMYKValue, CMYKValue]:
        if ls[0] == GMT_CPT_KEYWORD[2]:
            bg = cls._get_stock_color(color_model, ls)
        elif ls[0] == GMT_CPT_KEYWORD[3]:
            fg = cls._get_stock_color(color_model, ls)
        elif ls[0] == GMT_CPT_KEYWORD[4]:
            nn = cls._get_stock_color(color_model, ls)
        return bg, fg, nn

    @classmethod
    def _finalize_stock_colors(
        cls,
        clr_values: ValueTables,
        bg: CMYKValue,
        fg: CMYKValue,
        color_model: str,
    ) -> tuple[CMYKValue, CMYKValue]:
        r, g, b, k = clr_values

        if color_model == CM_GRAY:
            bg = (r[0], 0.0, 0.0, 0.0) if math.isnan(bg[0]) else bg
            fg = (r[-1], 0.0, 0.0, 0.0) if math.isnan(fg[0]) else fg

        elif color_model == CM_CMYK:
            bg = (r[0], g[0], b[0], k[0]) if math.isnan(bg[0]) else bg
            fg = (r[-1], g[-1], b[-1], k[-1]) if math.isnan(fg[0]) else fg

        else:
            bg = (r[0], g[0], b[0], 0.0) if math.isnan(bg[0]) else bg
            fg = (r[-1], g[-1], b[-1], 0.0) if math.isnan(fg[0]) else fg

        return bg, fg

    @staticmethod
    def _get_stock_color(color_model: str, ls: list[str]) -> CMYKValue:
        r, g, b, k = float(ls[1]), 0.0, 0.0, 0.0
        if color_model in {CM_RGB, CM_CMYK}:
            g = float(ls[2])
            b = float(ls[3])
            if color_model == CM_CMYK:
                k = float(ls[4])
        return r, g, b, k

    @staticmethod
    def _hsv_to_rgb(h: float, s: float, v: float) -> RGBValue:
        return colorsys.hsv_to_rgb(h / HUE_MAX, s / HSV_MAX, v / HSV_MAX)

    @staticmethod
    def _normalize_grayscale(x: float) -> float:
        return x / BRG_MAX

    @classmethod
    def _process_cpt_colors(
        cls,
        color_model: str,
        r: list[float],
        g: list[float],
        b: list[float],
        n: list[float],
    ) -> ValueTables:
        # Normalize color values
        if color_model == CM_RGB:
            r = list(map(cls._normalize_color, r))
            g = list(map(cls._normalize_color, g))
            b = list(map(cls._normalize_color, b))

        # Convert color model if necessary
        elif color_model == CM_HSV:
            for i, (h, s, v) in enumerate(zip(r, g, b)):
                r[i], g[i], b[i] = cls._hsv_to_rgb(h, s, v)

        elif color_model == CM_CMYK:
            for i, (c, m, y, k) in enumerate(zip(r, g, b, n)):
                r[i], g[i], b[i] = cls._cmyk_to_rgb(c, m, y, k)

        elif color_model == CM_GRAY:
            r = list(map(cls._normalize_grayscale, r))
            g, b = r, r

        else:
            raise ValueError("Invalid color model")

        return r, g, b

    @classmethod
    def _process_cpt_stock(
        cls,
        color_model: str,
        bg: CMYKValue,
        fg: CMYKValue,
        nn: CMYKValue,
    ) -> list[RGBValue]:
        packed = (bg, fg, nn)
        u, v, w, y = zip(*packed)
        r, g, b, k = list(u), list(v), list(w), list(y)

        r, g, b = cls._process_cpt_colors(color_model, r, g, b, k)

        return list(zip(r, g, b))
