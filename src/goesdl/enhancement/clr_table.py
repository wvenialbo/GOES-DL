from .constants import CLR_MAX
from .shared import ColorTable


class clr_utility:

    @classmethod
    def _make_color_table(
        cls, x: list[float], b: list[float], g: list[float], r: list[float]
    ) -> ColorTable:
        return list(zip(x, b, g, r))

    @staticmethod
    def _normalize_colors(y: list[float]) -> list[float]:
        return [k / CLR_MAX for k in y]

    @staticmethod
    def _normalize_values(x: list[float]) -> list[float]:
        x_min = x[0]
        length = x[-1] - x_min
        return [(k - x_min) / length for k in x]
