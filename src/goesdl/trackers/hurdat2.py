"""Parser for the HURDAT2 dataset.

This module provides functionality to parse the HURDAT2 dataset, which
contains hurricane track data. The parser extracts relevant information
from the dataset and provides a structured representation of the track
data.

The HURDAT2 dataset is a comma-separated values (CSV) file that contains
information about tropical cyclones, including their names, years, and
geographical coordinates (latitude and longitude) at various timestamps.

The parser reads the dataset, identifies the relevant event based on the
specified name and year, and extracts the track data for that event.

The extracted track data includes:
    - Timestamps: The time at which each track point was recorded.
    - Latitudes: The latitude coordinates of the track points.
    - Longitudes: The longitude coordinates of the track points.

The parser also validates the dataset file to ensure it is in the
correct format and contains the necessary information.
"""

from pathlib import Path
from typing import TextIO

from .file_parser import read_lines, skip_lines
from .track_info import TrackInfo
from .utility import iso_to_timestamp, str_to_float
from .validation import validate_dataset_file


class TrackParserHurdat2:

    ID = "HURDAT2"

    path: Path

    def __init__(self, path: Path) -> None:
        self.path = validate_dataset_file(path)

    def get_track(self, event: str, year: int) -> TrackInfo:
        info, lines = _parse_hurdat2(self.path, event, year)
        if lines:
            track_data = _get_track_data(lines)
            track_info = TrackInfo(*info)
            track_info.set_track_data(*track_data)
            return track_info
        else:
            raise ValueError("No data found for the specified event and year.")


def _parse_header_line(header_line: str) -> tuple[str, int, str, int, int]:
    try:
        parts = header_line.strip().split(",")

        identifier = parts[0].strip()
        sector = identifier[:2]
        number = int(identifier[2:4])
        year = int(identifier[4:8])

        name = parts[1].strip()
        nlines = int(parts[2].strip())

        return name, year, sector, number, nlines

    except (ValueError, IndexError) as error:
        raise ValueError(
            f"Error parsing header line: '{header_line}'. Error: {error}"
        ) from error


def _find_event(
    file: TextIO, event_name: str, event_year: int
) -> tuple[str, int, str, int, int]:
    while True:
        try:
            line = next(file)
            name, year, sector, number, nlines = _parse_header_line(line)
            if year == event_year and name == event_name:
                return name, year, sector, number, nlines
            else:
                skip_lines(file, nlines)
        except StopIteration:
            break
    raise ValueError(
        f"Event '{event_name}' in year '{event_year}' not found in the file."
    )


def _parse_hurdat2(
    file_path: Path, target_name: str, target_year: int
) -> tuple[tuple[str, int, str, int, int], list[str]]:
    target_name = target_name.upper()
    with file_path.open("r") as file:
        if info := _find_event(file, target_name, target_year):
            name, year, sector, number, nlines = info
            lines = read_lines(file, nlines)
            return (name, year, sector, number, nlines), lines

    raise ValueError(
        f"Event '{target_name}' in year '{target_year}' "
        "not found in the HURDAT2 database."
    )


def _get_track_data(
    lines: list[str],
) -> tuple[list[float], list[float], list[float]]:
    track_point: list[list[str]] = []
    for line in lines:
        components: list[str] = []
        components.extend(
            component.strip()
            for i, component in enumerate(line.split(","))
            if i in {0, 1, 4, 5}
        )

        # Convert the date component to ISO format
        raw_date = components[0]
        iso_date = f"{raw_date[:4]}-{raw_date[4:6]}-{raw_date[6:8]}"

        # Convert the time component to ISO format
        raw_time = components[1]
        time = f"{int(raw_time):0>4}"
        iso_time = f"T{time[:2]}:{time[2:]}Z"

        # Combine the date and time components
        iso_datetime = f"{iso_date}{iso_time}"

        # Convert the latitude component to a float
        # convertible string and add the sign based
        # on the hemisphere
        raw_lat = components[2]
        lat_val = raw_lat[:-1]
        lat_flag = raw_lat[-1]
        latitude = f"+{lat_val}" if lat_flag == "N" else f"-{lat_val}"

        # Convert the longitude component to a float
        # convertible string and add the sign based
        # on the hemisphere
        raw_lon = components[3]
        lon_val = raw_lon[:-1]
        lon_flag = raw_lon[-1]
        longitude = f"+{lon_val}" if lon_flag == "E" else f"-{lon_val}"

        # Append the canonicalised components to the track_point list
        components = [iso_datetime, latitude, longitude]
        track_point.append(components)

    iso_dates, latitudes, longitudes = zip(*track_point)

    return (
        iso_to_timestamp(iso_dates),
        str_to_float(latitudes),
        str_to_float(longitudes),
    )
