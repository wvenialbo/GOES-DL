from .constants import CLR_MAX
from .shared import ColorEntry


class clr_utility:

    @classmethod
    def _make_color_entries(
        cls, x: list[float], b: list[float], g: list[float], r: list[float]
    ) -> list[ColorEntry]:
        return list(zip(x, b, g, r))

    @staticmethod
    def _normalize_colors(y: list[float]) -> list[float]:
        return [k / CLR_MAX for k in y]

    @staticmethod
    def _normalize_values(j: list[float]) -> list[float]:
        length = j[-1] - j[0]
        return [(k - j[0]) / length for k in j]
