from collections.abc import Sequence
from datetime import datetime
from pathlib import Path
from typing import Protocol, TextIO

from numpy import array, float64, interp

from ..utils.array import ArrayFloat64


class TrackInfo:

    timestamps: Sequence[float]
    latitudes: Sequence[float]
    longitudes: Sequence[float]

    name: str
    year: int
    nlines: int
    sector: str
    number: int

    def __init__(
        self, name: str, year: int, nlines: int, sector: str, number: int
    ) -> None:
        self.name = name
        self.year = year
        self.nlines = nlines
        self.sector = sector
        self.number = number

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


class EventTracker:

    timestamps: ArrayFloat64
    latitudes: ArrayFloat64
    longitudes: ArrayFloat64

    track_info: TrackInfo

    def __init__(self, track_info: TrackInfo) -> None:
        self.track_info = track_info

        # Convert to NumPy arrays
        self.timestamps = array(track_info.timestamps, dtype=float64)
        self.latitudes = array(track_info.latitudes, dtype=float64)
        self.longitudes = array(track_info.longitudes, dtype=float64)

    def get(self, t: float) -> tuple[float, float]:
        """
        Interpolate the latitude and longitude for a given timestamp.

        If the timestamp is outside the range of the track data,
        extrapolation is performed.

        Parameters
        ----------
        t : float
            The tage timestamp for which to interpolate the latitude and
            longitude.

        Returns
        -------
        tuple[float, float]
            A tuple containing the interpolated latitude and longitude.
        """
        return self._interpolate_coordinates(
            t,
            self.track_info.timestamps,
            self.track_info.longitudes,
            self.track_info.latitudes,
        )

    @staticmethod
    def _interpolate_value(
        x: float, xp: ArrayFloat64, fp: ArrayFloat64
    ) -> float:
        """
        Perform linear interpolation or extrapolation.

        Performs a linear interpolation using np.interp and, if the
        point is outside the domain, performs a linear extrapolation.

        Parameters
        ----------
        x : float
            The x-coordinate for which to interpolate or extrapolate.
        xp : ArrayFloat64
            The x-coordinates of the data points.
        fp : ArrayFloat64
            The y-coordinates of the data points.

        Returns
        -------
        float
            The interpolated or extrapolated value.
        """
        if x < xp[0]:
            # Linear extrapolation to the left
            slope = (fp[1] - fp[0]) / (xp[1] - xp[0])
            return fp[0] + slope * (x - xp[0])

        if x > xp[-1]:
            # Linear extrapolation to the right
            slope = (fp[-1] - fp[-2]) / (xp[-1] - xp[-2])
            return fp[-1] + slope * (x - xp[-1])

        # Interpolation within the domain
        return float(interp(x, xp, fp))

    @classmethod
    def _interpolate_coordinates(
        cls,
        t: float,
        timestamps: ArrayFloat64,
        longitudes: ArrayFloat64,
        latitudes: ArrayFloat64,
    ) -> tuple[float, float]:
        """
        Interpolate or extrapolate coordinates for a given timestamp

        Interpolate the latitude and longitude for a given timestamp.
        If the timestamp is outside the range of the track data,
        extrapolation is performed.

        Parameters
        ----------
        t : float
            The timestamp for which to interpolate the latitude and
            longitude.
        timestamps : ArrayFloat64
            A sequence of timestamps representing the time of each track
            point.
        longitudes : ArrayFloat64
            A sequence of longitudes corresponding to the track points.
        latitudes : ArrayFloat64
            A sequence of latitudes corresponding to the track points.

        Returns
        -------
        tuple[float, float]
            A tuple containing the interpolated latitude and longitude.
        """
        # Interpolate or extrapolate for the given timestamp
        lon_interp = cls._interpolate_value(t, timestamps, longitudes)
        lat_interp = cls._interpolate_value(t, timestamps, latitudes)

        return lon_interp, lat_interp


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


class TrackParserHurdat2:

    ID = "HURDAT2"

    def __init__(self, path: Path) -> None:
        self.path = _validate_dataset_file(path)

    # def get_track(self, event: str, year: int) -> TrackInfo:
    #     lines = parse_hurdat(self.path, target_name, target_year)
    #     if lines:
    #         year, name, nlines, sector, number = parse_header(lines[0])
    #         return TrackInfo(name, year, nlines, sector, number)
    #     else:
    #         raise ValueError("No data found for the specified name and year.")


_track_parsers_stock: dict[str, type[TrackParser]] = {
    TrackParserHurdat2.ID: TrackParserHurdat2,
}

DEFAULT_TRACKER_ID = TrackParserHurdat2.ID


class EventTrackingInfo:
    def __init__(
        self, path: str | Path, dataset: str = DEFAULT_TRACKER_ID
    ) -> None:
        dataset = _validate_supported_dataset(dataset)
        path = _validate_dataset_file(path)

        self.dataset = dataset
        self.path = path

    def get_track(self, event: str, year: int) -> TrackInfo:
        try:
            tracker_class = _track_parsers_stock[self.dataset]
        except KeyError as error:
            raise ValueError(
                f"Tracker for '{self.dataset}' is not implemented."
            ) from error
        tracker = tracker_class(self.path)
        return tracker.get_track(event, year)


def _validate_dataset_file(path: str | Path) -> Path:
    """
    Validate the dataset file path.

    If the path is a string, convert it to a Path object.
    If the path is not a file, raise a FileNotFoundError.
    """
    path = Path(path)

    if not path.is_file():
        raise FileNotFoundError(f"File '{path}' does not exist.")

    return path


def _validate_supported_dataset(dataset: str) -> str:
    """
    Validate the dataset name.

    If the dataset is not supported, raise a ValueError.
    """
    available_datasets = {TrackParserHurdat2.ID}

    if dataset not in available_datasets:
        raise ValueError(f"Dataset '{dataset}' is not supported.")

    return dataset


def str_to_float(value_strings: Sequence[str]) -> list[float]:
    """
    Convert a sequence of strings to a list of floats.

    Parameters
    ----------
    value_strings : Sequence[str]
        A sequence of strings representing numeric values.

    Returns
    -------
    list[float]
        A list of floats converted from the input strings.
    """
    return [float(value) for value in value_strings]


def iso_to_timestamp(iso_strings):
    """Convierte una lista de cadenas ISO a una lista de timestamps en segundos desde la época."""
    # Convertir fechas ISO a timestamps en segundos desde la época
    return [
        datetime.fromisoformat(iso_string).timestamp()
        for iso_string in iso_strings
    ]


def get_track_data(lines: list[str]):
    clines = []
    for line in lines:
        cline = []
        cline.extend(
            word.strip()
            for i, word in enumerate(line.split(","))
            if i in {0, 1, 4, 5}
        )
        line = []
        for i in range(len(cline)):
            if i == 0:
                cline[i] = f"{cline[i][:4]}-{cline[i][4:6]}-{cline[i][6:8]}"
            elif i == 1:
                cline[i] = f"{int(cline[i]):0>4}"
                cline[i] = f"T{cline[i][:2]}:{cline[i][2:]}Z"
            elif i == 2:
                cline[i] = (
                    f"+{cline[i][:-1]}"
                    if cline[i][-1] == "N"
                    else f"-{cline[i][:-1]}"
                )
            elif i == 3:
                cline[i] = (
                    f"+{cline[i][:-1]}"
                    if cline[i][-1] == "E"
                    else f"-{cline[i][:-1]}"
                )
        line = [cline[0] + cline[1], cline[2], cline[3]]
        clines.append(line)

    iso_dates, latitudes, longitudes = zip(*clines)

    return (
        iso_to_timestamp(iso_dates),
        str_to_float(latitudes),
        str_to_float(longitudes),
    )


def parse_header(line: list[str]):
    parts = line.strip().split(",")

    identifier = parts[0].strip()
    sector = identifier[:2]
    number = int(identifier[2:4])
    year = int(identifier[4:8])

    name = parts[1].strip()
    nlines = int(parts[2].strip())

    return year, name, nlines, sector, number


def read_lines(file: TextIO, nlines: int):
    data_lines = []
    for _ in range(nlines):
        try:
            data_lines.append(next(file))
        except StopIteration:
            break
    return data_lines


def skip_lines(file: TextIO, nlines: int):
    for _ in range(nlines):
        try:
            next(file)
        except StopIteration:
            break


def parse_file(file: TextIO, target_name: str, target_year: str):
    while True:
        try:
            line = next(file)
            try:
                year, name, nlines, sector, number = parse_header(line)
                if year == target_year and name == target_name:
                    return read_lines(file, nlines)
                else:
                    skip_lines(file, nlines)
            except ValueError:
                continue
            except IndexError:
                continue
        except StopIteration:
            break
    return []


def parse_hurdat(
    file_path: str, target_name: str, target_year: str
) -> list[str]:
    target_name = target_name.upper()
    try:
        with open(file_path, "r") as file:
            if lines := parse_file(file, target_name, target_year):
                return lines
        return []
    except FileNotFoundError:
        print(f"Error: El archivo no se encontró en la ruta: {file_path}")
        return []
    except Exception as e:
        print(f"Ocurrió un error: {e}")
        return []
