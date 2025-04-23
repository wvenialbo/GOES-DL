from pathlib import Path
from typing import Protocol

from .track_info import TrackInfo


class TrackParser(Protocol):
    ID: str

    def __init__(self, path: Path) -> None: ...

    def get_track(self, event: str, year: int) -> TrackInfo:
        """
        Retrieve track information for a specific event and year.

        Parameters
        ----------
        event : str
            The name of the event to retrieve track information for.
        year : int
            The year of the event.

        Returns
        -------
        TrackInfo
            An object containing track information for the specified
            event and year.
        """
        ...
