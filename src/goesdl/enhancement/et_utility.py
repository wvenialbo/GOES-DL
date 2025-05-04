from math import nan
from struct import unpack

from .clr_utility import clr_utility
from .shared import ColorTable, DomainData

WORD_SIZE = 4
NUMBER_OF_WORDS = 817
EXPECTED_SIZE = NUMBER_OF_WORDS * WORD_SIZE

NO_DATA_RGB = nan, 1.0, 0.0, 1.0


class et_utility(clr_utility):

    @classmethod
    def parse_et_table(
        cls, data: bytes
    ) -> tuple[ColorTable, ColorTable, DomainData]:
        # Check file size
        if len(data) != EXPECTED_SIZE:
            raise ValueError(
                f"Invalid ET file size. Expected: {EXPECTED_SIZE} bytes, "
                f"got {len(data)} bytes"
            )

        # Unpack all words as 32-bit big-endian integers
        words = unpack(">817I", data)

        # Extract RGB channels
        red = list(words[1:257])
        green = list(words[257:513])
        blue = list(words[513:769])

        x, domain = cls._normalize_keypoint_values(list(range(256)))

        r, g, b = map(cls._normalize_color_values, (red, green, blue))

        color_table = cls._make_color_table((x, r, g, b))

        stock_table: ColorTable = [
            color_table[0],
            color_table[-1],
            NO_DATA_RGB,
        ]

        return color_table, stock_table, domain
