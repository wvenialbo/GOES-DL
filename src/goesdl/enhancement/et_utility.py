from struct import unpack

from .clr_utility import clr_utility
from .shared import ColorList, DomainData

WORD_SIZE = 4
NUMBER_OF_WORDS = 817
EXPECTED_SIZE = NUMBER_OF_WORDS * WORD_SIZE


class et_utility(clr_utility):

    @staticmethod
    def is_et_table(header: bytes) -> bool:
        return header == b"\x80\x80\x80\x80"

    @staticmethod
    def has_expected_size(data: bytes) -> bool:
        return len(data) == EXPECTED_SIZE

    @classmethod
    def parse_et_table(cls, data: bytes) -> tuple[ColorList, DomainData]:
        # Unpack all words as 32-bit big-endian integers
        words: tuple[int, ...] = unpack(">817I", data)

        # Extract RGB channels
        red = [float(x) for v in words[1:257] for x in (v, v)]
        green = [float(x) for v in words[257:513] for x in (v, v)]
        blue = [float(x) for v in words[513:769] for x in (v, v)]

        # Normalise RGB channels
        r, g, b = map(cls._normalize_color_values, (red, green, blue))

        # Create and normalise keypoints
        keys = [float(x) for v in range(256) for x in (v, v)]

        x, domain = cls._normalize_keypoint_values(keys)

        # Create colour table
        color_table = cls._make_color_list((x, r, g, b))

        return color_table, domain
