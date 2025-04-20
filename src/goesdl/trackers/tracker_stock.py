from .hurdat2 import TrackParserHurdat2
from .track_parser import TrackParser

track_parsers_stock: dict[str, type[TrackParser]] = {
    TrackParserHurdat2.ID: TrackParserHurdat2,
}

DEFAULT_TRACKER_ID = TrackParserHurdat2.ID
