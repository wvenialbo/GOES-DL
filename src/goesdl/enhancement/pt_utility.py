from typing import cast

from .clr_utility import clr_utility
from .shared import ColorList, DiscreteColorList, DomainData, RGBValue


class pt_utility(clr_utility):

    @classmethod
    def parse_plain_text(
        cls,
        lines: list[str],
    ) -> tuple[ColorList, DomainData]:
        color_list: DiscreteColorList = []
        for line in lines:
            ls = line.split()
            rgb = tuple(
                c / 255.0 for c in map(float, [a.strip(",") for a in ls[:3]])
            )
            color_list.append(cast(RGBValue, rgb))

        vmax = len(color_list) - 1
        color_table: ColorList = [
            (i / vmax, *rgb) for i, rgb in enumerate(color_list)
        ]

        color_table = cls._combine_lists(color_table, color_table)

        domain = 0.0, float(vmax)

        return color_table, domain
