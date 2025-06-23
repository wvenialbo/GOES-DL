from datetime import datetime, timedelta
from math import ceil, inf, nan
from pathlib import Path
from typing import Any, cast

from numpy import abs
from numpy import all as npall
from numpy import arange, bool_, floating, integer, isnan, load
from numpy import max as npmax
from numpy import min as npmin
from numpy import nanmean, nonzero, std
from numpy import sum as npsum
from numpy import zeros_like
from numpy.typing import NDArray
from scipy.interpolate import interp1d

from .config import ConfigDict

_Array = NDArray[floating[Any]]
_Index = NDArray[integer[Any]]
_Mask = NDArray[bool_]

_Series = list[_Array]
_Settings = dict[str, Any]
_Spectrum = Any

_prof_suffix = ".npz"
_matrix_suffix = ".npy"

# ---------- Environment tool utilities ----------


def is_colab() -> bool:
    """Detecta si corremos en el entorno Google Colab."""
    from os import getenv

    return bool(getenv("COLAB_RELEASE_TAG"))


# ---------- Settings information retrieval utilities ----------


def get_algorithm_info(
    settings: _Settings,
) -> tuple[float, float, float, float]:
    algorithm_config: dict[str, float] = settings.get("algorithm", {})

    # Extract values
    central_mask = algorithm_config.get("central_mask", nan)
    windows_size = algorithm_config.get("windows_size", nan)
    radius_min = algorithm_config.get("radius_min", nan)
    radius_step = algorithm_config.get("radius_step", nan)

    return central_mask, windows_size, radius_min, radius_step


def get_algorithm_extra(
    settings: _Settings,
) -> tuple[float, int, bool, str]:
    algorithm_config: _Settings = settings.get("algorithm", {})

    # Extract values
    delta_t: float = algorithm_config.get("delta_t", nan)
    sampling_rate: int = algorithm_config.get("sampling_rate", 0)
    invert_difference: bool = algorithm_config.get("invert_difference", False)
    diff_mode = "reversed" if invert_difference else "direct"

    return delta_t, sampling_rate, invert_difference, diff_mode


def get_event_info(settings: ConfigDict) -> tuple[str, str, str]:
    event_config = settings.section("event")

    event_name = event_config.as_str("name")
    time_start = event_config.as_str("time_start")
    time_end = event_config.as_str("time_end")

    return event_name, time_start, time_end


def get_filename_prefix(prefix: str, settings: ConfigDict) -> str:
    event_name, time_start, time_end = get_event_info(settings)

    time_start = time_start.replace("-", "").replace(":", "")
    time_end = time_end.replace("-", "").replace(":", "")

    return f"{event_name}_{prefix}_s{time_start}_e{time_end}"


# ---------- Profile loading utilities ----------


def load_profile(profile_directory: Path, filename: str) -> _Array:
    # Load the profile vector
    profile_data = load_profile_data(profile_directory, filename)

    profile: _Array = profile_data["profile"]

    return profile


def load_profile_data(profile_directory: Path, filename: str) -> _Settings:
    profile_path = create_profile_path(profile_directory, filename)

    profile_data: _Settings = load(profile_path)

    return profile_data


def load_matrix(directory: Path, filename: str) -> _Array:
    matrix_path = create_matrix_path(directory, filename)

    profile_data: _Array = load(matrix_path)

    return profile_data


def create_matrix_path(directory: Path, filename: str) -> Path:
    return create_path(directory, filename, _matrix_suffix)


def create_profile_path(directory: Path, filename: str) -> Path:
    return create_path(directory, filename, _prof_suffix)


def create_path(directory: Path, filename: str, suffix: str) -> Path:
    filepath = Path(filename).with_suffix(suffix)
    return directory / filepath.name


def get_difference_directory_name(settings: ConfigDict) -> Path:
    timedelta_h = settings.as_int("algorithm.delta_t")
    difference_directory = settings.as_path("repository.difference")
    return Path(f"{str(difference_directory)}_{timedelta_h}h")


# ---------- Fill missing values ----------


def _get_known_indices(profile: _Array) -> tuple[_Index, _Mask]:
    if profile.ndim != 1:
        raise ValueError("Array must be 1-dimensional")
    nan_mask = isnan(profile)
    known_indices = nonzero(~nan_mask)[0]
    if known_indices.size == 0:
        raise ValueError("Array contains only NaNs")
    return known_indices, nan_mask


def fill_inner_missing_values(profile: _Array) -> None:
    # Fill inner missing values using interpolation
    known_indices, nan_mask = _get_known_indices(profile)
    known_values = profile[known_indices]

    num_known_points = known_indices.size

    interp_kind: Any
    if num_known_points >= 4:
        interp_kind = "cubic"
    elif num_known_points == 3:
        interp_kind = "quadratic"
    elif num_known_points == 2:
        interp_kind = "linear"
    elif num_known_points == 1:
        interp_kind = "zero"
    else:
        raise ValueError("Array contains no known points")

    interp_func = interp1d(
        known_indices,
        known_values,
        kind=interp_kind,
        fill_value="extrapolate",
        bounds_error=False,
        assume_sorted=True,
    )

    unknown_indices = nonzero(nan_mask)[0]

    profile[unknown_indices] = interp_func(unknown_indices)


def fill_leading_missing_values(profile: _Array) -> None:
    # Fill the leading missing values with the first valid value
    known_indices, _ = _get_known_indices(profile)
    if (first_known_index := known_indices[0]) > 0:
        first_known_value = profile[first_known_index]
        profile[:first_known_index] = first_known_value


def fill_trailing_missing_values(profile: _Array) -> None:
    # Fill the trainling missing values with the last valid value
    known_indices, _ = _get_known_indices(profile)
    if (last_known_index := known_indices[-1]) < len(profile) - 1:
        last_known_value = profile[last_known_index]
        profile[last_known_index + 1 :] = last_known_value


def fill_missing_pixels(
    matrix: _Array,
    window_size: int = 5,
    max_iterations: int = 100,
    fill_remaining_with_global_mean: bool = True,
) -> _Array:
    if window_size % 2 == 0:
        raise ValueError("'window_size' must be an odd number")

    current_array = matrix

    rows: int
    cols: int
    rows, cols = current_array.shape
    half_window = window_size // 2

    is_missing = isnan(current_array)
    missing_pixels_count = npsum(is_missing)

    iteration = 0
    while missing_pixels_count > 0 and iteration < max_iterations:
        iteration += 1

        array_for_current_iteration = current_array.copy()

        current_missing_mask = isnan(current_array)
        pixels_to_impute_this_iteration_count = 0

        missing_row_indices, missing_col_indices = nonzero(
            current_missing_mask
        )

        imputed_values_buffer = zeros_like(current_array)

        successfully_imputed_mask = zeros_like(current_array, dtype=bool)

        for r_idx, c_idx in zip(missing_row_indices, missing_col_indices):
            r_start = max(0, int(r_idx - half_window))
            r_end = min(rows, int(r_idx + half_window + 1))
            c_start = max(0, int(c_idx - half_window))
            c_end = min(cols, int(c_idx + half_window + 1))

            window = array_for_current_iteration[r_start:r_end, c_start:c_end]

            if not npall(isnan(window)):
                imputed_value = nanmean(window)
                imputed_values_buffer[r_idx, c_idx] = imputed_value
                successfully_imputed_mask[r_idx, c_idx] = True
                pixels_to_impute_this_iteration_count += 1

        current_array[successfully_imputed_mask] = imputed_values_buffer[
            successfully_imputed_mask
        ]

        is_missing = isnan(current_array)
        missing_pixels_count = npsum(is_missing)

        if (
            pixels_to_impute_this_iteration_count == 0
            and missing_pixels_count > 0
        ):
            break

    if missing_pixels_count > 0 and fill_remaining_with_global_mean:
        global_mean = nanmean(current_array)

        if not isnan(global_mean):
            current_array[is_missing] = global_mean

    return current_array


# ---------- Plotting helpers ----------


def get_time_ticks(
    settings: ConfigDict, tick_interval: int = 6
) -> tuple[_Array, list[int], float]:
    time_start = settings.as_str("event.time_start")
    date_format = settings.as_str("date_format.input")
    sampling_rate = settings.as_int("subsampling.sampling_rate") // 24

    begin_offset = settings.as_int("parameters.sampling_offset")
    series_length = settings.as_int("parameters.series_length")

    dt_start = datetime.strptime(time_start, date_format)
    dt_start += timedelta(hours=begin_offset / sampling_rate)
    dt_end = dt_start + timedelta(hours=series_length / sampling_rate)

    time_hours = (dt_end - dt_start).total_seconds() / 3600
    duration_per_point_hours = 1 / sampling_rate

    start_hour_of_day = dt_start.hour

    first_real_tick_hour_of_day = (
        start_hour_of_day // tick_interval
    ) * tick_interval

    if first_real_tick_hour_of_day < start_hour_of_day:
        first_real_tick_hour_of_day += tick_interval

    first_tick_position_on_x_axis = (
        first_real_tick_hour_of_day - start_hour_of_day
    )

    tick_position = arange(
        first_tick_position_on_x_axis,
        time_hours + duration_per_point_hours,
        tick_interval,
    )

    tick_label = [
        (int(first_real_tick_hour_of_day + i * tick_interval)) % 24
        for i in range(len(tick_position))
    ]

    return tick_position, tick_label, time_hours


def get_date_markers(
    settings: ConfigDict, label_format: str = "%Y-%m-%d"
) -> tuple[list[float], list[str]]:
    time_start = settings.as_str("event.time_start")
    date_format = settings.as_str("date_format.input")
    sampling_rate = settings.as_int("subsampling.sampling_rate") // 24

    begin_offset = settings.as_int("parameters.sampling_offset")
    series_length = settings.as_int("parameters.series_length")

    dt_start = datetime.strptime(time_start, date_format)
    dt_start_offsetted = dt_start + timedelta(
        hours=begin_offset / sampling_rate
    )
    dt_end = dt_start_offsetted + timedelta(
        hours=series_length / sampling_rate
    )

    time_hours = (dt_end - dt_start_offsetted).total_seconds() / 3600

    hours_since_last_midnight = (
        dt_start_offsetted.hour + dt_start_offsetted.minute / 60.0
    )
    hours_to_next_midnight = (24 - hours_since_last_midnight) % 24

    if (
        hours_to_next_midnight == 0
        and dt_start_offsetted.hour == 0
        and dt_start_offsetted.minute == 0
    ):
        first_midnight_position = 0.0
    else:
        first_midnight_position = hours_to_next_midnight

    midnight_pos = [
        first_midnight_position + (j * 24)
        for j in range(int(ceil(time_hours / 24)) + 2)
    ]

    midnight_pos = [pos for pos in midnight_pos if 0 <= pos <= time_hours]

    date_labels: list[str] = []
    for pos in midnight_pos:
        current_datetime = dt_start_offsetted + timedelta(hours=pos)
        date_labels.append(current_datetime.strftime(label_format))

    return midnight_pos, date_labels


def combine_tick_labels(
    tick_positions: list[float] | _Array,
    tick_labels_hours: list[int],
    midnight_positions: list[float],
    midnight_labels_dates: list[str],
) -> list[str]:
    final_tick_labels: list[str] = []

    midnight_label_index = 0

    for i, pos_ in enumerate(tick_positions):
        pos = cast(float, pos_)
        label_hour = tick_labels_hours[i]

        if label_hour == 0 and midnight_label_index < len(midnight_positions):
            if abs(pos - midnight_positions[midnight_label_index]) < 0.1:
                final_tick_labels.append(
                    midnight_labels_dates[midnight_label_index]
                )
                midnight_label_index += 1
            else:
                final_tick_labels.append(f"{label_hour:02d}:00h")
        else:
            final_tick_labels.append(f"{label_hour:02d}:00h")

    return final_tick_labels


def calculate_global_limits(
    input_series: _Series,
) -> tuple[float, float, float, float]:
    max_abs_val = 0.0
    max_std_val = 0.0

    global_min_val = inf
    global_max_val = -inf

    for series in input_series:
        current_series_max_abs = npmax(abs(series))
        if current_series_max_abs > max_abs_val:
            max_abs_val = float(current_series_max_abs)

        current_series_max_std = std(series)
        if current_series_max_std > max_std_val:
            max_std_val = float(current_series_max_std)

        current_series_min = npmin(series)
        current_series_max = npmax(series)

        if current_series_min < global_min_val:
            global_min_val = float(current_series_min)

        if current_series_max > global_max_val:
            global_max_val = float(current_series_max)

    return global_min_val, global_max_val, max_abs_val, max_std_val
