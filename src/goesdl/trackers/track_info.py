from collections.abc import Sequence
from typing import cast, overload

from .utility import iso_to_timestamp


class TrackInfo:

    timestamps: Sequence[float]
    latitudes: Sequence[float]
    longitudes: Sequence[float]

    name: str
    year: int
    sector: str
    number: int
    nlines: int

    def __init__(
        self, name: str, year: int, sector: str, number: int, nlines: int
    ) -> None:
        self.name = name
        self.year = year
        self.sector = sector
        self.number = number
        self.nlines = nlines

        self.timestamps = ()
        self.latitudes = ()
        self.longitudes = ()

    @overload
    def set_track_data(
        self,
        timestamps: Sequence[float],
        latitudes: Sequence[float],
        longitudes: Sequence[float],
    ) -> None:
        """
        Set the track data for the event.

        Parameters
        ----------
        timestamps : Sequence[float]
            A sequence of timestamps representing the time of each track
            point.
        latitudes : Sequence[float]
            A sequence of latitudes corresponding to the track points.
        longitudes : Sequence[float]
            A sequence of longitudes corresponding to the track points.
        """

    @overload
    def set_track_data(
        self,
        timestamps: Sequence[str],
        latitudes: Sequence[float],
        longitudes: Sequence[float],
    ) -> None:
        """
        Set the track data for the event.

        Parameters
        ----------
        timestamps : Sequence[str]
            A sequence of strings representing the time of each track
            point in ISO 8601 format.
        latitudes : Sequence[float]
            A sequence of latitudes corresponding to the track points.
        longitudes : Sequence[float]
            A sequence of longitudes corresponding to the track points.
        """

    def set_track_data(
        self,
        timestamps: Sequence[float] | Sequence[str],
        latitudes: Sequence[float],
        longitudes: Sequence[float],
    ) -> None:
        """
        Set the track data for the event.

        Parameters
        ----------
        timestamps : Sequence[float] | Sequence[str]
            A sequence of timestamps or a sequence of date strings in
            ISO 8601 format representing the time of each track point.
        latitudes : Sequence[float]
            A sequence of latitudes corresponding to the track points.
        longitudes : Sequence[float]
            A sequence of longitudes corresponding to the track points.
        """
        if not timestamps:
            raise ValueError("`timestamps` cannot be empty.")
        if not latitudes:
            raise ValueError("`latitudes` cannot be empty.")
        if not longitudes:
            raise ValueError("`longitudes` cannot be empty.")

        same_length_latitudes = len(timestamps) == len(latitudes)
        same_length_longitudes = len(timestamps) == len(longitudes)

        if not same_length_latitudes or not same_length_longitudes:
            raise ValueError(
                "The lengths of `timestamps`, `latitudes`, "
                "and `longitudes` must be the same."
            )

        if isinstance(timestamps[0], str):
            timestamps = cast(Sequence[str], timestamps)
            self.timestamps = iso_to_timestamp(timestamps)
        else:
            self.timestamps = cast(Sequence[float], timestamps)

        self.latitudes = latitudes
        self.longitudes = longitudes
