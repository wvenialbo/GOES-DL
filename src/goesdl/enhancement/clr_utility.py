from colorsys import hsv_to_rgb

from .constants import (
    BRG_MAX,
    CLR_MAX,
    CMYK_MAX,
    HSV_MAX,
    HUE_MAX,
)
from .shared import (
    ColorList,
    ColorValueList,
    DomainData,
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
    def _make_color_table(cls, values: ValueTable) -> ColorList:
        x, r, g, b = values
        return list(zip(x, r, g, b))

    @staticmethod
    def _normalize_color_values(y: ColorValueList) -> ColorValueList:
        return [k / CLR_MAX for k in y]

    @staticmethod
    def _normalize_grayscale_values(y: ColorValueList) -> ColorValueList:
        return [k / BRG_MAX for k in y]

    @staticmethod
    def _normalize_keypoint_values(
        x: KeypointList,
    ) -> tuple[KeypointList, DomainData]:
        x_min, x_max = tuple(sorted((x[0], x[-1])))
        length = x_max - x_min
        return [(k - x_min) / length for k in x], (x_min, x_max)

    @staticmethod
    def _scale_color_values(y: ColorValueList) -> ColorValueList:
        return [round(k * CLR_MAX) for k in y]

    @staticmethod
    def _scale_keypoint_values(x: KeypointList) -> KeypointList:
        length = len(x) // 2
        print(length, len(x))
        return [round(k * length) for k in x]

    @staticmethod
    def _validate_monotonic_keypoints(x: KeypointList) -> None:
        if len(x) <= 1:
            return

        is_increasing = True
        is_decreasing = True

        for i in range(len(x) - 1):
            k_current = x[i]
            k_next = x[i + 1]

            if k_current > k_next:
                is_increasing = False
            elif k_current < k_next:
                is_decreasing = False

            if not is_increasing and not is_decreasing:
                break

        if not is_increasing and not is_decreasing:
            raise ValueError(
                "Keypoints are expected to increase or decrease monotonically"
            )
