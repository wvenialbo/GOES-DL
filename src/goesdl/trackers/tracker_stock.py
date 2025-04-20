from .hurdat2 import TrackParserHurdat2
from .track_parser import TrackParser

track_parsers_stock: dict[str, type[TrackParser]] = {
    TrackParserHurdat2.ID: TrackParserHurdat2,
}

DEFAULT_TRACKER_ID = TrackParserHurdat2.ID


def validate_supported_dataset(dataset: str) -> str:
    """
    Validate the dataset name.

    If the dataset is not supported, raise a ValueError.
    """
    if dataset not in track_parsers_stock:
        raise ValueError(f"Dataset '{dataset}' is not supported.")

    return dataset
