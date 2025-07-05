from math import floor, isnan
from typing import Any

from .config import ConfigDict

_bar_length = 120


# ---------- Report printing utilities ----------


def print_separator(char: str = "=", length: int = _bar_length) -> None:
    """Prints a customizable separator line."""
    print(char * length)


def print_line(length: int = _bar_length) -> None:
    print_separator(char="-", length=length)


def print_bar(length: int = _bar_length) -> None:
    print_separator(char="=", length=length)


def print_row(
    label: str,
    value: Any,
    sep: str = " : ",
    lf: str = "<30",
    cf: str = "",
    tf: str = "",
    vf: str = "",
    sv: str = "",
    sf: str = "",
    ss: str = " ",
) -> None:
    ss = ss if sv else ""
    label_text = f"{label:{tf}}"
    value_text = f"{value:{vf}}{ss}{sv:{sf}}"
    print(f"{label_text:{lf}}{sep}{value_text:{cf}}")


def print_event_report(settings: ConfigDict) -> None:
    event_config = settings.section("event")

    # Extract values
    event_name = event_config.as_str("name")
    time_start = event_config.as_str("time_start")
    time_end = event_config.as_str("time_end")

    # Print values
    print(f"Event name              : {event_name}")
    print(f"Coverage start time     : {time_start}")
    print(f"Coverage end time       : {time_end}")


def print_datasource_report(settings: ConfigDict) -> None:
    datasource_config = settings.section("datasource")

    # Extract values
    project = datasource_config.as_str("project")
    origin = ", ".join(datasource_config.get("origin", ["N/A"]))
    channel = datasource_config.as_str("channel")
    scene = datasource_config.as_str("scene")
    spatial_resolution = datasource_config.as_float("spatial_resolution")
    time_resolution = datasource_config.as_int("time_resolution")

    # Print values
    print(f"Datasets                : {project}")
    print(f"Satellite               : {origin}")
    print(f"Channel                 : {channel}")
    print(f"Scene                   : {scene}")
    print(
        f"Spatial resolution      : {spatial_resolution:>2.1f} kilometres/pixel"
    )
    print(f"Time resolution         : {time_resolution:>3d} frames/day")


def print_repository_report(settings: ConfigDict) -> None:
    repo_config = settings.section("repository")

    # Extract values
    root_path = repo_config.as_str("root")
    dataset_path = repo_config.as_str("path")
    difference_directory = repo_config.as_str("difference")
    profile_directory = repo_config.as_str("profile")
    reprojection_directory = repo_config.as_str("reprojection")

    # Print values
    print(f"Repository root path    : {root_path}")
    print(f"Dataset directory path  : {dataset_path}")
    print(f"Difference files path   : {difference_directory}")
    print(f"Profile files path      : {profile_directory}")
    print(f"Reprojection files path : {reprojection_directory}")


def print_setup_report(settings: ConfigDict) -> None:
    print_bar()
    print("Project configuration values")
    print_line()

    algorithm_name = settings.as_str("algorithm.name")
    print(f"Algorithm               : {algorithm_name}")
    print_line()

    # Event configuration
    print_event_report(settings)

    print_line()

    # Datasource configuration
    print_datasource_report(settings)

    print_line()

    # Repository configuration
    print_repository_report(settings)

    print_bar()


def print_derived_parameters_report(settings: ConfigDict) -> None:
    algorithm_id = settings.as_str("algorithm_id")

    if algorithm_id == "algorithm_0":
        return print_derived_parameters_report_w(settings)

    if algorithm_id == "algorithm_1":
        return print_derived_parameters_report_v(settings)

    return print_derived_parameters_report_t(settings)


def print_derived_parameters_report_w(settings: ConfigDict) -> None:
    parameters = settings.section("parameters")

    vmax: float = parameters.as_float("vmax")
    vmin: float = parameters.as_float("vmin")

    print_bar()
    print("Computed Parameters")
    print_line()

    # Radiometric parameters

    print(f"Minimum BT         : {vmin:>4.2f} Kelvin")
    print(f"Maximum BT         : {vmax:>4.2f} Kelvin")

    print_line()

    # Sampling paramters

    sequence_length = parameters.as_int("sequence_length")
    sampling_interval = parameters.as_int("sampling_interval")
    series_length = parameters.as_int("series_length")
    samples_lag = parameters.as_int("samples_lag")

    print(f"Sequence length    : {sequence_length:>4d} data points")
    print(f"Sequence lag       : {samples_lag:>4d} data points")
    print(f"Sampling interval  : {sampling_interval:>4d} data points")
    print(f"Time series lenght : {series_length:>4d} data points")

    sampling_rate = settings.as_int("subsampling.sampling_rate")
    time_resolution = settings.as_int("datasource.time_resolution")
    resolution_ratio = time_resolution // sampling_rate
    sampling_ratio = f"1:{resolution_ratio}"

    print(f"Sampling ratio     : {sampling_ratio:>4}")

    print_line()

    # Spatial parameters

    ignore = 0
    x_min = parameters.as_float("x_min")

    window = parameters.as_int("window")
    x_max = parameters.as_float("x_max")

    radius = parameters.as_int("radius")
    radius_km = parameters.as_float("radius_km")

    print(f"Central mask       : {ignore:>4d} pixels   (~{x_min:.0f}-km)")
    print(f"Analysis window    : {window:>4d} pixels   (~{x_max:.0f}-km)")
    print(f"Analysis extent    : {radius:>4d} pixels   (~{radius_km:.0f}-km)")

    print_line()

    label, sep = "Analysis radii", ":"

    radii = parameters.get_astype("radii", list[int])
    radii_km = parameters.get_astype("radii_km", list[float])

    for radius, radius_km in zip(radii, radii_km):
        print(f"{label:<19}{sep} {radius:>4d}-th pixel (~{radius_km:.0f}-km)")
        label, sep = "", " "


def print_derived_parameters_report_v(settings: ConfigDict) -> None:
    parameters = settings.section("parameters")

    vmax: float = parameters.as_float("vmax")
    vmin: float = parameters.as_float("vmin")

    print_bar()
    print("Computed Parameters")
    print_line()

    # Radiometric parameters

    print(f"Minimum BT         : {vmin:>4.2f} Kelvin")
    print(f"Maximum BT         : {vmax:>4.2f} Kelvin")

    print_line()

    # Sampling paramters

    sequence_length = parameters.as_int("sequence_length")
    sampling_interval = parameters.as_int("sampling_interval")
    series_length = parameters.as_int("series_length")
    samples_lag = parameters.as_int("samples_lag")

    print(f"Sequence length    : {sequence_length:>4d} data points")
    print(f"Sequence lag       : {samples_lag:>4d} data points")
    print(f"Sampling interval  : {sampling_interval:>4d} data points")
    print(f"Time series lenght : {series_length:>4d} data points")

    sampling_rate = settings.as_int("subsampling.sampling_rate")
    time_resolution = settings.as_int("datasource.time_resolution")
    resolution_ratio = time_resolution // sampling_rate
    sampling_ratio = f"1:{resolution_ratio}"

    print(f"Sampling ratio     : {sampling_ratio:>4}")

    print_line()

    # Spatial parameters

    ignore = parameters.as_int("ignore")
    x_min = parameters.as_float("x_min")

    window = parameters.as_int("window")
    x_max = parameters.as_float("x_max")

    radius = parameters.as_int("radius")
    radius_km = parameters.as_float("radius_km")

    print(f"Central mask       : {ignore:>4d} pixels   (~{x_min:.0f}-km)")
    print(f"Analysis window    : {window:>4d} pixels   (~{x_max:.0f}-km)")
    print(f"Analysis extent    : {radius:>4d} pixels   (~{radius_km:.0f}-km)")


def print_derived_parameters_report_t(settings: ConfigDict) -> None:
    parameters = settings.section("parameters")

    vmax: float = parameters.as_float("vmax")
    vmin: float = parameters.as_float("vmin")

    print_bar()
    print("Computed Parameters")
    print_line()

    # Radiometric parameters

    print(f"Minimum BT (diff.) : {vmin:>4.2f} Kelvin")
    print(f"Maximum BT (diff.) : {vmax:>4.2f} Kelvin")

    print_line()

    # Sampling paramters

    sequence_length = parameters.as_int("sequence_length")
    sampling_interval = parameters.as_int("sampling_interval")
    series_length = parameters.as_int("series_length")
    samples_lag = parameters.as_int("samples_lag")

    print(f"Sequence length    : {sequence_length:>4d} data points")
    print(f"Sequence lag       : {samples_lag:>4d} data points")
    print(f"Sampling interval  : {sampling_interval:>4d} data points")
    print(f"Time series lenght : {series_length:>4d} data points")

    sampling_rate = settings.as_int("subsampling.sampling_rate")
    time_resolution = settings.as_int("datasource.time_resolution")
    resolution_ratio = time_resolution // sampling_rate
    sampling_ratio = f"1:{resolution_ratio}"

    print(f"Sampling ratio     : {sampling_ratio:>4}")

    print_line()

    # Spatial parameters

    radius = parameters.as_int("radius")
    radius_km = parameters.as_float("radius_km")

    print(f"Analysis extent    : {radius:>4d} pixels   (~{radius_km:.0f}-km)")


def print_algorithm_parameters_report(settings: ConfigDict) -> None:
    algorithm_id = settings.as_str("algorithm_id")

    if algorithm_id == "algorithm_0":
        return print_algorithm_parameters_report_w(settings)

    if algorithm_id == "algorithm_1":
        return print_algorithm_parameters_report_v(settings)

    return print_algorithm_parameters_report_t(settings)


def print_algorithm_parameters_report_w(settings: ConfigDict) -> None:
    # Extract values
    algorithm_config = settings.section("algorithm")

    name = algorithm_config.as_str("name")
    delta_t = algorithm_config.as_int("delta_t")
    radius_min = algorithm_config.as_float("radius_min")
    radius_step = algorithm_config.as_float("radius_step")
    central_mask = algorithm_config.as_float("central_mask", 0.0)
    windows_size = algorithm_config.as_float("windows_size")
    invert_difference = algorithm_config.as_bool("invert_difference")

    radii_km = settings.get_astype("parameters.radii_km", list[float])

    # Print values
    print_bar()
    print("Algorithm Parameters")
    print_line()
    print(f"Name                      : {name}")
    print_line()
    print(f"Profile difference offset : {delta_t} hours")
    print(f"Invert profile difference : {invert_difference}")
    print_line()
    print(f"Minimum analysis radius   : {radius_min} km")
    print(f"Maximum analysis radius   : {radii_km[-1]} km")
    print(f"Analysis radius increment : {radius_step} km")
    print_line()
    print(f"Central mask extent       : {central_mask}%")
    print(f"Analysis window extent    : {windows_size}%")
    print_bar()


def print_algorithm_parameters_report_v(settings: ConfigDict) -> None:
    # Extract values
    algorithm_config = settings.section("algorithm")

    name = algorithm_config.as_str("name")
    delta_t = algorithm_config.as_int("delta_t")
    th_min = algorithm_config.as_int("bt_threshold_min")
    th_max = algorithm_config.as_int("bt_threshold_max")
    th_step = algorithm_config.as_int("bt_threshold_step")
    central_mask = algorithm_config.as_float("central_mask")
    windows_size = algorithm_config.as_float("windows_size")
    invert_difference = algorithm_config.as_bool("invert_difference")

    df_min = settings.as_float("parameters.dmin")
    df_max = settings.as_float("parameters.dmax")

    # Print values
    print_bar()
    print("Algorithm Parameters")
    print_line()
    print(f"Name                      : {name}")
    print_line()
    print(f"Profile difference offset : {delta_t} hours")
    print(f"Invert profile difference : {invert_difference}")

    if not isnan(df_min):
        print_line()
        print(f"Minimum difference        : {df_min}-Kelvin")
        print(f"Maximum difference        : {df_max}-Kelvin")

    print_line()
    print(f"Minimum threshold         : {th_min}-Kelvin")
    print(f"Maximum threshold         : {th_max}-Kelvin")
    print(f"Threshold increment       : {th_step}-Kelvin")
    print_line()
    print(f"Central mask extent       : {central_mask}%")
    print(f"Analysis window extent    : {windows_size}%")
    print_bar()


def print_algorithm_parameters_report_t(settings: ConfigDict) -> None:
    # Extract values
    algorithm_config = settings.section("algorithm")

    name = algorithm_config.as_str("name")
    delta_t = algorithm_config.as_int("delta_t")
    th_min = algorithm_config.as_int("bt_threshold_min")
    th_max = algorithm_config.as_int("bt_threshold_max")
    th_step = algorithm_config.as_int("bt_threshold_step")
    invert_difference = algorithm_config.as_bool("invert_difference")

    # Print values
    print_bar()
    print("Algorithm Parameters")
    print_line()
    print(f"Name                      : {name}")
    print_line()
    print(f"Profile difference offset : {delta_t} hours")
    print(f"Invert profile difference : {invert_difference}")
    print_line()
    print(f"Minimum threshold         : {th_min}-Kelvin")
    print(f"Maximum threshold         : {th_max}-Kelvin")
    print(f"Threshold increment       : {th_step}-Kelvin")
    print_bar()


def print_spectral_analysis_parameters_report(settings: ConfigDict) -> None:
    # Extract values
    spectral_config = settings.section("spectral")

    fft_size = spectral_config.as_int("fft_size")
    window_function = spectral_config.as_str("window")
    sampling_rate = settings.as_int("subsampling.sampling_rate")

    nperseg_ = spectral_config["nperseg"]

    if isinstance(nperseg_, int):
        nperseg = nperseg_
    elif isinstance(nperseg_, float):
        series_length = settings.as_int("parameters.series_length")
        nperseg = floor(nperseg_ * series_length)
    else:
        nperseg = 0

    noverlap_ = spectral_config["noverlap"]

    if isinstance(noverlap_, int):
        noverlap = noverlap_
    elif isinstance(noverlap_, float):
        noverlap = floor(noverlap_ * nperseg)
    else:
        noverlap = 0

    # Print values
    print_bar()
    print("Spectral Analysis Parameters")
    print_line()

    print_row("FFT analysis block size", fft_size, sv="samples", vf=">4d")
    print_row("FFT sampling rate", sampling_rate, sv="samples/day", vf=">4d")
    print_row("FFT window function", window_function)

    if nperseg > 0:
        print_line()
        print_row("Samples per segment (Welch)", nperseg, sv="samples")
        print_row("Overlaping elements (Welch)", noverlap, sv="samples")

    print_bar()


def print_filtering_parameters_report(settings: ConfigDict) -> None:
    # Extract values
    filter_config = settings.section("filter")
    filter_frequency = filter_config.as_float("frequency")
    filter_bandwidth = filter_config.as_float("bandwidth")
    filter_order = filter_config.as_int("order")

    parameters = settings.section("parameters")
    filter_lowcut = 24 * parameters.as_float("frequency_lowcut")
    filter_highcut = 24 * parameters.as_float("frequency_highcut")

    # Print values
    print_bar()
    print("Filter Parameters")
    print_line()

    print_row(
        "Central frequency", filter_frequency, sv="cycles/day", vf=">5.3f"
    )
    print_row("Band width", filter_bandwidth, sv="cycles/day", vf=">5.3f")
    print_row("Low cut frequency", filter_lowcut, sv="cycles/day", vf=">5.3f")
    print_row(
        "High cut frequency", filter_highcut, sv="cycles/day", vf=">5.3f"
    )
    print_row("Order", filter_order, sv="th", ss="-")

    print_bar()
