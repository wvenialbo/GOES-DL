from logging import INFO
from pathlib import Path
from typing import Any, cast

from numpy import floating
from numpy.typing import NDArray

from .utilities import (
    get_algorithm_extra,
    get_algorithm_info,
    get_event_info,
    notify,
)

_Array = NDArray[floating[Any]]
_Settings = dict[str, Any]

_prof_suffix = ".npz"
_sepbar = "=" * 50


def _load_profile(profiles_path: Path, path: str) -> _Array:
    from numpy import load

    # Create the profile file path
    profile_path = Path(path)
    profile_path = profile_path.with_suffix(_prof_suffix)
    profile_path = profiles_path / profile_path.name

    # Load the profile data
    profile_data = load(profile_path)
    profile: _Array = profile_data["profile"]

    return profile


def _fill_missing_profile_values(profile: _Array, ignore: int) -> _Array:
    from numpy import isnan, nanmean

    # Fill missing values
    invalid_data = isnan(profile)
    mean_data = cast(float, nanmean(profile))
    profile[invalid_data] = mean_data

    # Set ignored central region to the next value in the profile
    profile[:ignore] = profile[ignore]

    return profile


def _run_algorithm_w(
    settings: _Settings, params: _Settings, dataset_paths: list[str]
) -> list[list[float]]:
    from numpy import nan

    # Get the left and right hand sides sequences
    time_offset: int = params["time_offset"]
    lhs_sequence = dataset_paths[:-time_offset]
    rhs_sequence = dataset_paths[time_offset:]

    sequence_length: int = params["sequence_length"]
    sequence_step: int = params["sequence_step"]

    display_settings: _Settings = settings["display"]
    verbose: bool = display_settings["verbose"]

    radii: list[int] = params["radii"]
    ignore: int = params["ignore"]

    repo_settings: dict[str, Path] = settings["repository"]
    profiles_path = repo_settings["profiles"]

    algo_settings: _Settings = settings["algorithm"]
    invert_difference: bool = algo_settings["invert_difference"]

    raw_time_series: list[list[float]] = [[] for _ in range(len(radii))]

    # Execute the algorithm
    for i in range(0, sequence_length, sequence_step):
        lhs_path = lhs_sequence[i]
        rhs_path = rhs_sequence[i]

        if verbose:
            notify(
                INFO, f"Generating data point {i + 1} of {sequence_length}\n"
            )

        if not lhs_path or not rhs_path:
            if verbose:
                notify(INFO, "... no data available\n")
            for k in range(len(radii)):
                raw_time_series[k].append(nan)
            continue

        # Load the profile
        lhs_profile = _load_profile(profiles_path, lhs_path)
        rhs_profile = _load_profile(profiles_path, rhs_path)

        # Fill missing values
        lhs_profile = _fill_missing_profile_values(lhs_profile, ignore)
        rhs_profile = _fill_missing_profile_values(rhs_profile, ignore)

        # Calculate the profile difference
        if invert_difference:
            difference = rhs_profile - lhs_profile
        else:
            difference = lhs_profile - rhs_profile

        # Add point to time series
        for k in range(len(radii)):
            radius_k = radii[k]
            value_at_radius = difference[radius_k]
            raw_time_series[k].append(value_at_radius)

    return raw_time_series


def _get_timeseries_filename(settings: _Settings) -> Path:
    event_name, time_start, time_end = get_event_info(settings, True)
    central_mask, windows_size, radius_min, radius_step = get_algorithm_info(
        settings
    )
    delta, sampling_rate, _, diff_mode = get_algorithm_extra(settings)

    filename_parts = [
        f"s{time_start}_e{time_end}",
        f"d{delta:0.0f}",
        f"r{radius_min:0.0f}-{radius_step:0.0f}",
        f"s{windows_size:0.1f}-{central_mask:0.1f}",
        f"fs{sampling_rate:0.0f}",
        f"{diff_mode}",
    ]

    filename_base = "_".join(filename_parts)
    filename = f"{event_name}_timeseries_{filename_base}.dat"

    repo_settings: dict[str, Path] = settings["repository"]
    repository_path = repo_settings["path"]

    return repository_path / filename


def run_algorithm_w(
    settings: _Settings, params: _Settings, dataset_paths: list[str]
) -> list[list[float]]:
    from goesdl.fileio import load_metadata, save_metadata

    notify(INFO, _sepbar)

    # Retrieve or build the time series
    timeseries_filename = _get_timeseries_filename(settings)

    raw_time_series: list[list[float]]

    if timeseries_filename.exists():
        # Just retrieve the precomputed time series
        notify(INFO, "Retrieving timeseries data...")

        raw_time_series = load_metadata(timeseries_filename)

        notify(INFO, "Time series retrieved!")

    else:
        # Compute parameters with values derived from data and other
        # parameters
        notify(INFO, "Generating time series...")

        raw_time_series = _run_algorithm_w(settings, params, dataset_paths)

        save_metadata(timeseries_filename, raw_time_series)

        notify(INFO, "Time series generation finished!")

    notify(INFO, _sepbar)

    return raw_time_series
