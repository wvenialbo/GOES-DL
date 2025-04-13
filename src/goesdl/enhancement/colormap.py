from collections.abc import Sequence

from .shared import DomainData


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

        if len(keypoints) != len(cmap_names) + 1:
            raise ValueError(
                f"Expected {len(cmap_names) + 1} keypoints, got {len(keypoints)}"
            )

        for i in range(1, len(keypoints)):
            if keypoints[i] <= keypoints[i - 1]:
                raise ValueError("Keypoints must be monotonically increasing")

        self.cmap_names = cmap_names
        self.domain = keypoints[0], keypoints[-1]
        self.extent = self.domain
        self.keypoints = keypoints
        self.name = name
