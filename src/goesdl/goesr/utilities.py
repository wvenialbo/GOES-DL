import re
from typing import Literal


def _filter_hourly(listed_files: list[str]) -> list[str]:
    filtered_files: list[str] = []

    for nombre_archivo in listed_files:
        if match := re.search(
            r"_s\d{4}\d{3}\d{2}(\d{2})\d{2}\d_", nombre_archivo
        ):
            minutes = int(match[1])

            if minutes <= 2 or minutes >= 58:
                filtered_files.append(nombre_archivo)

    return filtered_files


def _filter_semihourly(listed_files: list[str]) -> list[str]:
    if not listed_files:
        return []

    filtered_files: list[str] = []

    for nombre_archivo in listed_files:
        if match := re.search(
            r"_s\d{4}\d{3}\d{2}(\d{2})\d{2}\d_", nombre_archivo
        ):
            minutes = int(match[1])

            if minutes <= 2 or minutes >= 58 or 28 <= minutes <= 32:
                filtered_files.append(nombre_archivo)

    return filtered_files


def filter_by_interval(
    listed_files: list[str], mode: Literal["hourly", "semi"] | str
) -> list[str]:
    if not listed_files:
        return []

    if mode == "hourly":
        return _filter_hourly(listed_files)

    elif mode == "semi":
        return _filter_semihourly(listed_files)

    raise ValueError(
        f"Invalid filter mode '{mode}', "
        "allowed values are: 'hourly' and 'semi'"
    )
