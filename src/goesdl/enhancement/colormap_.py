from collections.abc import Sequence
from typing import Any, cast

from matplotlib import colormaps
from matplotlib.colors import Colormap, LinearSegmentedColormap, ListedColormap

from .constants import COLOR_COMPONENTS
from .shared import MSegmentData

ColorValue = tuple[int, int, int]
ColorList = list[ColorValue]

ColorPoint = tuple[int, ColorValue]
ColorTable = list[ColorPoint]

IndexList = list[int]

RealColorValue = tuple[float, float, float]
RealColorList = list[RealColorValue]

RealColorPoint = tuple[float, RealColorValue]
RealColorTable = list[RealColorPoint]

ColorEndpoint = tuple[int, int, int]
ColorEndpointList = list[ColorEndpoint]
ColorSegments = dict[str, ColorEndpointList]

RealColorEndpoint = tuple[float, float, float]
RealColorEndpointList = list[RealColorEndpoint]
RealColorSegments = dict[str, RealColorEndpointList]


class BaseColormap:

    colormap: Colormap

    def __init__(self, colormap: Colormap) -> None:
        self.colormap = colormap

    def set_bad(self, color: ColorValue) -> None:
        rgb = self._normalize_color_value(color)
        self.colormap.set_bad(rgb)

    def set_extremes(
        self, *, bad: ColorValue, under: ColorValue, over: ColorValue
    ) -> None:
        bad_color = self._normalize_color_value(bad)
        under_color = self._normalize_color_value(under)
        over_color = self._normalize_color_value(over)
        self.colormap.set_extremes(
            bad=bad_color, under=under_color, over=over_color
        )

    def set_over(self, color: ColorValue) -> None:
        rgb = self._normalize_color_value(color)
        self.colormap.set_over(rgb)

    def set_under(self, color: ColorValue) -> None:
        rgb = self._normalize_color_value(color)
        self.colormap.set_under(rgb)

    @staticmethod
    def _get_colormap(colormap_name: str) -> Colormap:
        try:
            colormap = colormaps.get_cmap(colormap_name)
            return colormap.copy()

        except (KeyError, ValueError) as error:
            raise ValueError(
                f"Invalid colormap '{colormap_name}': {error}"
            ) from error

    @staticmethod
    def _normalize_color_value(value: ColorValue) -> RealColorValue:
        red, green, blue = map(lambda x: x / 255, value)
        return red, green, blue

    @staticmethod
    def _validate_color_component(
        n: int, m: int, value: int, varname: str
    ) -> None:
        is_integer = isinstance(value, int)

        if not is_integer:
            raise ValueError(
                f"Component ({n}, {m}) of '{varname}' must be an integer, "
                f"got {type(value)}"
            )

        in_range = 0 <= value <= 255

        if not in_range:
            raise ValueError(
                f"Component ({n}, {m}) of '{varname}' must be in "
                f"range [0, 255], got {value}"
            )

    @classmethod
    def _validate_color_value(
        cls, n: int, value: ColorValue, varname: str
    ) -> None:
        is_tuple = isinstance(value, tuple)

        if not is_tuple:
            raise ValueError(
                f"Value {n} of '{varname}' is expected to be a `tuple`, "
                f"got `{type(value)}`"
            )

        ncomponents = len(value)

        if ncomponents != 3:
            raise ValueError(
                f"Value {n} of '{varname}' must have 3 components, "
                f"got {ncomponents}"
            )

        for m, component in enumerate(value):
            cls._validate_color_component(n, m, component, varname)

    @staticmethod
    def _validate_monotonic_indices(x: IndexList, vmax: int) -> None:
        is_list = isinstance(x, list)

        if not is_list:
            raise ValueError(
                f"'x' is expected to be a `list`, got `{type(x)}`"
            )

        nindices = len(x)

        if nindices < 2:
            raise ValueError("At least 2 control points are expected")

        if nindices > vmax + 1:
            raise ValueError(
                f"Control points can not exceed {vmax + 1} entries, "
                f"got {nindices}"
            )

        for n, i in enumerate(x):
            is_integer = isinstance(i, int)

            if not is_integer:
                raise ValueError(
                    f"Control point {n} is expected to be an `int`, "
                    f"got `{type(i)}`"
                )

        x_min = x[0]
        x_max = x[-1]

        if x_min != 0 or x_max != vmax:
            raise ValueError(
                f"Control points must start with x=0 and end with x={vmax}"
            )

        for i in range(len(x) - 1):
            x_current = x[i]
            x_next = x[i + 1]

            if x_current > x_next:
                raise ValueError(
                    "Control points must have x in increasing order"
                )

    @staticmethod
    def _validate_ncolors(ncolors: int | None, accept_none: bool) -> None:
        if ncolors is None and accept_none:
            return

        or_none = " or None" if accept_none else ""

        if not isinstance(ncolors, int):
            raise ValueError(
                f"'ncolors' must be an integer{or_none}, got {type(ncolors)}"
            )

        if not (2 <= ncolors <= 256):
            raise ValueError(
                f"'ncolors' must be in range [2, 256]{or_none}, got {ncolors}"
            )


class _ListBasedColormap(BaseColormap):

    @classmethod
    def _normalize_color_list(cls, color_list: ColorList) -> RealColorList:
        try:
            return list(map(cls._normalize_color_value, color_list))

        except (IndexError, TypeError, ValueError) as error:
            raise ValueError(f"Invalid color list: {error}") from error

    @classmethod
    def _rescale_color_list(cls, color_list: RealColorList) -> ColorList:
        try:
            return list(map(cls._rescale_color_value, color_list))

        except (IndexError, TypeError, ValueError) as error:
            raise ValueError(f"Invalid color list: {error}") from error

    @staticmethod
    def _rescale_color_value(value: RealColorValue) -> ColorValue:
        red, green, blue = map(lambda x: round(x * 255), value)
        return red, green, blue

    @classmethod
    def _validate_color_list(cls, color_list: ColorList) -> None:
        is_list = isinstance(color_list, list)

        if not is_list:
            raise ValueError(
                "'color_list' is expected to be a `list`, "
                f"got `{type(color_list)}`"
            )

        ncolors = len(color_list)

        if ncolors == 0:
            raise ValueError("'color_list' can not be empty")

        if ncolors > 256:
            raise ValueError(
                f"'color_list' can not exceed 256 entries, got {ncolors}"
            )

        for n, value in enumerate(color_list):
            cls._validate_color_value(n, value, "color_list")


class DiscreteColormap(_ListBasedColormap):

    def __init__(
        self, name: str, color_list: ColorList, ncolors: int | None = None
    ) -> None:
        self._validate_color_list(color_list)
        self._validate_ncolors(ncolors, True)

        normalized_color_list = self._normalize_color_list(color_list)

        ncolors = ncolors or len(color_list)

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
        self, name: str, color_list: ColorList, ncolors: int = 256
    ) -> None:
        self._validate_color_list(color_list)
        self._validate_ncolors(ncolors, False)

        normalized_color_list = self._normalize_color_list(color_list)

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


class _SegmentedBasedColormap(BaseColormap):

    @staticmethod
    def _normalize_color_index(index: int) -> float:
        return index / 255

    @classmethod
    def _normalize_color_point(cls, point: ColorPoint) -> RealColorPoint:
        index, value = point
        location = cls._normalize_color_index(index)
        rgb = cls._normalize_color_value(value)
        return location, rgb

    @classmethod
    def _normalize_color_table(cls, color_table: ColorTable) -> RealColorTable:
        try:
            return list(map(cls._normalize_color_point, color_table))

        except (IndexError, TypeError, ValueError) as error:
            raise ValueError(f"Invalid color table: {error}") from error

    @staticmethod
    def _validate_color_index(n: int, index: int) -> None:
        is_integer = isinstance(index, int)

        if not is_integer:
            raise ValueError(
                f"Index {n} in 'color_list' must be an integer, "
                f"got {type(index)}"
            )

        in_range = 0 <= index <= 255

        if not in_range:
            raise ValueError(
                f"Index {n} in 'color_list' must be in "
                f"range [0, 255], got {index}"
            )

    @classmethod
    def _validate_color_point(cls, n: int, point: ColorPoint) -> None:
        is_tuple = isinstance(point, tuple)

        if not is_tuple:
            raise ValueError(
                f"Entry {n} of 'color_table' is expected to be a `tuple`, "
                f"got `{type(point)}`"
            )

        nelements = len(point)

        if nelements != 2:
            raise ValueError(
                f"Entry {n} of 'color_table' must have 2 elements, "
                f"got {nelements}"
            )

        index, value = point

        cls._validate_color_index(n, index)

        cls._validate_color_value(n, value, "color_table")

    @classmethod
    def _validate_color_table(cls, color_table: ColorTable) -> None:
        is_list = isinstance(color_table, list)

        if not is_list:
            raise ValueError(
                "'color_table' is expected to be a `list`, "
                f"got `{type(color_table)}`"
            )

        ncolors = len(color_table)

        if ncolors == 0:
            raise ValueError("'color_table' can not be empty")

        if ncolors > 510:
            raise ValueError(
                f"'color_table' can not exceed 510 entries, got {ncolors}"
            )

        for n, point in enumerate(color_table):
            cls._validate_color_point(n, point)


class SegmentedColormap(_SegmentedBasedColormap):

    def __init__(
        self, name: str, color_table: ColorTable, ncolors: int = 256
    ) -> None:
        self._validate_color_table(color_table)
        self._validate_monotonic_indices([x for x, _ in color_table], 255)
        self._validate_ncolors(ncolors, False)

        normalized_color_table = self._normalize_color_table(color_table)

        colormap = LinearSegmentedColormap.from_list(
            name, normalized_color_table, N=ncolors
        )

        super().__init__(colormap)

    @staticmethod
    def _create_color_table(src_color_table: ColorTable) -> ColorTable:
        color_table = src_color_table[:1]

        for point in src_color_table:
            color_table.extend((point,) * 2)

        color_table.append(src_color_table[-1])

        return color_table


class _SegregatedBasedColormap(BaseColormap):

    @classmethod
    def _create_color_table(
        cls, colormap: LinearSegmentedColormap
    ) -> ColorTable:
        color_table = cls._make_color_table(colormap)
        return SegmentedColormap._create_color_table(color_table)

    @staticmethod
    def _make_color_table(colormap: LinearSegmentedColormap) -> ColorTable:
        segment_data: RealColorSegments = getattr(colormap, "_segmentdata")
        x_values = {
            endpoint[0]
            for endpoint_list in segment_data.values()
            for endpoint in endpoint_list
        }

        cm = colormap.resampled(512)

        def imap(x: float) -> int:
            return round(255 * x)

        def cmap(x: float) -> ColorValue:
            value = tuple(map(imap, iter(cm(x)[:3])))
            return cast(ColorValue, value)

        eps = 1.0e-6

        color_table: ColorTable = []
        for x in sorted(x_values):
            if x in {0.0, 1.0}:
                color_value = imap(x), cmap(x)
                color_table.append(color_value)
                continue

            value_left = cmap(x - eps)
            value_right = cmap(x + eps)

            if value_left == value_right:
                color_value = imap(x), value_left
                color_table.append(color_value)
            else:
                index = imap(x)
                color_table.extend(((index, value_left), (index, value_right)))

        return color_table

    @classmethod
    def _normalize_color_segments(
        cls, color_segments: ColorSegments
    ) -> RealColorSegments:
        normalized_segments: RealColorSegments = {}

        for color_name in COLOR_COMPONENTS:
            endpoin_tlist = color_segments[color_name]
            normalized_segments[color_name] = cls._normalize_enpoint_list(
                endpoin_tlist
            )

        return normalized_segments

    @classmethod
    def _normalize_enpoint(cls, endpoint: ColorEndpoint) -> RealColorEndpoint:
        location, end, begin = map(lambda x: x / 255, endpoint)
        return location, end, begin

    @classmethod
    def _normalize_enpoint_list(
        cls, endpoint_list: ColorEndpointList
    ) -> RealColorEndpointList:
        normalized_endpoint_list: RealColorEndpointList = []

        for endpoint in endpoint_list:
            normalized_endpoint = cls._normalize_enpoint(endpoint)
            normalized_endpoint_list.append(normalized_endpoint)

        return normalized_endpoint_list

    @classmethod
    def _validate_color_segments(cls, color_segments: ColorSegments) -> None:
        is_dictionary = isinstance(color_segments, dict)

        if not is_dictionary:
            raise ValueError(
                "'color_segments' is expected to be a `dict`, "
                f"got `{type(color_segments)}`"
            )

        for color_name in color_segments:
            if color_name not in COLOR_COMPONENTS:
                allowed_components = "', '".join(COLOR_COMPONENTS)
                raise ValueError(
                    f"Unknown '{color_name}' component, "
                    f"allowed components are: '{allowed_components}'"
                )

        for color_name in COLOR_COMPONENTS:
            if color_name not in color_segments:
                raise ValueError(
                    f"Missing '{color_name}' component in 'color_segments'"
                )

            endpoint_list = color_segments[color_name]

            cls._validate_endpoint_list(endpoint_list, color_name)

    @classmethod
    def _validate_endpoint(
        cls, n: int, endpoint: ColorEndpoint, segment_name: str
    ) -> None:
        is_tuple = isinstance(endpoint, tuple)

        if not is_tuple:
            raise ValueError(
                f"Value {n} of '{segment_name}' is expected to be a `tuple`, "
                f"got `{type(endpoint)}`"
            )

        ncomponents = len(endpoint)

        if ncomponents != 3:
            raise ValueError(
                f"Value {n} of '{segment_name}' must have 3 components, "
                f"got {ncomponents}"
            )

        for m, component in enumerate(endpoint):
            cls._validate_endpoint_item(n, m, component, segment_name)

    @staticmethod
    def _validate_endpoint_item(
        n: int, m: int, value: int, segment_name: str
    ) -> None:
        is_integer = isinstance(value, int)

        if not is_integer:
            raise ValueError(
                f"Component ({n}, {m}) of '{segment_name}' must be an integer, "
                f"got {type(value)}"
            )

        in_range = 0 <= value <= 255

        if not in_range:
            raise ValueError(
                f"Component ({n}, {m}) of '{segment_name}' must be in "
                f"range [0, 255], got {value}"
            )

    @classmethod
    def _validate_endpoint_list(
        cls, endpoint_list: ColorEndpointList, color_name: str
    ) -> None:
        is_list = isinstance(endpoint_list, list)

        segment_name = f'color_segments["{color_name}"]'
        if not is_list:
            raise ValueError(
                f"'{segment_name}' is expected to be a `list`, "
                f"got `{type(endpoint_list)}`"
            )

        ncolors = len(endpoint_list)

        if ncolors == 0:
            raise ValueError(f"'{segment_name}' can not be empty")

        if ncolors > 510:
            raise ValueError(
                f"'{segment_name}' can not exceed 510 entries, got {ncolors}"
            )

        for n, endpoint in enumerate(endpoint_list):
            cls._validate_endpoint(n, endpoint, segment_name)

    @classmethod
    def _validate_segment_indices(cls, color_segments: ColorSegments) -> None:
        for endpoint_list in color_segments.values():
            cls._validate_monotonic_indices(
                [x for x, _, _ in endpoint_list], 255
            )


class SegregatedColormap(_SegregatedBasedColormap):

    def __init__(
        self, name: str, color_segments: ColorSegments, ncolors: int = 256
    ) -> None:
        self._validate_color_segments(color_segments)
        self._validate_segment_indices(color_segments)
        self._validate_ncolors(ncolors, False)

        normalized_segments = self._normalize_color_segments(color_segments)

        segment_data = cast(MSegmentData, normalized_segments)

        colormap = LinearSegmentedColormap(name, segment_data, N=ncolors)

        super().__init__(colormap)


class _NamedColormapBased(_ListBasedColormap):

    @classmethod
    def _create_color_table(cls, colormap: Colormap) -> ColorTable:
        try:
            if isinstance(colormap, LinearSegmentedColormap):
                return cls._segmented_color_table(colormap)

            if isinstance(colormap, ListedColormap):
                return cls._discrete_color_table(colormap)

        except AttributeError as error:
            raise ValueError(
                "Unable to create colour table, "
                "probably due to Matplotlib version issues"
            ) from error

        raise ValueError(f"Unsupported colormap type: {type(colormap)}")

    @classmethod
    def _discrete_color_table(cls, colormap: ListedColormap) -> ColorTable:
        ncolors = colormap.N
        color_array = colormap([i / (ncolors - 1) for i in range(ncolors)])
        colors = cast(RealColorList, color_array[:, :3])
        color_list = cls._rescale_color_list(colors)
        return DiscreteColormap._create_color_table(color_list)

    @classmethod
    def _segmented_color_table(
        cls, colormap: LinearSegmentedColormap
    ) -> ColorTable:
        segment_data = getattr(colormap, "_segmentdata")

        is_functional = False
        for _, component in segment_data.items():
            is_functional = is_functional or callable(component)

        if is_functional:
            return cls._uniform_color_table(colormap)

        return SegregatedColormap._create_color_table(colormap)

    @classmethod
    def _uniform_color_table(
        cls, colormap: LinearSegmentedColormap
    ) -> ColorTable:
        cm = colormap.resampled(512)
        color_array = cm([i / 255 for i in range(256)])
        colors = cast(RealColorList, color_array[:, :3])
        color_list = cls._rescale_color_list(colors)
        return UniformColormap._create_color_table(color_list)


class NamedColormap(_NamedColormapBased):

    def __init__(self, name: str, ncolors: int = 256) -> None:
        self._validate_ncolors(ncolors, False)

        colormap = self._get_colormap(name)

        super().__init__(colormap.resampled(ncolors))


class CombinedColormap(UniformColormap):

    def __init__(
        self,
        name: str,
        colormaps: Sequence[Colormap],
        bounds: IndexList,
        ncolors: int = 256,
    ) -> None:
        self._validate_monotonic_indices(bounds, 256)
        self._validate_ncolors(ncolors, False)

        self._validate_bounds(colormaps, bounds)

        color_list = self._create_color_list(colormaps, bounds)

        super().__init__(name, color_list, ncolors)

    @classmethod
    def combined_from_stock(
        cls,
        name: str,
        colormap_names: Sequence[str],
        bounds: IndexList,
        ncolors: int = 256,
    ) -> "CombinedColormap":
        cls._validate_colormap_names(colormap_names)

        if isinstance(colormap_names, str):
            colormap_names = [colormap_names]

        colormaps: list[Colormap] = []

        for colormap_name in colormap_names:
            colormap = cls._get_colormap(colormap_name)
            colormaps.append(colormap)

        return cls(name, colormaps, bounds, ncolors)

    @classmethod
    def _create_color_list(
        cls, colormaps: Sequence[Colormap], bounds: IndexList
    ) -> ColorList:
        color_list: RealColorList = []

        for i, colormap in enumerate(colormaps):
            x_0 = bounds[i]
            x_1 = bounds[i + 1]
            control_points = [j / 255 for j in range(x_0, x_1)]
            colors = cast(RealColorList, colormap(control_points)[:, :3])
            color_list.extend(colors)

        return cls._rescale_color_list(color_list)

    def _validate_bounds(
        self, colormaps: Sequence[Colormap], bounds: IndexList
    ) -> None:
        nbounds = len(bounds)
        bounds_size = len(colormaps) + 1
        if nbounds != bounds_size:
            raise ValueError(
                f"Expected {bounds_size} bound points, got {nbounds}"
            )

    @staticmethod
    def _validate_colormap_names(colormap_names: Sequence[Any]) -> None:
        if not isinstance(colormap_names, (list, tuple)):
            raise ValueError(
                "'colormap_names' is expected to be a `list` or `tuple`, "
                f"got {type(colormap_names)}"
            )

        for n, name in enumerate(colormap_names):
            if not isinstance(name, str):
                raise ValueError(
                    f"Item {n} of 'colormap_names' is expected to be a `str`, "
                    f"got `{type(name)}`"
                )
