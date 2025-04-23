from collections.abc import Sequence


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
        self.timestamps = timestamps
        self.latitudes = latitudes
        self.longitudes = longitudes
