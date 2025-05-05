from math import isnan, nan

from .clr_utility import clr_utility
from .constants import (
    CM_CMYK,
    CM_GRAY,
    CM_HSV,
    CM_RGB,
)
from .shared import (
    ColorList,
    DomainData,
    ValueTable,
    ValueTableColumn,
)

CMYKValue = tuple[float, float, float, float]

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
COLOR_MODEL = GMT_CPT_KEYWORD[1]
GMT_CPT_COLOR_MODEL = {CM_CMYK, CM_GRAY, CM_HSV, CM_RGB}

INVALID_COLOR_MODEL = "Invalid colour model"

NO_DATA_RGB = nan, 1.0, 0.0, 1.0


class cpt_utility(clr_utility):

    @classmethod
    def parse_cpt_table(
        cls, lines: list[str]
    ) -> tuple[ColorList, ColorList, DomainData]:
        j: ValueTableColumn = []

        r: ValueTableColumn = []
        g: ValueTableColumn = []
        b: ValueTableColumn = []
        k: ValueTableColumn = []

        cpt_table = j, r, g, b, k

        bg: CMYKValue = nan, nan, nan, nan
        fg: CMYKValue = nan, nan, nan, nan
        nn: CMYKValue = nan, nan, nan, nan

        color_model = CM_RGB

        for line in lines:
            # Split line into list of strings of keywords or values
            ls = line.split()

            if len(ls) <= 1:
                continue

            # Check for alternative colour model
            color_model = cls._extract_color_model(color_model, ls)

            # Extract stock colors
            bg, fg, nn = cls._extract_stock_color(color_model, bg, fg, nn, ls)

            # Ignore other header, comments and footer lines
            if ls[0] in GMT_CPT_KEYWORD:
                continue

            cls._extract_color_range(color_model, cpt_table, ls)

        # The `r`, `g`, and `b` lists are modified in place and contain
        # the normalized colour component intensity values corresponding
        # to the blue, green, and red colour components, respectively;
        # the `k` list is left unchanged since it is used only for CMYK
        # to RGB colorspace conversion.
        color_table, domain = cls._process_cpt_table(color_model, cpt_table)

        stock_table = cls._process_cpt_stock(
            color_model, color_table, (bg, fg, nn)
        )

        return color_table, stock_table, domain

    @classmethod
    def _extract_color_model(cls, color_model: str, ls: list[str]) -> str:
        if ls[0] == GMT_CPT_COMMENT and ls[1] == COLOR_MODEL:
            if ls[-1] not in GMT_CPT_COLOR_MODEL:
                raise ValueError("Unknown colour model")
            color_model = ls[-1]
        return color_model

    @classmethod
    def _extract_color_range(
        cls,
        color_model: str,
        value_table: ValueTable,
        ls: list[str],
    ) -> None:
        j, r, g, b, k = value_table

        lv = list(map(float, ls))

        if color_model == CM_GRAY:
            j.extend(lv[::2])
            r.extend(lv[1::2])

        elif color_model in {CM_HSV, CM_RGB}:
            j.extend(lv[::4])
            r.extend(lv[1::4])
            g.extend(lv[2::4])
            b.extend(lv[3::4])

        elif color_model == CM_CMYK:
            j.extend(lv[::5])
            r.extend(lv[1::5])
            g.extend(lv[2::5])
            b.extend(lv[3::5])
            k.extend(lv[4::5])

        else:
            raise ValueError(INVALID_COLOR_MODEL)

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

    @staticmethod
    def _get_stock_color(color_model: str, ls: list[str]) -> CMYKValue:
        # This handles color_model == CM_GRAY
        r, g, b, k = float(ls[1]), 0.0, 0.0, 0.0

        if color_model in {CM_RGB, CM_HSV, CM_CMYK}:
            g = float(ls[2])
            b = float(ls[3])

            if color_model == CM_CMYK:
                k = float(ls[4])

        elif color_model != CM_GRAY:
            raise ValueError(INVALID_COLOR_MODEL)

        return r, g, b, k

    @classmethod
    def _process_cpt_table(
        cls, color_model: str, values: ValueTable
    ) -> tuple[ColorList, DomainData]:
        j, r, g, b, n = values

        # Normalise scale keypoints values
        cls._validate_monotonic_keypoints(j)

        x, domain = cls._normalize_keypoint_values(j)

        # Normalise colour component values
        if color_model == CM_RGB:
            r, g, b = map(cls._normalize_color_values, (r, g, b))

        # Convert colour model and normalise if necessary
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
            raise ValueError(INVALID_COLOR_MODEL)

        color_table = cls._make_color_list((x, r, g, b))

        return color_table, domain

    @classmethod
    def _process_cpt_stock(
        cls,
        color_model: str,
        color_table: ColorList,
        stock_values: tuple[CMYKValue, ...],
    ) -> ColorList:
        j = [float(i) for i in range(3)]

        r, g, b, k = map(list, zip(*stock_values))

        stok_table, _ = cls._process_cpt_table(color_model, (j, r, g, b, k))

        # Background (colour for values that are less than the defined
        # range)
        if isnan(stok_table[0][1]):
            stok_table[0] = color_table[0]

        # Foreground (colour for values that are greater than the
        # defined range)
        if isnan(stok_table[1][1]):
            stok_table[1] = color_table[-1]

        # No-data colour
        if isnan(stok_table[2][1]):
            stok_table[2] = NO_DATA_RGB

        return stok_table
