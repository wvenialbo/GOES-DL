from .constants import CLR_MAX
from .shared import ColorEntry


class clr_utility:

    @classmethod
    def _make_color_entries(
        cls, j: list[float], b: list[float], g: list[float], r: list[float]
    ) -> list[ColorEntry]:
        length = j[-1] - j[0]
        x = [(k - j[0]) / length for k in j]

        return list(zip(x, b, g, r))

    @staticmethod
    def _normalize_color(x: float) -> float:
        return x / CLR_MAX
