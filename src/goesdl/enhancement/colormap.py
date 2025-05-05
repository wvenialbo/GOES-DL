from collections.abc import Sequence
from copy import deepcopy
from typing import cast

from matplotlib import colormaps
from matplotlib.colors import Colormap, LinearSegmentedColormap, ListedColormap

from .constants import COLOR_COMPONENTS, UNNAMED_COLORMAP
from .shared import (
    ColorSegments,
    ColorTable,
    DiscreteColorList,
    DomainData,
    GColorValue,
    GKeypointList,
    GListedColors,
    GSegmentData,
    GSegmentEntry,
    KeypointList,
    MSegmentData,
    RGBValue,
    SegmentData,
    SegmentDataRow,
    UniformColorList,
)


class BaseColormap:

    keypoints: KeypointList
    name: str
    ncolors: int
    color_table: ColorTable

    under: RGBValue
    over: RGBValue
    bad: RGBValue

    domain: DomainData

    def __init__(
        self,
        name: str,
        color_table: ColorTable,
        keypoints: KeypointList,
        ncolors: int,
    ) -> None:
        if ncolors < 1:
            raise ValueError("'ncolors' must be a positive integer")

        self.color_table = color_table

        self.keypoints = keypoints or self._get_keypoints(color_table)

        self.ncolors = ncolors

        self.name = name or UNNAMED_COLORMAP

        self.under = 0.0, 0.0, 1.0
        self.over = 0.0, 1.0, 0.0
        self.bad = 1.0, 0.0, 0.0

        self.domain = 0.0, ncolors - 1.0

    def set_stock_colors(
        self, under: RGBValue, over: RGBValue, bad: RGBValue
    ) -> None:
        self.under = under
        self.over = over
        self.bad = bad

    def set_domain(self, domain: DomainData) -> None:
        self.domain = domain

    @staticmethod
    def _get_keypoints(color_table: ColorTable) -> KeypointList:
        return sorted({x for x, _ in color_table})


class SegmentedColormap(BaseColormap):

    def __init__(
        self, name: str, segment_data: GSegmentData, ncolors: int = 256
    ) -> None:
        segment_data_copy = self._copy_segment_data(segment_data)

        segment_data_copy = self._get_full_segment_data(segment_data_copy)

        color_table = self._get_color_table(segment_data_copy)

        super().__init__(name, color_table, [], ncolors)

    @staticmethod
    def _get_color_table(segment_data: SegmentData) -> ColorTable:
        segments: list[ColorSegments] = [
            segment_data[component] for component in COLOR_COMPONENTS
        ]

        color_table: ColorTable = []

        for x, r0, r1, _, g0, g1, _, b0, b1 in zip(*segments):
            color_table.extend(((x, (r0, g0, b0)), (x, (r1, g1, b1))))

        return color_table

    @staticmethod
    def _add_next_segment(
        k: int,
        vmin: float,
        color: GColorValue,
        entries: list[SegmentDataRow],
        src_segment: list[SegmentDataRow],
        dst_segment: list[SegmentDataRow],
    ) -> SegmentDataRow:
        current_entry = entries[k]
        current_value = current_entry[0]
        if current_value != vmin:
            previous_entry = dst_segment[-1]
            previous_value = previous_entry[0]
            if previous_value == vmin:
                next_entry = previous_entry
            else:
                vcolor = float(color[k])
                next_entry = vmin, vcolor, vcolor
        else:
            next_entry = current_entry
            current_entry = src_segment.pop(0)
        dst_segment.append(next_entry)
        return current_entry

    @classmethod
    def _copy_segment_data(cls, raw_segment_data: GSegmentData) -> SegmentData:
        try:
            return cls._do_copy(raw_segment_data)

        except (IndexError, TypeError, ValueError) as error:
            raise ValueError(f"Invalid color segment data: {error}") from error

    @staticmethod
    def _decompress_color_segment(
        color_segments: list[SegmentDataRow],
    ) -> list[SegmentDataRow]:
        decompressed_color_segments: list[SegmentDataRow] = []

        for x, y_0, y_1 in color_segments:
            if y_0 == y_1:
                decompressed_color_segments.append((x, y_0, y_1))
            else:
                decompressed_color_segments.extend(
                    [(x, y_0, y_0), (x, y_1, y_1)]
                )

        return decompressed_color_segments

    @classmethod
    def _do_copy(cls, raw_segment_data: GSegmentData) -> SegmentData:
        segment_data: SegmentData = {}

        for component in COLOR_COMPONENTS:
            segment_data[component] = []

            for segment_entry in raw_segment_data[component]:
                segment_entry = cls._to_segment_entry(segment_entry)
                segment_data[component].append(segment_entry)

        return segment_data

    @classmethod
    def _expand_segment_data(cls, segment_data: SegmentData) -> SegmentData:
        expanded_segment_data: SegmentData = {}

        for component in COLOR_COMPONENTS:
            color_segments = segment_data[component]
            color_segments = cls._decompress_color_segment(color_segments)
            expanded_segment_data[component] = color_segments

        return expanded_segment_data

    @classmethod
    def _get_full_segment_data(cls, segment_data: SegmentData) -> SegmentData:
        expanded_segment_data = cls._expand_segment_data(segment_data)

        return cls._homogenize_segment_data(expanded_segment_data)

    @classmethod
    def _homogenize_segment_data(
        cls, src_segment_data: SegmentData
    ) -> SegmentData:
        colormap = LinearSegmentedColormap(
            UNNAMED_COLORMAP, cast(MSegmentData, src_segment_data), 1024
        )

        src_segment_data = deepcopy(src_segment_data)

        dst_segment_data: SegmentData = {
            component: [] for component in COLOR_COMPONENTS
        }

        src_segments = [
            src_segment_data[component] for component in COLOR_COMPONENTS
        ]

        entries = [segment.pop(0) for segment in src_segments]

        while True:
            # Get the current minimum level value
            values = {entry[0] for entry in entries}
            vmin = min(values)

            # Check if all the current level values are the same
            if len(values) == 1:
                # Add the current level to the destination segment
                for k, component in enumerate(COLOR_COMPONENTS):
                    dst_segment_data[component].append(entries[k])
                # Update the segment entries if required and continue or
                # terminate the loop
                if vmin < 1.0:
                    entries = [segment.pop(0) for segment in src_segments]
                    continue
                break

            color = colormap(vmin)

            for k, component in enumerate(COLOR_COMPONENTS):
                src_segment = src_segment_data[component]
                dst_segment = dst_segment_data[component]

                entries[k] = cls._add_next_segment(
                    k, vmin, color, entries, src_segment, dst_segment
                )

        return dst_segment_data

    @staticmethod
    def _to_segment_entry(raw_segment_entry: GSegmentEntry) -> SegmentDataRow:
        x, y_0, y_1 = map(float, raw_segment_entry)
        return x, y_0, y_1


class ContinuousColormap(BaseColormap):

    def __init__(
        self, name: str, color_table: ColorTable, ncolors: int = 256
    ) -> None:
        super().__init__(name, color_table, [], ncolors)


class _ListBasedColormap(BaseColormap):

    @classmethod
    def _copy_listed_colors(
        cls, listed_colors: GListedColors
    ) -> UniformColorList:
        try:
            return cls._do_copy_listed_colors(listed_colors)

        except (IndexError, TypeError, ValueError) as error:
            raise ValueError(f"Invalid color list: {error}") from error

    @classmethod
    def _do_copy_listed_colors(
        cls, listed_colors: GListedColors
    ) -> UniformColorList:
        return list(map(cls._to_rgb, listed_colors))

    @staticmethod
    def _to_rgb(rgb_value: GColorValue) -> RGBValue:
        red, green, blue = map(float, rgb_value)
        return red, green, blue


class UniformColormap(_ListBasedColormap):

    def __init__(
        self, name: str, listed_colors: GListedColors, ncolors: int = 256
    ) -> None:
        color_list = self._copy_listed_colors(listed_colors)

        color_table = self._get_color_table(color_list)

        super().__init__(name, color_table, [], ncolors)

    @staticmethod
    def _get_color_table(
        listed_colors: UniformColorList,
    ) -> ColorTable:
        ncolors = len(listed_colors)
        return [(i / ncolors, x) for i, x in enumerate(listed_colors)]


class DiscreteColormap(_ListBasedColormap):

    def __init__(self, name: str, listed_colors: GListedColors) -> None:
        color_list = self._copy_listed_colors(listed_colors)

        ncolors = len(color_list)

        color_table = self._get_color_table(color_list, ncolors)

        super().__init__(name, color_table, [], ncolors)

    @staticmethod
    def _get_color_table(
        listed_colors: DiscreteColorList, ncolors: int
    ) -> ColorTable:
        return [
            ((i + j) / ncolors, x)
            for i, color in enumerate(listed_colors)
            for j, x in enumerate((color, color))
        ]


class _NamedColormapBased(BaseColormap):

    @staticmethod
    def _get_colormap(colormap_name: str) -> Colormap:
        try:
            return colormaps.get_cmap(colormap_name)

        except (KeyError, ValueError) as error:
            raise ValueError(
                f"Invalid colormap '{colormap_name}': {error}"
            ) from error

    @staticmethod
    def _get_segmented_colormap(
        colormap: Colormap,
    ) -> tuple[BaseColormap, bool]:
        try:
            if isinstance(colormap, LinearSegmentedColormap):
                raw_segment_data = getattr(colormap, "_segmentdata")
                return SegmentedColormap(colormap.name, raw_segment_data), True

            if isinstance(colormap, ListedColormap):
                listed_colors = cast(GListedColors, colormap.colors)
                return DiscreteColormap(colormap.name, listed_colors), False

        except AttributeError as error:
            raise ValueError(
                "Unable to create the colour map segment data, "
                "probably due to Matplotlib version issues"
            ) from error

        raise ValueError(f"Unsupported colormap type: {type(colormap)}")


class NamedColormap(_NamedColormapBased):

    def __init__(self, name: str, ncolors: int = 256) -> None:
        colormap = self._get_colormap(name)

        segmented_colormap, segmented = self._get_segmented_colormap(colormap)

        ncolors = ncolors if segmented else segmented_colormap.ncolors

        super().__init__(
            segmented_colormap.name,
            segmented_colormap.color_table,
            segmented_colormap.keypoints,
            ncolors,
        )


class CombinedColormap(_NamedColormapBased):

    def __init__(
        self,
        name: str,
        colormap_names: str | Sequence[str],
        keypoints: GKeypointList,
        ncolors: int = 256,
    ) -> None:
        if isinstance(colormap_names, str):
            colormap_names = [colormap_names]

        # Validate keypoints
        self._validate_keypoints(colormap_names, keypoints)

        # Normalise keypoints
        normalized_keypoints = self._normalize_keypoints(keypoints)

        # Get the segment data of each sub-colormap
        color_tables = self._extract_color_tables(colormap_names)

        # Rescale segment values for concatenation
        color_tables = self._rescale_color_tables(
            normalized_keypoints, color_tables
        )

        # Create the combined color segment data
        combined_color_table = self._combine_color_table(color_tables)

        name = name or "+".join(colormap_names)

        super().__init__(name, combined_color_table, [], ncolors)

    def _combine_color_table(
        self, color_tables: list[ColorTable]
    ) -> ColorTable:
        combined_color_table: ColorTable = []

        for color_table in color_tables:
            combined_color_table.extend(color_table)

        return combined_color_table

    def _extract_color_tables(
        self, colormap_names: Sequence[str]
    ) -> list[ColorTable]:
        color_tables: list[ColorTable] = []

        for colormap_name in colormap_names:
            colormap = self._get_colormap(colormap_name)
            segmented_colormap, _ = self._get_segmented_colormap(colormap)
            color_tables.append(segmented_colormap.color_table)

        return color_tables

    def _normalize_keypoints(self, keypoints: GKeypointList) -> KeypointList:
        vmin, vmax = min(keypoints), max(keypoints)

        norm = vmax - vmin
        return [(keypoint - vmin) / norm for keypoint in keypoints]

    def _rescale_color_tables(
        self,
        normalized_keypoints: KeypointList,
        color_tables: list[ColorTable],
    ) -> list[ColorTable]:
        for i, color_table in enumerate(color_tables):
            smin, smax = normalized_keypoints[i : i + 2]

            for j, (x, rgb) in enumerate(color_table):
                x = smin * (1.0 - x) + smax * x
                color_table[j] = x, rgb

            color_tables[i] = color_table

        return color_tables

    def _validate_keypoints(
        self, colormap_names: Sequence[str], keypoints: GKeypointList
    ) -> None:
        # Validate keypoints number
        keypoints_size = len(colormap_names) + 1
        if len(keypoints) != keypoints_size:
            raise ValueError(
                f"Expected {keypoints_size} keypoints, got {len(keypoints)}"
            )

        # Validate keypoints disposition
        for i in range(1, len(keypoints)):
            if keypoints[i] >= keypoints[i - 1]:
                raise ValueError("Keypoints must be monotonically decreasing")
