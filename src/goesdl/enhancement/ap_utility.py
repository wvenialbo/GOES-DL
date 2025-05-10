from typing import cast

from .shared import ColorList, ColorListRow, DomainData

AP_KEYWORD = ("astroart", "palette")
AP_SIGNATURE = f"{AP_KEYWORD[0]} {AP_KEYWORD[1]}"

INVALID_ASTROART_PALETTE_FILE = "Invalid Astroart Palette file"


class ap_utility:

    @staticmethod
    def is_ap_table(header: str) -> bool:
        return AP_SIGNATURE in header.lower()

    @classmethod
    def parse_ap_table(
        cls,
        lines: list[str],
    ) -> tuple[ColorList, DomainData]:
        if not cls.is_ap_table(lines[0]):
            raise ValueError("Not an Astroart Palette file")

        try:
            ncolors = int(lines[1].strip())

        except TypeError as error:
            raise ValueError(INVALID_ASTROART_PALETTE_FILE) from error

        indices: set[float] = set()
        raw_color_list: ColorList = []
        for line in lines[2:]:
            ls = line.split()
            xrgb = tuple(map(float, [a.strip(",") for a in ls[:4]]))
            indices.add(xrgb[0])
            raw_color_list.append(cast(ColorListRow, xrgb))

        if ncolors != len(raw_color_list):
            raise ValueError(INVALID_ASTROART_PALETTE_FILE)

        vmin, vmax = min(indices), max(indices)

        if vmin != 0:
            raw_color_list.append((0.0, 0.0, 0.0, 0.0))

        if vmax != 255:
            raw_color_list.append((255.0, 255.0, 255.0, 255.0))

        color_list = [
            tuple(v / 255.0 for v in xrgb) for xrgb in sorted(raw_color_list)
        ]

        color_table = [color_list[0]]
        for color_entry in color_list[1:-1]:
            color_table.extend((color_entry, color_entry))
        color_table.append(color_list[-1])

        return cast(ColorList, color_table), (0, 255.0)
