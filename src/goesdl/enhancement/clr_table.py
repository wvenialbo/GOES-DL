from colorsys import hsv_to_rgb

from .constants import (
    BRG_MAX,
    CLR_MAX,
    CMYK_MAX,
    HSV_MAX,
    HUE_MAX,
)
from .shared import (
    ColorTable,
    ColorValueList,
    KeypointList,
    RGBValue,
    ValueTable,
)


class clr_utility:

    @staticmethod
    def _cmyk_to_rgb(c: float, m: float, y: float, k: float) -> RGBValue:
        b = 1.0 - k / CMYK_MAX
        return (
            (1.0 - c / CMYK_MAX) * b,
            (1.0 - m / CMYK_MAX) * b,
            (1.0 - y / CMYK_MAX) * b,
        )

    @staticmethod
    def _hsv_to_rgb(h: float, s: float, v: float) -> RGBValue:
        return hsv_to_rgb(h / HUE_MAX, s / HSV_MAX, v / HSV_MAX)

    @classmethod
    def _make_color_table(cls, values: ValueTable) -> ColorTable:
        x, b, g, r = values
        return list(zip(x, b, g, r))

    @staticmethod
    def _normalize_color_values(y: ColorValueList) -> ColorValueList:
        return [k / CLR_MAX for k in y]

    @staticmethod
    def _normalize_grayscale_values(y: ColorValueList) -> ColorValueList:
        return [k / BRG_MAX for k in y]

    @staticmethod
    def _normalize_keypoint_values(x: KeypointList) -> KeypointList:
        x_min = x[0]
        length = x[-1] - x_min
        return [(k - x_min) / length for k in x]

    @staticmethod
    def _scale_color_values(y: ColorValueList) -> ColorValueList:
        return [round(k * CLR_MAX) for k in y]

    @staticmethod
    def _scale_keypoint_values(x: KeypointList) -> KeypointList:
        return [round(k * CLR_MAX) for k in x]
