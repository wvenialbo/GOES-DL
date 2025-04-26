from collections.abc import Sequence
from copy import deepcopy
from math import nan
from typing import cast

from matplotlib import colormaps
from matplotlib.colors import Colormap, LinearSegmentedColormap, ListedColormap

from .constants import COLOR_COMPONENTS
from .shared import (
    ColorSegment,
    GColorValue,
    GListedColors,
    GSegmentData,
    GSegmentEntry,
    ListedColors,
    MSegmentData,
    RGBValue,
    SegmentData,
)


class _SegmentedColormapBased:

    segment_data: SegmentData

    def __init__(self, segment_data: SegmentData) -> None:
        self.segment_data = segment_data

    @staticmethod
    def _add_next_segment(
        k: int,
        vmin: float,
        color: GColorValue,
        entries: list[ColorSegment],
        src_segment: list[ColorSegment],
        dst_segment: list[ColorSegment],
    ) -> ColorSegment:
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
        color_segments: list[ColorSegment],
    ) -> list[ColorSegment]:
        compressed_color_segments: list[ColorSegment] = [color_segments[0]]

        for x_1, y_2_0, y_2_1 in color_segments[1:]:
            x_0, y_1_0, _ = compressed_color_segments[-1]

            if x_0 == x_1:
                compressed_color_segments[-1] = (x_0, y_1_0, y_2_1)
            else:
                compressed_color_segments.append((x_1, y_2_0, y_2_1))

        return compressed_color_segments

    @staticmethod
    def _decompress_color_segment(
        color_segments: list[ColorSegment],
    ) -> list[ColorSegment]:
        decompressed_color_segments: list[ColorSegment] = []

        for x, y_0, y_1 in color_segments:
            if y_0 == y_1:
                decompressed_color_segments.append((x, y_0, y_1))
            else:
                decompressed_color_segments.extend(
                    [(x, y_0, y_0), (x, y_1, y_1)]
                )

        return decompressed_color_segments

    @classmethod
    def _homogenize_segment_data(
        cls, src_segment_data: SegmentData
    ) -> SegmentData:
        colormap = LinearSegmentedColormap(
            "temp-cmap", cast(MSegmentData, src_segment_data), 256
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
        color_segments: list[ColorSegment],
    ) -> list[ColorSegment]:
        cleaned_color_segments: list[ColorSegment] = []

        previous_color_segment = (nan, nan, nan)
        for color_segment in color_segments:
            if color_segment == previous_color_segment:
                continue

            previous_color_segment = color_segment
            cleaned_color_segments.append(color_segment)

        return cleaned_color_segments


class SegmentedColormap(_SegmentedColormapBased):

    def __init__(self, raw_segment_data: GSegmentData) -> None:
        segment_data = self._copy_segment_data(raw_segment_data)

        segment_data = self._reduce_segment_data(segment_data)

        super().__init__(segment_data)

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
    def _to_segment_entry(raw_segment_entry: GSegmentEntry) -> ColorSegment:
        x, y_0, y_1 = raw_segment_entry
        return float(x), float(y_0), float(y_1)


class DiscreteColormap(SegmentedColormap):

    def __init__(self, raw_listed_colors: GListedColors) -> None:
        listed_colors = self._copy_listed_colors(raw_listed_colors)

        segment_data = self._create_segment_data(listed_colors)

        super().__init__(cast(GSegmentData, segment_data))

    @classmethod
    def _copy_listed_colors(
        cls, raw_listed_colors: GListedColors
    ) -> ListedColors:

        try:
            return cls._do_copy_listed_colors(raw_listed_colors)

        except (IndexError, TypeError, ValueError) as error:
            raise ValueError(f"Invalid color list: {error}") from error

    @staticmethod
    def _create_segment_data(listed_colors: ListedColors) -> SegmentData:
        n_colors = len(listed_colors)

        # Create keypoint values
        values: list[float] = []

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
    ) -> ListedColors:
        listed_colors: ListedColors = []

        for color_data in raw_listed_colors:
            color_entry: RGBValue = cls._to_rgb(color_data)
            listed_colors.append(color_entry)

        return listed_colors

    @staticmethod
    def _to_rgb(raw_segment_entry: GColorValue) -> RGBValue:
        red, green, blue = raw_segment_entry
        return float(red), float(green), float(blue)


class _NamedColormapBased:

    @staticmethod
    def _get_segment_data(colormap: Colormap) -> SegmentData:
        if isinstance(colormap, LinearSegmentedColormap):
            raw_segment_data = getattr(colormap, "_segmentdata")
            s_colormap = SegmentedColormap(raw_segment_data)

            return s_colormap.segment_data

        if isinstance(colormap, ListedColormap):
            listed_colors = cast(GListedColors, colormap.colors)
            l_colormap = DiscreteColormap(listed_colors)

            return l_colormap.segment_data

        raise ValueError(f"Unsupported colormap type: {type(colormap)}")

    @staticmethod
    def _get_colormap(colormap_name: str) -> Colormap:
        try:
            return colormaps.get_cmap(colormap_name)

        except (KeyError, ValueError) as error:
            raise ValueError(
                f"Invalid colormap'{colormap_name}': {error}"
            ) from error


class NamedColormap(_SegmentedColormapBased, _NamedColormapBased):

    def __init__(
        self,
        colormap_name: str,
    ) -> None:
        colormap = self._get_colormap(colormap_name)
        segment_data = self._get_segment_data(colormap)

        super().__init__(segment_data)


class EnhancementColormap(_SegmentedColormapBased, _NamedColormapBased):

    def __init__(
        self,
        colormap_names: str | Sequence[str],
        keypoints: Sequence[float],
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
        segments = self._rescale_segment_values(
            normalized_keypoints, segment_data_list
        )

        # Create the combined color segment data
        combined_segment_data = self._combine_segmen_data(
            segment_data_list, segments
        )

        super().__init__(combined_segment_data)

    def _combine_segmen_data(
        self,
        segment_data_list: list[SegmentData],
        segments: list[ColorSegment],
    ) -> SegmentData:
        combined_segment_data: SegmentData = {}
        for component in COLOR_COMPONENTS:
            combined_segment_data[component] = []
            for segment_data in segment_data_list:
                segments.extend(segment_data[component])
        return combined_segment_data

    def _extract_subsegment_data(
        self, colormap_names: Sequence[str]
    ) -> list[SegmentData]:
        segment_data_list: list[SegmentData] = []
        for colormap_name in colormap_names:
            colormap = self._get_colormap(colormap_name)
            segment_data = self._get_segment_data(colormap)
            segment_data_list.append(segment_data)
        return segment_data_list

    def _normalize_keypoints(self, keypoints: Sequence[float]) -> list[float]:
        vmin, vmax = min(keypoints), max(keypoints)

        norm = vmax - vmin
        return [(keypoint - vmin) / norm for keypoint in keypoints]

    def _rescale_segment_values(
        self,
        normalized_keypoints: list[float],
        segment_data_list: list[SegmentData],
    ) -> list[ColorSegment]:
        for i, segment_data in enumerate(segment_data_list):
            smin, smax = normalized_keypoints[i : i + 2]
            for component, segments in segment_data.items():
                for j, (x, y1, y2) in enumerate(segments):
                    x = smin * (1 - x) + smax * x
                    segments[j] = x, y1, y2
                segment_data[component] = segments
        return segments

    def _validate_keypoints(
        self, colormap_names: Sequence[str], keypoints: Sequence[float]
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
