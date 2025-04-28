import colorsys

from .clr_table import clr_utility
from .constants import (
    CM_CMYK,
    CM_GRAY,
    CM_HSV,
    CM_RGB,
    CMYK_MAX,
    HSV_MAX,
    HUE_MAX,
    UNNAMED_COLORMAP,
)
from .shared import ColorTable, RGBValue, ValueTable, ValueTableColumn

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
    def parse_cpt_table(cls, lines: list[str]) -> tuple[ColorTable, str]:
        j: ValueTableColumn = []

        r: ValueTableColumn = []
        g: ValueTableColumn = []
        b: ValueTableColumn = []
        k: ValueTableColumn = []

        input_table = j, r, g, b, k

        color_model = CM_RGB

        for line in lines:
            # Split line into list of strings of keywords or values
            ls = line.split()

            # Check for alternative colour model
            if line[0] == GMT_CPT_COMMENT and ls[-1] in GMT_CPT_COLOR_MODEL:
                color_model = ls[-1]

            # Ignore header lines
            if ls[0] in GMT_CPT_KEYWORD:
                continue

            cls._extract_color_range(input_table, color_model, ls)

        # The `r`, `g`, and `b` lists are modified in place and contain
        # the normalized colour component intensity values corresponding
        # to the blue, green, and red colour components, respectively;
        # the `n` list is left unchanged since it is used only for CMYK
        # to RGB colorspace conversion.
        value_table = cls._process_cpt_colors(color_model, (j, r, g, b, k))

        color_table = cls._make_color_table(value_table)

        return color_table, UNNAMED_COLORMAP.lower()

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
        value_table: ValueTable,
        color_model: str,
        ls: list[str],
    ) -> None:
        j, r, g, b, k = value_table

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

    @staticmethod
    def _hsv_to_rgb(h: float, s: float, v: float) -> RGBValue:
        return colorsys.hsv_to_rgb(h / HUE_MAX, s / HSV_MAX, v / HSV_MAX)

    @classmethod
    def _process_cpt_colors(
        cls, color_model: str, values: ValueTable
    ) -> ValueTable:
        j, r, g, b, n = values

        # Normalise scale values
        x = cls._normalize_keypoint_values(j)

        # Normalize colour values
        if color_model == CM_RGB:
            r = cls._normalize_color_values(r)
            g = cls._normalize_color_values(g)
            b = cls._normalize_color_values(b)

        # Convert colour model if necessary
        elif color_model == CM_HSV:
            for i, (h, s, v) in enumerate(zip(r, g, b)):
                r[i], g[i], b[i] = cls._hsv_to_rgb(h, s, v)

        elif color_model == CM_CMYK:
            for i, (c, m, y, k) in enumerate(zip(r, g, b, n)):
                r[i], g[i], b[i] = cls._cmyk_to_rgb(c, m, y, k)

        elif color_model == CM_GRAY:
            r = cls._normalize_grayscale_values(r)
            g, b = r, r

        else:
            raise ValueError("Invalid colour model")

        return x, b, g, r
