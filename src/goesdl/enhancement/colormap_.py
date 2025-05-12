from types import NoneType

from matplotlib.colors import Colormap, LinearSegmentedColormap, ListedColormap

ColorValue = tuple[int, int, int]
ColorList = list[ColorValue]

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


class DiscreteColormap(BaseColormap):

    def __init__(
        self, name: str, color_list: ColorList, ncolors: int | None = None
    ) -> None:
        self._validate_color_list(color_list)

        normalized_color_list = self._normalize_color_list(color_list)

        is_expected_type = isinstance(ncolors, (int, NoneType))

        if ncolors is None:
            ncolors = len(color_list)

        in_range = 2 <= ncolors <= 256

        if not is_expected_type or not in_range:
            raise ValueError(
                "'ncolors' must be an integer in the range [2, 256] or None"
            )

        colormap = ListedColormap(normalized_color_list, name)

        super().__init__(colormap)


class UniformColormap(BaseColormap):

    def __init__(
        self, name: str, color_list: ColorList, ncolors: int | None = None
    ) -> None:
        self._validate_color_list(color_list)

        normalized_color_list = self._normalize_color_list(color_list)

        is_expected_type = isinstance(ncolors, (int, NoneType))

        if ncolors is None:
            ncolors = len(color_list)

        in_range = 2 <= ncolors <= 256

        if not is_expected_type or not in_range:
            raise ValueError(
                "'ncolors' must be an integer in the range [2, 256] or None"
            )

        colormap = LinearSegmentedColormap.from_list(
            name, normalized_color_list
        )

        super().__init__(colormap)
