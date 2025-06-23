from collections.abc import Callable
from copy import deepcopy
from math import ceil, floor, inf
from pathlib import Path
from typing import Any

from .config import ConfigDict
from .report_tools import print_bar, print_derived_parameters_report
from .utilities import (
    create_matrix_path,
    get_difference_directory_name,
    get_filename_prefix,
    load_matrix,
    load_profile,
    load_profile_data,
)

_Settings = dict[str, Any]


_ALGORITHM_DELTA_T = "algorithm.delta_t"
_DATASOURCE_SPATIAL_RESOLUTION = "datasource.spatial_resolution"
_DATASOURCE_TIME_RESOLUTION = "datasource.time_resolution"
_FILTER_BANDWIDTH = "filter.bandwidth"
_FILTER_FREQUENCY = "filter.frequency"
_REPOSITORY_PROFILE = "repository.profile"
_SUBSAMPLING_SAMPLING_RATE = "subsampling.sampling_rate"


def update_computed_parameters(
    settings: ConfigDict, dataset_paths: list[str]
) -> ConfigDict:
    algorithm_id = settings.as_str("algorithm_id")

    if algorithm_id == "algorithm_0":
        return update_computed_parameters_w(settings, dataset_paths)

    if algorithm_id == "algorithm_1":
        return update_computed_parameters_v(settings, dataset_paths)

    if algorithm_id != "algorithm_2":
        raise ValueError(
            f"Unexpected algorithm ID '{algorithm_id}', allowed values are: "
            "'algorithm_0', 'algorithm_1', and 'algorithm_2'"
        )

    _calculate_difference_matrices(settings, dataset_paths)

    return update_computed_parameters_t(settings, dataset_paths)


def _update_computed_parameters_common(
    settings: ConfigDict,
    dataset_paths: list[str],
    get_parameters_filename_func: Callable[[ConfigDict], Path],
    compute_parameters_func: Callable[[ConfigDict, list[str]], _Settings],
) -> ConfigDict:
    from goesdl.fileio import load_metadata, save_metadata

    print_bar()

    # Retrieve or calculate derived parameters
    parameters_filename = get_parameters_filename_func(settings)

    parameters_data: _Settings

    if parameters_filename.exists():
        # Just retrieve the precomputed parameters
        print("Retrieving precomputed parameters...")

        parameters_data = load_metadata(parameters_filename)

        print("Precomputed parameters retrieved!")
    else:
        # Compute parameters with values derived from data and other
        # parameters
        print("Computing derived parameters...")

        parameters_data = compute_parameters_func(settings, dataset_paths)
        save_metadata(parameters_filename, parameters_data)

        print("Derived parameters computed!")

    updated_settings = deepcopy(settings)
    updated_settings["parameters"] |= parameters_data

    print_derived_parameters_report(updated_settings)

    print_bar()

    return updated_settings


# ---------- Radial profile difference time series algorithm ----------
# ---------- Derived parameters computation or retrieval  ----------


def update_computed_parameters_w(
    settings: ConfigDict, dataset_paths: list[str]
) -> ConfigDict:
    # This function acts as a simple wrapper
    return _update_computed_parameters_common(
        settings,
        dataset_paths,
        _get_parameters_filename_w,
        _compute_parameters_w,
    )


def _compute_parameters_w(
    settings: ConfigDict, dataset_paths: list[str]
) -> _Settings:
    # Retrieve or calculate the derived parameters
    radius = _get_radius_value_w(settings, dataset_paths)
    spatial_parameters = _compute_spatial_parameters_w(settings, radius)

    sequence_length = len(dataset_paths)
    sampling_parameters = _get_sampling_parameters_w(settings, sequence_length)

    radiometric_parameters = _compute_radiometric_parameters_w(
        settings, dataset_paths
    )

    filter_parameters = _get_filter_parameters_w(settings)

    return (
        spatial_parameters
        | sampling_parameters
        | radiometric_parameters
        | filter_parameters
    )


def _get_radius_value_w(settings: ConfigDict, dataset_paths: list[str]) -> int:
    profile_directory = settings.as_path(_REPOSITORY_PROFILE)

    radius = 0

    for dataset_path in dataset_paths:
        if not dataset_path:
            continue

        # Load the profile data
        profile_data = load_profile_data(profile_directory, dataset_path)

        radius = int(profile_data["radius"])

        break

    return radius


def _compute_spatial_parameters_w(
    settings: ConfigDict, radius: int
) -> _Settings:
    algorithm_config = settings.section("algorithm")

    windows_size = algorithm_config.as_float("windows_size")
    radius_min = algorithm_config.as_float("radius_min")
    radius_step = algorithm_config.as_float("radius_step")

    spatial_resolution = settings.as_float(_DATASOURCE_SPATIAL_RESOLUTION)

    # Calculate the central-ignore and analysis sizes
    window = min(int(windows_size * radius / 100), radius)

    # Create the x-axis tick and limit values (kilometres per pixel)
    x_ticks = [spatial_resolution * (i + 0.5) for i in range(window)]
    x_min = 0.0
    x_max = spatial_resolution * window

    # Create a list of radii for the analysis
    radius_max = x_max + radius_step
    nrange = ceil((radius_max - radius_min) / radius_step)

    radii = [
        floor(i * radius_step / spatial_resolution)
        for i in range(nrange)
        if x_min <= i * radius_step <= x_max
    ]

    radii_km = [spatial_resolution * r for r in radii]
    radius_km = spatial_resolution * radius

    return {
        "radii": radii,
        "radii_km": radii_km,
        "radius": radius,
        "radius_km": radius_km,
        "window": window,
        "x_min": x_min,
        "x_max": x_max,
        "x_ticks": x_ticks,
    }


def _get_sampling_parameters_w(
    settings: ConfigDict, full_sequence_length: int
) -> _Settings:
    # Satellite temporal resolution (in samples/day)
    time_resolution_spd = settings.as_int(_DATASOURCE_TIME_RESOLUTION)

    if (
        time_resolution_spd < 1
        or 24 % time_resolution_spd != 0
        and time_resolution_spd % 24 != 0
    ):
        raise ValueError(
            "'datasource.time_resolution' must be an integer divisor or "
            f"multiple of 24 samples/day, got {time_resolution_spd}"
        )

    # Time series sampling rate (in samples/day)
    sampling_rate_spd = settings.as_int(_SUBSAMPLING_SAMPLING_RATE)

    if sampling_rate_spd < 1 or time_resolution_spd % sampling_rate_spd != 0:
        raise ValueError(
            f"'subsampling.sampling_rate' ({sampling_rate_spd}) must "
            "be an integer divisor of 'datasource.time_resolution' "
            f"({time_resolution_spd})"
        )

    # Calculate the effective sampling interval
    sampling_interval = time_resolution_spd // sampling_rate_spd

    # Time delta for the radial profile differences (in hours)
    timedelta_h = settings.as_int(_ALGORITHM_DELTA_T)

    # Calculate the offset in samples
    lag_in_samples = timedelta_h * time_resolution_spd / 24

    if (
        lag_in_samples < 1
        or timedelta_h >= 24
        or 24 % timedelta_h != 0
        or not lag_in_samples.is_integer()
    ):
        min_delta_h_float = 24 / time_resolution_spd

        def valid_delta(delta: float) -> bool:
            return (
                delta >= min_delta_h_float
                and (delta * time_resolution_spd) % 24 == 0
            )

        possible_delta_values = [1, 2, 3, 4, 6, 8, 12]
        if valid_options_for_delta_h := [
            f"{delta}"
            for delta in possible_delta_values
            if (valid_delta(delta))
        ]:
            raise ValueError(
                "'algorithm.delta_t' must be "
                f"{'h, '.join(valid_options_for_delta_h)}; "
                f"but got {timedelta_h}h"
            )
        raise ValueError(
            "The current 'datasource.time_resolution' "
            f"({time_resolution_spd} samples/day) is too low for "
            "this operation, unable to set a valid 'algorithm.delta_t'"
        )

    # Calculate the effective lag in samples
    effective_lag = int(lag_in_samples)

    if effective_lag >= full_sequence_length:
        raise ValueError(
            f"The current sequence length ({full_sequence_length} samples) "
            "is not enough to perform this operation using the calculated "
            f"lag ({lag_in_samples} samples). Please reduce "
            "'algorithm.delta_t' or ensure the data sequence length "
            "is sufficient"
        )

    # Sequence effective length and time series length
    sequence_length = full_sequence_length - effective_lag
    series_length = ceil(sequence_length / sampling_interval)

    return {
        "sequence_length": sequence_length,
        "sampling_interval": sampling_interval,
        "series_length": series_length,
        "samples_lag": effective_lag,
    }


def _compute_radiometric_parameters_w(
    settings: ConfigDict, dataset_paths: list[str]
) -> _Settings:
    from numpy import nanmax, nanmin

    profile_directory = settings.as_path(_REPOSITORY_PROFILE)

    vmin = inf
    vmax = -inf

    for dataset_path in dataset_paths:
        if not dataset_path:
            continue

        profile = load_profile(profile_directory, dataset_path)

        vmax = max(vmax, float(nanmax(profile)))
        vmin = min(vmin, float(nanmin(profile)))

    return {"vmin": float(vmin), "vmax": float(vmax)}


def _get_filter_parameters_w(settings: ConfigDict) -> _Settings:
    filter_frequency = settings.as_float(_FILTER_FREQUENCY)
    filter_bandwidth = settings.as_float(_FILTER_BANDWIDTH)

    # Compute the filter cut frequencies in cycles per hour
    filter_highcut = (filter_frequency + 0.5 * filter_bandwidth) / 24
    filter_lowcut = (filter_frequency - 0.5 * filter_bandwidth) / 24

    return {
        "frequency_lowcut": filter_lowcut,
        "frequency_highcut": filter_highcut,
    }


def _get_parameters_filename_w(settings: ConfigDict) -> Path:
    filename_prefix = get_filename_prefix("parameters", settings)

    algorithm_config = settings.section("algorithm")

    central_mask = 0.0
    windows_size = algorithm_config.as_float("windows_size")
    radius_min = algorithm_config.as_int("radius_min")
    radius_step = algorithm_config.as_int("radius_step")

    spatial_resolution = settings.as_float(_DATASOURCE_SPATIAL_RESOLUTION)

    time_resolution_spd = settings.as_int(_DATASOURCE_TIME_RESOLUTION)
    sampling_rate_spd = settings.as_int(_SUBSAMPLING_SAMPLING_RATE)
    timedelta_h = settings.as_int(_ALGORITHM_DELTA_T)

    filter_frequency = settings.as_float(_FILTER_FREQUENCY)
    filter_bandwidth = settings.as_float(_FILTER_BANDWIDTH)

    algorithm_id = settings.as_str("algorithm_id")

    filename_parts = [
        f"r{radius_min:d}-{radius_step:d}",
        f"w{windows_size:0.1f}-{central_mask:0.1f}",
        f"or{spatial_resolution:0.1f}-{time_resolution_spd:d}",
        f"fs{sampling_rate_spd:d}-dt{timedelta_h:d}",
        f"fc{filter_frequency:0.1f}-{filter_bandwidth:0.1f}",
        f"a[{algorithm_id}]",
    ]

    filename_base = "_".join(filename_parts)
    filename = f"{filename_prefix}_{filename_base}.dat"

    repository_config: dict[str, Path] = settings.get("repository", {})
    repository_path = repository_config["path"]

    return repository_path / filename


# ---------- Radial profile difference using a 1-D TDA algorithm ----------
# ---------- Derived parameters computation or retrieval  -----------------


def update_computed_parameters_v(
    settings: ConfigDict, dataset_paths: list[str]
) -> ConfigDict:
    # This function acts as a simple wrapper
    return _update_computed_parameters_common(
        settings,
        dataset_paths,
        _get_parameters_filename_v,
        _compute_parameters_v,
    )


def _compute_parameters_v(
    settings: ConfigDict, dataset_paths: list[str]
) -> _Settings:
    # Retrieve or calculate the derived parameters
    radius = _get_radius_value_w(settings, dataset_paths)
    spatial_parameters = _compute_spatial_parameters_v(settings, radius)

    sequence_length = len(dataset_paths)
    sampling_parameters = _get_sampling_parameters_w(settings, sequence_length)

    threshold_parameters = _compute_bt_thresholds_v(settings)

    radiometric_parameters = _compute_radiometric_parameters_w(
        settings, dataset_paths
    )

    filter_parameters = _get_filter_parameters_w(settings)

    return (
        spatial_parameters
        | sampling_parameters
        | radiometric_parameters
        | filter_parameters
        | threshold_parameters
    )


def _compute_spatial_parameters_v(
    settings: ConfigDict, radius: int
) -> _Settings:
    algorithm_config = settings.section("algorithm")

    central_mask = algorithm_config.as_float("central_mask")
    windows_size = algorithm_config.as_float("windows_size")

    spatial_resolution = settings.as_float(_DATASOURCE_SPATIAL_RESOLUTION)

    # Calculate the central-ignore and analysis sizes
    ignore = max(int(central_mask * radius / 100), 1)
    window = min(int(windows_size * radius / 100), radius)

    # Create the x-axis tick and limit values (kilometres per pixel)
    x_ticks = [
        spatial_resolution * (i + 0.5 - window) for i in range(2 * window)
    ]
    x_limit = spatial_resolution * window
    x_min = -x_limit
    x_max = x_limit

    radius_km = spatial_resolution * radius

    return {
        "ignore": ignore,
        "radius": radius,
        "radius_km": radius_km,
        "window": window,
        "x_min": x_min,
        "x_max": x_max,
        "x_ticks": x_ticks,
    }


def _compute_bt_thresholds_v(settings: ConfigDict) -> _Settings:
    algorithm_config = settings.section("algorithm")

    th_min = algorithm_config.as_int("bt_threshold_min")
    th_max = algorithm_config.as_int("bt_threshold_max")
    th_step = algorithm_config.as_int("bt_threshold_step")

    thresholds = list(range(th_min, th_max + 1, th_step))

    return {"bt_thresholds": thresholds}


def _get_parameters_filename_v(settings: ConfigDict) -> Path:
    filename_prefix = get_filename_prefix("parameters", settings)

    algorithm_config = settings.section("algorithm")

    central_mask = algorithm_config.as_float("central_mask")
    windows_size = algorithm_config.as_float("windows_size")

    threshold_min = algorithm_config.as_int("bt_threshold_min")
    threshold_max = algorithm_config.as_int("bt_threshold_max")
    threshold_step = algorithm_config.as_int("bt_threshold_step")

    spatial_resolution = settings.as_float(_DATASOURCE_SPATIAL_RESOLUTION)

    time_resolution_spd = settings.as_int(_DATASOURCE_TIME_RESOLUTION)
    sampling_rate_spd = settings.as_int(_SUBSAMPLING_SAMPLING_RATE)
    timedelta_h = settings.as_int(_ALGORITHM_DELTA_T)

    filter_frequency = settings.as_float(_FILTER_FREQUENCY)
    filter_bandwidth = settings.as_float(_FILTER_BANDWIDTH)

    algorithm_id = settings.as_str("algorithm_id")

    filename_parts = [
        f"w{windows_size:0.1f}-{central_mask:0.1f}",
        f"th{threshold_min:d}-{threshold_max:d}-{threshold_step:d}",
        f"or{spatial_resolution:0.1f}-{time_resolution_spd:d}",
        f"fs{sampling_rate_spd:d}-dt{timedelta_h:d}",
        f"fc{filter_frequency:0.1f}-{filter_bandwidth:0.1f}",
        f"a[{algorithm_id}]",
    ]

    filename_base = "_".join(filename_parts)
    filename = f"{filename_prefix}_{filename_base}.dat"

    repository_config: dict[str, Path] = settings.get("repository", {})
    repository_path = repository_config["path"]

    return repository_path / filename


# ---------- BT Field Difference Matrix using a 2-D TDA algorithm ----------
# ------------- Derived parameters computation or retrieval  ---------------


def update_computed_parameters_t(
    settings: ConfigDict, dataset_paths: list[str]
) -> ConfigDict:
    # This function acts as a simple wrapper
    return _update_computed_parameters_common(
        settings,
        dataset_paths,
        _get_parameters_filename_t,
        _compute_parameters_t,
    )


def _compute_parameters_t(
    settings: ConfigDict, dataset_paths: list[str]
) -> _Settings:
    # Retrieve or calculate the derived parameters
    radius = _get_radius_value_t(settings, dataset_paths)
    spatial_parameters = _compute_spatial_parameters_t(settings, radius)

    sequence_length = len(dataset_paths)
    sampling_parameters = _get_sampling_parameters_w(settings, sequence_length)

    threshold_parameters = _compute_bt_thresholds_v(settings)

    samples_lag: int = sampling_parameters["samples_lag"]
    lht_sequence = dataset_paths[:-samples_lag]
    rht_sequence = dataset_paths[samples_lag:]

    radiometric_parameters = _get_radiometric_parameters_t(
        settings, lht_sequence, rht_sequence
    )

    filter_parameters = _get_filter_parameters_w(settings)

    return (
        spatial_parameters
        | sampling_parameters
        | radiometric_parameters
        | filter_parameters
        | threshold_parameters
    )


def _get_radius_value_t(settings: ConfigDict, dataset_paths: list[str]) -> int:
    difference_directory = get_difference_directory_name(settings)

    radius = 0

    for dataset_path in dataset_paths:
        if not dataset_path:
            continue

        # Load the difference matrix data
        difference_data = load_matrix(difference_directory, dataset_path)

        if difference_data.shape[0] != difference_data.shape[1]:
            print(
                "WARNING: Non-square matrix found, dimensions are: "
                f"{difference_data.shape[1]}×{difference_data.shape[0]} px, "
                "using the bigger dimension"
            )

        diameter: int = max(difference_data.shape)

        if diameter % 2 != 0:
            print(
                f"WARNING: Found odd size diameter ({diameter}), "
                "using truncated radius"
            )

        radius = diameter // 2

        break

    return radius


def _compute_spatial_parameters_t(
    settings: ConfigDict, radius: int
) -> _Settings:
    spatial_resolution = settings.as_float(_DATASOURCE_SPATIAL_RESOLUTION)

    # Create the x-axis tick and limit values (kilometres per pixel)
    ax_ticks = [
        spatial_resolution * (i + 0.5 - radius) for i in range(2 * radius)
    ]
    ax_limit = spatial_resolution * radius
    ax_min = -ax_limit
    ax_max = ax_limit

    radius_km = spatial_resolution * radius

    return {
        "radius": radius,
        "radius_km": radius_km,
        "ax_min": ax_min,
        "ax_max": ax_max,
        "ax_ticks": ax_ticks,
    }


def _get_radiometric_parameters_t(
    settings: ConfigDict, lht_sequence: list[str], rht_sequence: list[str]
) -> _Settings:
    from goesdl.fileio import load_metadata, save_metadata

    # Retrieve or calculate derived parameters
    parameters_filename = _get_radiometric_parameters_filename_t(settings)

    parameters_data: _Settings

    if parameters_filename.exists():
        # Just retrieve the precomputed radiometric parameters
        parameters_data = load_metadata(parameters_filename)

    else:
        # Compute radiometric parameters with values derived from data
        parameters_data = _compute_radiometric_parameters_t(
            settings, lht_sequence, rht_sequence
        )

        save_metadata(parameters_filename, parameters_data)

    return parameters_data


def _compute_radiometric_parameters_t(
    settings: ConfigDict, lht_sequence: list[str], rht_sequence: list[str]
) -> _Settings:
    from numpy import nanmax, nanmin

    difference_directory = get_difference_directory_name(settings)

    vmin = inf
    vmax = -inf

    for lht_path, rht_path in zip(lht_sequence, rht_sequence):
        if not lht_path or not rht_path:
            continue

        # Load the difference matrix data
        difference_matrix = load_matrix(difference_directory, lht_path)

        vmax = max(vmax, float(nanmax(difference_matrix)))
        vmin = min(vmin, float(nanmin(difference_matrix)))

    return {"vmin": float(vmin), "vmax": float(vmax)}


def _get_parameters_filename_t(settings: ConfigDict) -> Path:
    filename_prefix = get_filename_prefix("parameters", settings)

    algorithm_config = settings.section("algorithm")

    threshold_min = algorithm_config.as_int("bt_threshold_min")
    threshold_max = algorithm_config.as_int("bt_threshold_max")
    threshold_step = algorithm_config.as_int("bt_threshold_step")

    spatial_resolution = settings.as_float(_DATASOURCE_SPATIAL_RESOLUTION)

    time_resolution_spd = settings.as_int(_DATASOURCE_TIME_RESOLUTION)
    sampling_rate_spd = settings.as_int(_SUBSAMPLING_SAMPLING_RATE)
    timedelta_h = settings.as_int(_ALGORITHM_DELTA_T)

    filter_frequency = settings.as_float(_FILTER_FREQUENCY)
    filter_bandwidth = settings.as_float(_FILTER_BANDWIDTH)

    algorithm_id = settings.as_str("algorithm_id")

    filename_parts = [
        f"th{threshold_min:d}-{threshold_max:d}-{threshold_step:d}",
        f"or{spatial_resolution:0.1f}-{time_resolution_spd:d}",
        f"fs{sampling_rate_spd:d}-dt{timedelta_h:d}",
        f"fc{filter_frequency:0.1f}-{filter_bandwidth:0.1f}",
        f"a[{algorithm_id}]",
    ]

    filename_base = "_".join(filename_parts)
    filename = f"{filename_prefix}_{filename_base}.dat"

    repository_config: dict[str, Path] = settings.get("repository", {})
    repository_path = repository_config["path"]

    return repository_path / filename


def _get_radiometric_parameters_filename_t(settings: ConfigDict) -> Path:
    filename_prefix = get_filename_prefix("radiometric_parameters", settings)

    algorithm_id = settings.as_str("algorithm_id")

    filename = f"{filename_prefix}_a[{algorithm_id}].dat"

    repository_config: dict[str, Path] = settings.get("repository", {})
    repository_path = repository_config["path"]

    return repository_path / filename


# ----------------------------------------------------------------------


def _calculate_difference_matrices(
    settings: ConfigDict, dataset_paths: list[str]
) -> None:
    from numpy import save

    difference_directory = get_difference_directory_name(settings)

    if difference_directory.exists():
        return

    difference_directory.mkdir(parents=True, exist_ok=True)
    reprojection_directory = settings.as_path("repository.reprojection")

    print_bar()
    print("Generating difference matrices...")

    parameters = _get_sampling_parameters_w(settings, len(dataset_paths))

    # Get the left and right sides sequences
    samples_lag: int = parameters["samples_lag"]
    lht_sequence = dataset_paths[:-samples_lag]
    rht_sequence = dataset_paths[samples_lag:]

    sequence_length: int = parameters["sequence_length"]

    for i in range(sequence_length):
        lht_path = lht_sequence[i]
        rht_path = rht_sequence[i]

        if not lht_path or not rht_path:
            continue

        lht_matrix = load_matrix(reprojection_directory, lht_path)
        rht_matrix = load_matrix(reprojection_directory, rht_path)

        difference_matrix_path = create_matrix_path(
            difference_directory, lht_path
        )

        # Create the difference matrix, if not exists
        if not difference_matrix_path.exists():
            # Calculate the difference matrix
            difference_matrix = lht_matrix - rht_matrix

            # Save the difference matrix
            save(difference_matrix_path, difference_matrix)

    print("Difference matrices generation completed!")
