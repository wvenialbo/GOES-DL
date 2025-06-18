from pathlib import Path
from typing import Any, cast

from numpy import floating
from numpy.typing import NDArray

from .utilities import (
    get_algorithm_extra,
    get_algorithm_info,
    get_event_info,
    load_profile,
    print_algorithm_parameters_report,
    print_bar,
)

_Array = NDArray[floating[Any]]
_Settings = dict[str, Any]

_prof_suffix = ".npz"


# ---------- Radial profile difference time series algorithm ----------
# ----------     (author: Waldemar Villamayor-Venialbo)      ----------


def run_algorithm_w(
    settings: _Settings, params: _Settings, dataset_paths: list[str]
) -> list[list[float]]:
    from goesdl.fileio import load_metadata, save_metadata

    print_algorithm_parameters_report(settings)

    # Retrieve or build the time series
    timeseries_filename = _get_timeseries_filename(settings)

    raw_time_series: list[list[float]]

    if timeseries_filename.exists():
        # Just retrieve the precomputed time series
        print("Retrieving timeseries data...")

        raw_time_series = load_metadata(timeseries_filename)

        print("Time series retrieved!")

    else:
        # Compute parameters with values derived from data and other
        # parameters
        print("Generating time series...")

        raw_time_series = _run_algorithm_w(settings, params, dataset_paths)

        save_metadata(timeseries_filename, raw_time_series)

        print("Time series generation finished!")

    print_bar()

    return raw_time_series


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
    profile_directory = repo_settings["profile"]

    algo_settings: _Settings = settings["algorithm"]
    invert_difference: bool = algo_settings["invert_difference"]

    raw_time_series: list[list[float]] = [[] for _ in range(len(radii))]

    # Execute the algorithm
    for i in range(0, sequence_length, sequence_step):
        lhs_path = lhs_sequence[i]
        rhs_path = rhs_sequence[i]

        if verbose:
            print(f"Generating data point {i + 1} of {sequence_length}\n")

        if not lhs_path or not rhs_path:
            if verbose:
                print("... no data available\n")
            for k in range(len(radii)):
                raw_time_series[k].append(nan)
            continue

        # Load the profile
        lhs_profile = load_profile(profile_directory, lhs_path)
        rhs_profile = load_profile(profile_directory, rhs_path)

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


def _fill_missing_profile_values(profile: _Array, ignore: int) -> _Array:
    from numpy import isnan, nanmean

    # Fill missing values
    invalid_data = isnan(profile)
    mean_data = cast(float, nanmean(profile))
    profile[invalid_data] = mean_data

    # Set ignored central region to the next value in the profile
    profile[:ignore] = profile[ignore]

    return profile


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

    repository_config: dict[str, Path] = settings.get("repository", {})
    repository_path = repository_config["path"]

    return repository_path / filename
