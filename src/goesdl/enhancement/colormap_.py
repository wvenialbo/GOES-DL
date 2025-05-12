from types import NoneType

from matplotlib.colors import Colormap, LinearSegmentedColormap, ListedColormap

ColorValue = tuple[int, int, int]
ColorList = list[ColorValue]

ColorPoint = tuple[int, ColorValue]
ColorTable = list[ColorPoint]

UniformColorValue = tuple[float, float, float]
UniformColorList = list[UniformColorValue]


class BaseColormap:

    colormap: Colormap

    def __init__(self, colormap: Colormap) -> None:
        self.colormap = colormap

    @staticmethod
    def _validate_color_list(color_list: ColorList) -> None:
        ncolors = len(color_list)

        if ncolors:
            raise ValueError("Colour list can not be empty")

        if ncolors > 256:
            raise ValueError("Colour list can not have more than 256 colours")

        for n, entry in enumerate(color_list):
            ncomponents = len(entry)
            if ncomponents != 3:
                raise ValueError(
                    "Entries in colour list must have 3 components, "
                    f"entry #{n} have {ncomponents} components"
                )

        expanded_list: list[int] = [v for entry in color_list for v in entry]
        for n, value in enumerate(expanded_list):
            is_integer = isinstance(value, int)
            in_range = 0 <= value <= 255

            if not is_integer:
                raise ValueError(
                    f"Colour components must be integers, component #{n%3} "
                    f"in entry #{n // 3} is of type {type(value)}"
                )

            if not in_range:
                raise ValueError(
                    "Entries in colour list must be integers in the "
                    f"range [0, 255], component #{n%3} in entry #{n//3} "
                    f"has value={value}"
                )

    @classmethod
    def _normalize_color_list(cls, color_list: ColorList) -> UniformColorList:
        try:
            return list(map(cls._normalize_color, color_list))

        except (IndexError, TypeError, ValueError) as error:
            raise ValueError(f"Invalid color list: {error}") from error

    @staticmethod
    def _normalize_color(rgb_value: ColorValue) -> UniformColorValue:
        red, green, blue = map(lambda x: x / 255.0, rgb_value)
        return red, green, blue


class _ListBasedColormap(BaseColormap):

    def _init_color_list(self, color_list: ColorList) -> UniformColorList:
        self._validate_color_list(color_list)

        return self._normalize_color_list(color_list)

    def _init_data(
        self, color_list: ColorList, ncolors: int | None
    ) -> tuple[UniformColorList, int]:
        normalized_color_list = self._init_color_list(color_list)

        ncolors = self._init_ncolors(ncolors, len(color_list))

        return normalized_color_list, ncolors

    @staticmethod
    def _init_ncolors(ncolors: int | None, list_size: int) -> int:
        is_expected_type = isinstance(ncolors, (int, NoneType))

        if ncolors is None:
            ncolors = list_size

        in_range = 2 <= ncolors <= 256

        if not is_expected_type or not in_range:
            raise ValueError(
                "'ncolors' must be an integer in the range [2, 256] or None"
            )

        return ncolors


class DiscreteColormap(_ListBasedColormap):

    def __init__(
        self, name: str, color_list: ColorList, ncolors: int | None = None
    ) -> None:
        normalized_color_list, ncolors = self._init_data(color_list, ncolors)

        colormap = ListedColormap(normalized_color_list, name, N=ncolors)

        super().__init__(colormap)

    @staticmethod
    def _create_color_table(color_list: ColorList) -> ColorTable:
        ncolors = len(color_list)
        width = 256 / ncolors

        i = 0
        location = 0.0
        color_table: ColorTable = []

        while location <= 255:
            begin = round(location)
            location += width
            end = round(location) - 1
            first = begin, color_list[i]
            last = end, color_list[i]

            color_table.extend((first, last))

        return color_table


class UniformColormap(_ListBasedColormap):

    def __init__(
        self, name: str, color_list: ColorList, ncolors: int | None = None
    ) -> None:
        normalized_color_list, ncolors = self._init_data(color_list, ncolors)

        colormap = LinearSegmentedColormap.from_list(
            name, normalized_color_list, N=ncolors
        )

        super().__init__(colormap)

    @staticmethod
    def _create_color_table(color_list: ColorList) -> ColorTable:
        max_index = len(color_list) - 1

        color_table: ColorTable = []

        for i in range(max_index):
            j = i + 1
            begin = round(255 * i / max_index)
            end = round(255 * j / max_index)
            first = begin, color_list[i]
            last = end, color_list[j]

            color_table.extend((first, last))

        return color_table
