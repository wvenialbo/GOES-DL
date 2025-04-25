from collections.abc import Sequence

from .shared import (
    DomainData,
    GListedColors,
    ListedColors,
    RGBValue,
    SegmentData,
)
from .utility import to_rgb

color_components = ["red", "green", "blue"]


class DiscreteColormap:

    segment_data: SegmentData

    def __init__(self, raw_listed_colors: GListedColors) -> None:
        listed_colors = self._copy_listed_colors(raw_listed_colors)
        self.segment_data = self._create_segment_data(listed_colors)

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

        for k, component in enumerate(color_components):
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

    @staticmethod
    def _copy_listed_colors(raw_listed_colors: GListedColors) -> ListedColors:
        listed_colors: ListedColors = []
        try:
            for color_data in raw_listed_colors:
                color_entry: RGBValue = to_rgb(color_data)
                listed_colors.append(color_entry)
        except (IndexError, TypeError) as error:
            raise ValueError(f"Invalid color list: {error}") from error

        return listed_colors


class EnhancementColormap:

    cmap_names: Sequence[str]
    domain: DomainData
    extent: DomainData
    keypoints: Sequence[float]
    name: str

    def __init__(
        self,
        name: str,
        cmap_names: str | Sequence[str],
        keypoints: Sequence[float],
    ) -> None:
        if isinstance(cmap_names, str):
            cmap_names = [cmap_names]

        keypoints_size = len(cmap_names) + 1
        if len(keypoints) != keypoints_size:
            raise ValueError(
                f"Expected {keypoints_size} keypoints, got {len(keypoints)}"
            )

        for i in range(1, len(keypoints)):
            if keypoints[i] <= keypoints[i - 1]:
                raise ValueError("Keypoints must be monotonically increasing")

        self.cmap_names = cmap_names
        self.domain = keypoints[0], keypoints[-1]
        self.extent = self.domain
        self.keypoints = keypoints
        self.name = name
