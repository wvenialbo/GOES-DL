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

        color_list: ColorList = []
        for line in lines[2:]:
            ls = line.split()
            xrgb = tuple(map(float, [a.strip(",") for a in ls[:4]]))
            color_list.append(cast(ColorListRow, xrgb))

        if ncolors != len(color_list):
            raise ValueError(INVALID_ASTROART_PALETTE_FILE)

        color_table = [tuple(v / 255.0 for v in xrgb) for xrgb in color_list]

        return cast(ColorList, color_table), (0, 255.0)
