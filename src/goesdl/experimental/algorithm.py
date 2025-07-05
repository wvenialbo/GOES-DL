from collections.abc import Callable
from pathlib import Path
from typing import Any, cast

from numpy import floating
from numpy.typing import NDArray

from .config import ConfigDict
from .report_tools import (
    print_algorithm_parameters_report,
    print_bar,
    print_line,
)
from .utilities import (
    fill_inner_missing_values,
    fill_leading_missing_values,
    fill_trailing_missing_values,
    get_difference_directory_name,
    get_filename_prefix,
    load_matrix,
    load_profile,
)

_Array = NDArray[floating[Any]]

_ALGORITHM_DELTA_T = "algorithm.delta_t"
_INVERT_DIFFERENCE = "algorithm.invert_difference"


def run_algorithm(
    settings: ConfigDict, dataset_paths: list[str]
) -> list[list[float]]:
    algorithm_id = settings.as_str("algorithm_id")

    if algorithm_id == "algorithm_0":
        return run_algorithm_w(settings, dataset_paths)

    if algorithm_id == "algorithm_1":
        return run_algorithm_v(settings, dataset_paths)

    return run_algorithm_t(settings, dataset_paths)


def _run_algorithm_common(
    settings: ConfigDict,
    dataset_paths: list[str],
    get_algorithm_filename_func: Callable[[ConfigDict], Path],
    run_algorithm_func: Callable[[ConfigDict, list[str]], list[list[float]]],
) -> list[list[float]]:
    from goesdl.fileio import load_metadata, save_metadata

    print_algorithm_parameters_report(settings)

    # Retrieve or build the time series
    timeseries_filename = get_algorithm_filename_func(settings)

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

        raw_time_series = run_algorithm_func(settings, dataset_paths)

        save_metadata(timeseries_filename, raw_time_series)

        print("Time series generation completed!")

    return raw_time_series


def _get_sequences(
    settings: ConfigDict, dataset_paths: list[str]
) -> tuple[list[str], list[str], int]:
    # Get the left and right term sequences
    samples_lag = settings.as_int("parameters.samples_lag")
    lht_sequence = dataset_paths[:-samples_lag]
    rht_sequence = dataset_paths[samples_lag:]

    sequence_length = settings.as_int("parameters.sequence_length")

    return lht_sequence, rht_sequence, sequence_length


def _load_preprocessed_profile(
    profile_directory: Path, dataset_path: str, extent: int
) -> _Array:
    # Load the profile
    profile_array = load_profile(profile_directory, dataset_path)

    # Limit to the extent of analysis
    profile_array = profile_array[:extent]

    # Fill missing values
    return _fill_missing_profile_values(profile_array)


def _load_preprocessed_matrix(
    difference_directory: Path, difference_path: str
) -> _Array:
    # Load the difference matrix
    return load_matrix(difference_directory, difference_path)


def _fill_missing_profile_values(profile: _Array) -> _Array:
    fill_leading_missing_values(profile)
    fill_trailing_missing_values(profile)
    fill_inner_missing_values(profile)
    return profile


# ---------- Radial profile difference time series algorithm ----------
# ----------     (author: Waldemar Villamayor-Venialbo)      ----------


def run_algorithm_w(
    settings: ConfigDict, dataset_paths: list[str]
) -> list[list[float]]:
    raw_time_series = _run_algorithm_common(
        settings, dataset_paths, _get_algorithm_filename_w, _run_algorithm_w
    )

    if settings.as_bool(_INVERT_DIFFERENCE):
        print_line()
        print("Inverting timeseries data...")
        for j in range(len(raw_time_series)):
            for k in range(len(raw_time_series[j])):
                raw_time_series[j][k] = -raw_time_series[j][k]
        print("Time series inverted!")

    print_bar()

    return raw_time_series


def _run_algorithm_w(
    settings: ConfigDict, dataset_paths: list[str]
) -> list[list[float]]:
    from numpy import nan

    # Get the left and right term sequences
    lht_sequence, rht_sequence, sequence_length = _get_sequences(
        settings, dataset_paths
    )

    parameters = settings.section("parameters")

    window = parameters.as_int("window")

    radii = parameters.get_astype("radii", list[int])
    radii_count = len(radii)

    raw_time_series: list[list[float]] = [[] for _ in range(radii_count)]

    profile_directory = settings.as_path("repository.profile")

    # Execute the algorithm
    for i in range(sequence_length):
        lht_path = lht_sequence[i]
        rht_path = rht_sequence[i]

        if not lht_path or not rht_path:
            for k in range(radii_count):
                raw_time_series[k].append(nan)
            continue

        # Load the preprocessed profiles
        lht_profile = _load_preprocessed_profile(
            profile_directory, lht_path, window
        )
        rht_profile = _load_preprocessed_profile(
            profile_directory, rht_path, window
        )

        # Calculate the profile difference
        difference = lht_profile - rht_profile

        # Add point to time series
        for k in range(radii_count):
            radius_k = radii[k]
            value_at_radius = difference[radius_k]
            raw_time_series[k].append(value_at_radius)

    return raw_time_series


def _get_algorithm_filename_w(settings: ConfigDict) -> Path:
    filename_prefix = get_filename_prefix("timeseries", settings)

    timedelta_h = settings.as_int(_ALGORITHM_DELTA_T)

    algorithm_config = settings.section("algorithm")
    central_mask = 0.0
    windows_size = algorithm_config.as_float("windows_size")
    radius_min = algorithm_config.as_float("radius_min")
    radius_step = algorithm_config.as_float("radius_step")

    algorithm_id = settings.as_str("algorithm_id")

    filename_parts = [
        f"dt{timedelta_h:d}",
        f"r{radius_min:0.0f}-{radius_step:0.0f}",
        f"w{windows_size:0.1f}-{central_mask:0.1f}",
        f"a[{algorithm_id}]",
    ]

    filename_base = "_".join(filename_parts)
    filename = f"{filename_prefix}_{filename_base}.dat"

    repository_config: dict[str, Path] = settings.get("repository", {})
    repository_path = repository_config["path"]

    return repository_path / filename


# ---------- Radial profile difference 1-D TDA algorithm ----------
# ---------- (author: Waldemar Villamayor-Venialbo)  --------------


def run_algorithm_v(
    settings: ConfigDict, dataset_paths: list[str]
) -> list[list[float]]:
    raw_time_series = _run_algorithm_common(
        settings, dataset_paths, _get_algorithm_filename_v, _run_algorithm_v
    )

    print_bar()

    return raw_time_series


def _run_algorithm_v(
    settings: ConfigDict, dataset_paths: list[str]
) -> list[list[float]]:
    from numpy import nan

    # Get the left and right term sequences
    lht_sequence, rht_sequence, sequence_length = _get_sequences(
        settings, dataset_paths
    )

    parameters = settings.section("parameters")

    ignore = parameters.as_int("ignore")
    window = parameters.as_int("window")

    bt_thresholds = settings.get_astype("parameters.bt_thresholds", list[int])
    threshold_count = len(bt_thresholds)

    invert_difference = settings.as_bool(_INVERT_DIFFERENCE)
    small_blob_size = settings.as_int("algorithm.small_blob_size")
    spatial_resolution = settings.as_float("datasource.spatial_resolution")

    profile_directory = settings.as_path("repository.profile")

    verbose = settings.as_bool("display.verbose")

    bt_scale = settings.as_int("algorithm.bt_scale", 1)

    raw_time_series: list[list[float]] = [[] for _ in range(threshold_count)]

    # Execute the algorithm
    for i in range(sequence_length):
        lht_path = lht_sequence[i]
        rht_path = rht_sequence[i]

        if verbose:
            print(f"Generating data point {i + 1} of {sequence_length}\n")

        if not lht_path or not rht_path:
            if verbose:
                print("... no data available\n")
            for k in range(threshold_count):
                raw_time_series[k].append(nan)
            continue

        # Calculate the profile difference
        difference = _algorithm_v_step1(
            profile_directory, lht_path, rht_path, window, invert_difference
        )

        if bt_scale > 1:
            difference *= bt_scale

        for k, threshold in enumerate(bt_thresholds):
            # Compute the H0 maximum persistence
            lifetime = _algorithm_v_step2(
                difference,
                threshold,
                spatial_resolution,
                small_blob_size,
                ignore,
            )

            # Create the maximum persistence time series
            raw_time_series[k].append(lifetime)

    return raw_time_series


def _algorithm_v_step1(
    profile_directory: Path,
    lht_path: str,
    rht_path: str,
    extent: int,
    invert_difference: bool,
) -> _Array:
    lht_profile = _load_preprocessed_profile(
        profile_directory, lht_path, extent
    )
    rht_profile = _load_preprocessed_profile(
        profile_directory, rht_path, extent
    )

    # Calculate the profile difference
    return (
        rht_profile - lht_profile
        if invert_difference
        else lht_profile - rht_profile
    )


def _algorithm_v_step2(
    difference: _Array,
    threshold: float,
    spatial_resolution: float,
    small_blob_size: int,
    mask_size: int,
) -> float:
    from numpy import concatenate, where
    from scipy.ndimage import distance_transform_cdt

    from goesdl.experimental.topology import (
        create_complex,
        maximum_persistence,
        remove_small_blobs,
    )

    # Calculate the thresholded difference profile
    thresholded = where(difference < threshold, 1, 0)
    thresholded[:mask_size] = 1

    # Remove small blobs
    thresholded = remove_small_blobs(thresholded, small_blob_size)

    # Mirror the thresholded profile
    mirrored = concatenate((thresholded[::-1], thresholded))

    # Calculate the (Chebyshev) distance transform
    dtransform = (
        cast(_Array, distance_transform_cdt(mirrored)) * spatial_resolution
    )

    # Create cubical complex
    cubical_complex = create_complex(dtransform, False)

    # Calculate the persistent homology (sublevel set filtration)
    persistence_pairs = cubical_complex.persistence()
    # plot_persistence_diagram(persistence_pairs)

    # Compute the H0 maximum persistence
    lifetime, _ = maximum_persistence(0, persistence_pairs)

    return float(lifetime)


def _get_algorithm_filename_v(settings: ConfigDict) -> Path:
    filename_prefix = get_filename_prefix("timeseries", settings)

    timedelta_h = settings.as_int(_ALGORITHM_DELTA_T)

    algorithm_config = settings.section("algorithm")
    central_mask = algorithm_config.as_float("central_mask")
    windows_size = algorithm_config.as_float("windows_size")
    threshold_min = algorithm_config.as_int("bt_threshold_min")
    threshold_max = algorithm_config.as_int("bt_threshold_max")
    threshold_step = algorithm_config.as_int("bt_threshold_step")
    small_blob_size = algorithm_config.as_int("small_blob_size")
    bt_scale = algorithm_config.as_int("bt_scale", 1)

    invert = settings.as_bool(_INVERT_DIFFERENCE)

    inverted = "inv" if invert else ""

    algorithm_id = settings.as_str("algorithm_id")

    filename_parts = [
        f"dt{timedelta_h:d}_x{bt_scale:d}",
        f"th{threshold_min:d}-{threshold_max:d}-{threshold_step:d}",
        f"w{windows_size:0.1f}-{central_mask:0.1f}",
        f"sb{small_blob_size}_a[{algorithm_id}]{inverted}",
    ]

    filename_base = "_".join(filename_parts)
    filename = f"{filename_prefix}_{filename_base}.dat"

    repository_config: dict[str, Path] = settings.get("repository", {})
    repository_path = repository_config["path"]

    return repository_path / filename


# ---------- Field difference 2-D TDA algorithm ----------
# ------------- (author: Sarah Tymochko)  ----------------
# ----- (implementor: Waldemar Villamayor-Venialbo)  -----


def run_algorithm_t(
    settings: ConfigDict, dataset_paths: list[str]
) -> list[list[float]]:
    from goesdl.fileio import load_metadata, save_metadata

    print_bar()

    # Retrieve or build the time series
    timeseries_filename = _get_algorithm_filename_t(settings)

    bt_thresholds = settings.get_astype("parameters.bt_thresholds", list[int])
    bt_missing_thresholds: list[int] = []

    raw_time_series: dict[int, list[float]] = {}

    if timeseries_filename.exists():
        # Just retrieve the precomputed time series
        print("Retrieving timeseries data...")

        raw_time_series = load_metadata(timeseries_filename)

        bt_missing_thresholds.extend(
            threshold
            for threshold in bt_thresholds
            if threshold not in raw_time_series
        )

        print("Time series retrieved!")

    else:
        bt_missing_thresholds = bt_thresholds

    if bt_missing_thresholds:
        # Compute parameters with values derived from data and other
        # parameters
        print("Generating time series...")

        raw_time_series |= _run_algorithm_t(
            settings, dataset_paths, bt_missing_thresholds
        )

        save_metadata(timeseries_filename, raw_time_series)

        print("Time series generation completed!")

    print_bar()

    print_algorithm_parameters_report(settings)

    return list(raw_time_series.values())


def _run_algorithm_t(
    settings: ConfigDict, dataset_paths: list[str], bt_thresholds: list[int]
) -> dict[int, list[float]]:
    from numpy import nan

    # Get the left and right term sequences
    lht_sequence, rht_sequence, sequence_length = _get_sequences(
        settings, dataset_paths
    )

    invert_difference = settings.as_bool(_INVERT_DIFFERENCE)
    small_blob_size = settings.as_int("algorithm.small_blob_size")
    spatial_resolution = settings.as_float("datasource.spatial_resolution")

    profile_directory = get_difference_directory_name(settings)

    verbose = settings.as_bool("display.verbose")

    raw_time_series: dict[int, list[float]] = {
        threshold: [] for threshold in bt_thresholds
    }

    # Execute the algorithm
    for i in range(sequence_length):
        lht_path = lht_sequence[i]
        rht_path = rht_sequence[i]

        if verbose:
            print(f"Generating data point {i + 1} of {sequence_length}\n")

        if not lht_path or not rht_path:
            if verbose:
                print("... no data available\n")
            for threshold in bt_thresholds:
                raw_time_series[threshold].append(nan)
            continue

        # Calculate the profile difference
        difference = _algorithm_t_step1(
            profile_directory, lht_path, invert_difference
        )

        for threshold in bt_thresholds:
            # Compute the H1 maximum persistence
            lifetime = _algorithm_t_step2(
                difference,
                threshold,
                spatial_resolution,
                small_blob_size,
            )

            # Create the maximum persistence time series
            raw_time_series[threshold].append(lifetime)

    return raw_time_series


def _algorithm_t_step1(
    difference_directory: Path,
    difference_path: str,
    invert_difference: bool,
) -> _Array:
    difference_matrix = _load_preprocessed_matrix(
        difference_directory, difference_path
    )
    return -difference_matrix if invert_difference else difference_matrix


def _algorithm_t_step2(
    difference: _Array,
    threshold: float,
    spatial_resolution: float,
    small_blob_size: int,
) -> float:
    from numpy import where
    from scipy.ndimage import distance_transform_cdt

    from goesdl.experimental.topology import (
        create_complex,
        maximum_persistence,
        remove_small_blobs,
    )

    # Calculate the thresholded difference matrix
    thresholded = where(difference < threshold, 1, 0)

    # Remove small blobs
    thresholded = remove_small_blobs(thresholded, small_blob_size)

    # Calculate the (Chebyshev) distance transform
    dtransform = (
        cast(_Array, distance_transform_cdt(thresholded)) * spatial_resolution
    )

    # Create cubical complex
    cubical_complex = create_complex(dtransform, False)

    # Calculate the persistent homology (sublevel set filtration)
    persistence_pairs = cubical_complex.persistence()
    # plot_persistence_diagram(persistence_pairs)

    # Compute the H1 maximum persistence
    lifetime, _ = maximum_persistence(1, persistence_pairs)

    return float(lifetime)


def _get_algorithm_filename_t(settings: ConfigDict) -> Path:
    filename_prefix = get_filename_prefix("timeseries", settings)

    timedelta_h = settings.as_int(_ALGORITHM_DELTA_T)

    algorithm_config = settings.section("algorithm")
    threshold_min = algorithm_config.as_int("bt_threshold_min")
    threshold_max = algorithm_config.as_int("bt_threshold_max")
    threshold_step = algorithm_config.as_int("bt_threshold_step")
    small_blob_size = algorithm_config.as_int("small_blob_size")

    invert = settings.as_bool(_INVERT_DIFFERENCE)

    inverted = "inv" if invert else ""

    algorithm_id = settings.as_str("algorithm_id")

    filename_parts = [
        f"dt{timedelta_h:d}",
        f"th{threshold_min:d}-{threshold_max:d}-{threshold_step:d}",
        f"sb{small_blob_size}_a[{algorithm_id}]{inverted}",
    ]

    filename_base = "_".join(filename_parts)
    filename = f"{filename_prefix}_{filename_base}.dat"

    repository_config: dict[str, Path] = settings.get("repository", {})
    repository_path = repository_config["path"]

    return repository_path / filename
