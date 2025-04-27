from .constants import BRG_MAX, CLR_MAX
from .shared import ColorTable, ColorValueList, KeypointList, ValueTable


class clr_utility:

    @classmethod
    def _make_color_table(cls, values: ValueTable) -> ColorTable:
        x, b, g, r = values
        return list(zip(x, b, g, r))

    @staticmethod
    def _normalize_color_values(y: ColorValueList) -> ColorValueList:
        return [k / CLR_MAX for k in y]

    @staticmethod
    def _normalize_grayscale(y: ColorValueList) -> ColorValueList:
        return [k / BRG_MAX for k in y]

    @staticmethod
    def _normalize_values(x: KeypointList) -> KeypointList:
        x_min = x[0]
        length = x[-1] - x_min
        return [(k - x_min) / length for k in x]
