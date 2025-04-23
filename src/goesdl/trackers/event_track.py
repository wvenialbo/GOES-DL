from pathlib import Path

from .track_info import TrackInfo
from .tracker_stock import (
    DEFAULT_TRACKER_ID,
    track_parsers_stock,
    validate_supported_dataset,
)
from .validation import validate_dataset_file


class EventTrackDataset:
    def __init__(
        self, path: str | Path, dataset: str = DEFAULT_TRACKER_ID
    ) -> None:
        dataset = validate_supported_dataset(dataset)
        path = validate_dataset_file(path)

        self.dataset = dataset
        self.path = path

    def get_track(self, event: str, year: int) -> TrackInfo:
        try:
            tracker_class = track_parsers_stock[self.dataset]
        except KeyError as error:
            raise ValueError(
                f"Tracker for '{self.dataset}' is not implemented."
            ) from error
        tracker = tracker_class(self.path)
        return tracker.get_track(event, year)
