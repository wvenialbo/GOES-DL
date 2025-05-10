from typing import cast

from .shared import ColorList, DiscreteColorList, DomainData, RGBValue


class pt_utility:

    @staticmethod
    def parse_plain_text(
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
        domain = 0.0, float(vmax)

        return color_table, domain
