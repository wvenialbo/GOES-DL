ColorValue = tuple[int, int, int]
ColorList = list[ColorValue]


class BaseColormap:

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
            in_range = value < 0 or value > 255

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
