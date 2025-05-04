from collections.abc import Sequence
from copy import deepcopy
from math import nan
from typing import cast

from matplotlib import colormaps
from matplotlib.colors import Colormap, LinearSegmentedColormap, ListedColormap

from .constants import COLOR_COMPONENTS, UNNAMED_COLORMAP
from .shared import (
    ContinuousColorList,
    ContinuousColorTable,
    DiscreteColorList,
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
)


class BaseColormap:

    keypoints: KeypointList
    name: str
    ncolors: int
    segment_data: SegmentData

    def __init__(
        self,
        name: str,
        segment_data: SegmentData,
        keypoints: KeypointList,
        ncolors: int,
        reduce: bool,
    ) -> None:
        if reduce:
            segment_data = self._reduce_segment_data(segment_data)

        self.segment_data = segment_data

        self.keypoints = keypoints or self._get_keypoints(segment_data)

        self.ncolors = ncolors

        self.name = name or UNNAMED_COLORMAP

    @property
    def full_segment_data(self) -> SegmentData:
        return self._get_full_segment_data(self.segment_data)

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

    @staticmethod
    def _compress_color_segment(
        color_segments: list[SegmentDataRow],
    ) -> list[SegmentDataRow]:
        compressed_color_segments: list[SegmentDataRow] = [color_segments[0]]

        for x_1, y_2_0, y_2_1 in color_segments[1:]:
            x_0, y_1_0, _ = compressed_color_segments[-1]

            if x_0 == x_1:
                compressed_color_segments[-1] = (x_0, y_1_0, y_2_1)
            else:
                compressed_color_segments.append((x_1, y_2_0, y_2_1))

        return compressed_color_segments

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

    @staticmethod
    def _get_keypoints(segment_data: SegmentData) -> KeypointList:
        values: set[float] = set()

        for component, segments in segment_data.items():
            values.update({x for (x, y0, y1) in segments})

        return sorted(values)

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

    @classmethod
    def _reduce_segment_data(cls, segment_data: SegmentData) -> SegmentData:
        reduced_segment_data: SegmentData = {}

        for component in COLOR_COMPONENTS:
            color_segments = segment_data[component]
            color_segments = cls._remove_duplicate_color_segment(
                color_segments
            )
            color_segments = cls._compress_color_segment(color_segments)
            reduced_segment_data[component] = color_segments

        return reduced_segment_data

    @staticmethod
    def _remove_duplicate_color_segment(
        color_segments: list[SegmentDataRow],
    ) -> list[SegmentDataRow]:
        cleaned_color_segments: list[SegmentDataRow] = []

        previous_color_segment = (nan, nan, nan)
        for color_segment in color_segments:
            if color_segment == previous_color_segment:
                continue

            previous_color_segment = color_segment
            cleaned_color_segments.append(color_segment)

        return cleaned_color_segments


class SegmentedColormap(BaseColormap):

    def __init__(
        self, name: str, raw_segment_data: GSegmentData, ncolors: int = 256
    ) -> None:
        segment_data = self._copy_segment_data(raw_segment_data)

        super().__init__(name, segment_data, [], ncolors, True)

    @classmethod
    def _copy_segment_data(cls, raw_segment_data: GSegmentData) -> SegmentData:
        try:
            return cls._do_copy(raw_segment_data)

        except (IndexError, TypeError, ValueError) as error:
            raise ValueError(f"Invalid color segment data: {error}") from error

    @classmethod
    def _do_copy(cls, raw_segment_data: GSegmentData) -> SegmentData:
        segment_data: SegmentData = {}

        for component in COLOR_COMPONENTS:
            segment_data[component] = []

            for segment_entry in raw_segment_data[component]:
                segment_entry = cls._to_segment_entry(segment_entry)
                segment_data[component].append(segment_entry)

        return segment_data

    @staticmethod
    def _to_segment_entry(raw_segment_entry: GSegmentEntry) -> SegmentDataRow:
        x, y_0, y_1 = map(float, raw_segment_entry)
        return x, y_0, y_1


class _GRadiendBasedColormap(BaseColormap):

    def __init__(
        self,
        name: str,
        listed_colors: ContinuousColorList | ContinuousColorTable,
        ncolors: int = 256,
    ) -> None:
        colormap = self._get_colormap(listed_colors)

        segmented_colormap = self._get_segment_data(colormap)

        super().__init__(
            name,
            segmented_colormap.segment_data,
            segmented_colormap.keypoints,
            ncolors,
            False,
        )

    @staticmethod
    def _get_colormap(listed_colors: GListedColors) -> Colormap:
        try:
            return LinearSegmentedColormap.from_list(
                UNNAMED_COLORMAP, listed_colors
            )

        except (TypeError, ValueError) as error:
            raise ValueError(
                f"Invalid colour list specification: {error}"
            ) from error

    @staticmethod
    def _get_segment_data(colormap: Colormap) -> BaseColormap:
        if isinstance(colormap, LinearSegmentedColormap):
            raw_segment_data = getattr(colormap, "_segmentdata")
            return SegmentedColormap(colormap.name, raw_segment_data)

        raise ValueError(f"Unsupported colormap type: {type(colormap)}")


class ContinuousColormap(_GRadiendBasedColormap):

    def __init__(
        self, name: str, color_table: ContinuousColorTable, ncolors: int = 256
    ) -> None:
        super().__init__(name, color_table, ncolors)


class UniformColormap(_GRadiendBasedColormap):

    def __init__(
        self, name: str, color_list: ContinuousColorList, ncolors: int = 256
    ) -> None:
        super().__init__(name, color_list, ncolors)


class DiscreteColormap(BaseColormap):

    def __init__(
        self,
        name: str,
        raw_listed_colors: GListedColors,
        ncolors: int | None = None,
    ) -> None:
        listed_colors = self._copy_listed_colors(raw_listed_colors)

        segment_data = self._create_segment_data(listed_colors)

        ncolors = ncolors or len(listed_colors)

        super().__init__(name, segment_data, [], ncolors, True)

    @classmethod
    def _copy_listed_colors(
        cls, raw_listed_colors: GListedColors
    ) -> DiscreteColorList:

        try:
            return cls._do_copy_listed_colors(raw_listed_colors)

        except (IndexError, TypeError, ValueError) as error:
            raise ValueError(f"Invalid color list: {error}") from error

    @staticmethod
    def _create_segment_data(listed_colors: DiscreteColorList) -> SegmentData:
        n_colors = len(listed_colors)

        # Create keypoint values
        values: KeypointList = []

        for i in range(n_colors + 1):
            value = i / n_colors
            values.extend([value, value])
        values.pop(-1)
        values.pop(0)

        # Create segmen data
        segment_data: SegmentData = {}

        for k, component in enumerate(COLOR_COMPONENTS):
            # Create the segments for the k-th color component
            segment_data[component] = []

            for i in range(0, len(values), 2):
                j = i // 2

                # Get the k-th color component value of the j-th color
                color = listed_colors[j][k]

                # Add the i-th value entry
                value = values[i]
                segment_data[component].append((value, color, color))

                # Add the (i+1)-th value entry
                value = values[i + 1]
                segment_data[component].append((value, color, color))

        return segment_data

    @classmethod
    def _do_copy_listed_colors(
        cls, raw_listed_colors: GListedColors
    ) -> DiscreteColorList:
        listed_colors: DiscreteColorList = []

        for color_data in raw_listed_colors:
            color_entry: RGBValue = cls._to_rgb(color_data)
            listed_colors.append(color_entry)

        return listed_colors

    @staticmethod
    def _to_rgb(raw_segment_entry: GColorValue) -> RGBValue:
        red, green, blue = map(float, raw_segment_entry)
        return red, green, blue


class _NamedColormapBased:

    @staticmethod
    def _get_colormap(colormap_name: str) -> Colormap:
        try:
            return colormaps.get_cmap(colormap_name)

        except (KeyError, ValueError) as error:
            raise ValueError(
                f"Invalid colormap '{colormap_name}': {error}"
            ) from error

    @staticmethod
    def _get_segment_data(colormap: Colormap) -> BaseColormap:
        if isinstance(colormap, LinearSegmentedColormap):
            raw_segment_data = getattr(colormap, "_segmentdata")
            return SegmentedColormap(colormap.name, raw_segment_data)

        if isinstance(colormap, ListedColormap):
            listed_colors = cast(GListedColors, colormap.colors)
            return DiscreteColormap(colormap.name, listed_colors)

        raise ValueError(f"Unsupported colormap type: {type(colormap)}")


class NamedColormap(BaseColormap, _NamedColormapBased):

    def __init__(self, name: str, ncolors: int = 256) -> None:
        colormap = self._get_colormap(name)

        segmented_colormap = self._get_segment_data(colormap)

        super().__init__(
            segmented_colormap.name,
            segmented_colormap.segment_data,
            segmented_colormap.keypoints,
            ncolors,
            False,
        )


class CombinedColormap(BaseColormap, _NamedColormapBased):

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
        segment_data_list = self._extract_subsegment_data(colormap_names)

        # Rescale segment values for concatenation
        segment_data_list = self._rescale_segment_values(
            normalized_keypoints, segment_data_list
        )

        # Create the combined color segment data
        combined_segment_data = self._combine_segment_data(segment_data_list)

        name = name or "+".join(colormap_names)

        super().__init__(name, combined_segment_data, [], ncolors, True)

    def _combine_segment_data(
        self, segment_data_list: list[SegmentData]
    ) -> SegmentData:
        combined_segment_data: SegmentData = {}

        for component in COLOR_COMPONENTS:
            segments: list[SegmentDataRow] = []

            for segment_data in segment_data_list:
                segments.extend(segment_data[component])

            combined_segment_data[component] = segments

        return combined_segment_data

    def _extract_subsegment_data(
        self, colormap_names: Sequence[str]
    ) -> list[SegmentData]:
        segment_data_list: list[SegmentData] = []

        for colormap_name in colormap_names:
            colormap = self._get_colormap(colormap_name)
            segmented_colormap = self._get_segment_data(colormap)
            segment_data_list.append(segmented_colormap.segment_data)

        return segment_data_list

    def _normalize_keypoints(self, keypoints: GKeypointList) -> KeypointList:
        vmin, vmax = min(keypoints), max(keypoints)

        norm = vmax - vmin
        return [(keypoint - vmin) / norm for keypoint in keypoints]

    def _rescale_segment_values(
        self,
        normalized_keypoints: KeypointList,
        segment_data_list: list[SegmentData],
    ) -> list[SegmentData]:
        for i, segment_data in enumerate(segment_data_list):
            smin, smax = normalized_keypoints[i : i + 2]

            for component, segments in segment_data.items():
                for j, (x, y1, y2) in enumerate(segments):
                    x = smin * (1.0 - x) + smax * x
                    segments[j] = x, y1, y2

                segment_data[component] = segments

            segment_data_list[i] = segment_data

        return segment_data_list

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
            if keypoints[i] <= keypoints[i - 1]:
                raise ValueError("Keypoints must be monotonically increasing")
