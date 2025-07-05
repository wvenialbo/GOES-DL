from math import floor
from pathlib import Path
from typing import Any, TypeGuard, cast

from numpy import float64, floating, zeros
from numpy.typing import NDArray

from .config import ConfigDict
from .report_tools import (
    print_bar,
    print_spectral_analysis_parameters_report,
)
from .utilities import (
    get_filename_prefix,
)

_Array = NDArray[floating[Any]]
_Series = list[_Array]

_Spectrum = Any
_Spectra = list[_Spectrum]

_ALGORITHM_DELTA_T = "algorithm.delta_t"
_INVERT_DIFFERENCE = "algorithm.invert_difference"
_ANALYSIS_PREFFIX = "analysis"

# ---------- Spectrum analysis utilities ----------


def analyze_spectra(
    detrended_timeseries: _Series,
    mean_timeseries: dict[str, _Array],
    settings: ConfigDict,
) -> tuple[_Spectra, dict[str, _Spectrum]]:
    from goesdl.experimental.fourier import FourierAnalysis
    from goesdl.fileio import load_metadata, save_metadata

    print_spectral_analysis_parameters_report(settings)

    algorithm_id = settings.as_str("algorithm_id")

    # Retrieve or build the time series
    timeseries_filename = _get_analysis_filename(algorithm_id, settings)

    analysers_data: tuple[_Spectra, dict[str, _Spectrum]]

    if timeseries_filename.exists():
        # Just retrieve the precomputed time series
        print("Retrieving analysis data...")

        analysers_data = load_metadata(timeseries_filename)

        print("Analysis data retrieved!")

    else:
        # Compute parameters with values derived from data and other
        # parameters
        print("Analysing timeseries spectra...")

        analysers_data = _do_analyze_spectra(
            detrended_timeseries, mean_timeseries, settings
        )

        save_metadata(timeseries_filename, analysers_data)

        print("Spectra analysis finished!")

    print_bar()

    analysers: list[FourierAnalysis]
    analysers, _ = analysers_data

    fft_size = settings.as_int("spectral.fft_size")
    actual_fft_size = analysers[0].fft_size

    required_fft_size = f"{fft_size:>4d}" if fft_size else "(automatic)"
    effective_fft_size = (
        f"{actual_fft_size:>4d}" if actual_fft_size else "(unknown)"
    )

    print(f"Requested FFT spectrum size    : {required_fft_size} samples")
    print(f"Effective FFT spectrum size    : {effective_fft_size} samples")

    print_bar()

    return analysers_data


def _do_analyze_spectra(
    detrended_timeseries: _Series,
    mean_timeseries: dict[str, _Array],
    settings: ConfigDict,
) -> tuple[_Spectra, dict[str, _Spectrum]]:
    from goesdl.experimental.fourier import FourierAnalysis

    analysers: _Spectra = []
    mean_analysers: dict[str, _Spectrum] = {}

    sampling_rate = settings.as_int("subsampling.sampling_rate")
    series_length = settings.as_int("parameters.series_length")
    fft_size = settings.as_int("spectral.fft_size")
    window_function = settings.as_str("spectral.window")

    nperseg, noverlap = _get_welch_params(settings)

    noise = settings.as_str("evaluation.noise_model")

    # Perform Fourier Analysis
    for time_series in detrended_timeseries:
        analyser = FourierAnalysis(
            sampling_rate=sampling_rate / 24,
            signal_size=series_length,
            fft_size=fft_size,
            window=window_function,
            dewindow_threshold=0.1,
        )

        analyser.apply(time_series, nperseg, noverlap, noise)

        analysers.append(analyser)

    for key, time_series in mean_timeseries.items():
        analyser = FourierAnalysis(
            sampling_rate=sampling_rate / 24,
            signal_size=series_length,
            fft_size=fft_size,
            window=window_function,
            dewindow_threshold=0.1,
        )

        analyser.apply(time_series, nperseg, noverlap, noise)

        mean_analysers[key] = analyser

    return analysers, mean_analysers


def _get_welch_params(settings: ConfigDict) -> tuple[int | None, int | None]:
    def valid_nproportion(x: Any) -> TypeGuard[float]:
        return isinstance(x, float) and 0 < x <= 1.0

    def valid_block(x: Any) -> TypeGuard[int]:
        if not isinstance(x, int):
            return False
        block_size = floor(x * sampling_rate)
        return 0 < block_size <= series_length

    def valid_oproportion(x: Any) -> TypeGuard[float]:
        return isinstance(x, float) and 0 <= x <= 0.75

    def valid_overlap(x: Any) -> TypeGuard[int]:
        if not isinstance(x, int) or not isinstance(nperseg, int):
            return False
        return 0 <= x < nperseg

    sampling_rate = settings.as_int("subsampling.sampling_rate")
    series_length = settings.as_int("parameters.series_length")

    nperseg = settings["spectral.nperseg"]
    noverlap = settings["spectral.noverlap"]

    if nperseg is None:
        nperseg = None
    elif valid_nproportion(nperseg):
        nperseg = floor(nperseg * series_length)
    elif valid_block(nperseg):
        nperseg = min(floor(nperseg * sampling_rate), series_length)
    else:
        raise ValueError("Invalid `nperseg` value")

    if noverlap is None:
        noverlap = None
    elif valid_oproportion(noverlap) and isinstance(nperseg, int):
        noverlap = floor(noverlap * nperseg)
    elif not valid_overlap(noverlap):
        raise ValueError("Invalid `noverlap` value")

    return nperseg, noverlap


def _find_diurnal_cycle(input_analyser: Any) -> _Array:
    from goesdl.experimental.fourier import FourierAnalysis

    analyser = cast(FourierAnalysis, input_analyser)

    if not (diurnal := analyser.find_frequency(1.0 / 24)):
        return zeros((analyser.signal_size,), dtype=float64)

    diurnal_index = diurnal[0]

    time_series = analyser.reconstruct_components(diurnal_index)

    return cast(_Array, time_series)


def find_diurnal_cycle(
    analysers: _Spectra, input_mean_analysers: dict[str, _Spectrum]
) -> tuple[_Series, dict[str, _Array]]:
    diurnal_cycles: _Series = []

    for analyser in analysers:
        diurnal_cycle = _find_diurnal_cycle(analyser)
        diurnal_cycles.append(diurnal_cycle)

    mean_diurnal_cycles: dict[str, _Array] = {}

    for key, analyser in input_mean_analysers.items():
        diurnal_cycle = _find_diurnal_cycle(analyser)
        mean_diurnal_cycles[key] = diurnal_cycle

    return diurnal_cycles, mean_diurnal_cycles


def get_dominant_cycle(
    input_analysers: _Spectra, input_mean_analysers: dict[str, _Spectrum]
) -> tuple[_Series, dict[str, _Array]]:
    from goesdl.experimental.fourier import FourierAnalysis

    analysers = cast(list[FourierAnalysis], input_analysers)
    mean_analysers = cast(dict[str, FourierAnalysis], input_mean_analysers)

    dominant_cycles: _Series = []

    for analyser in analysers:
        dominant_cycle = analyser.reconstruct_components(indices=0)
        dominant_cycles.append(cast(_Array, dominant_cycle))

    mean_dominant_cycles: dict[str, _Array] = {}

    for key, analyser in mean_analysers.items():
        dominant_cycle = analyser.reconstruct_components(indices=0)
        mean_dominant_cycles[key] = cast(_Array, dominant_cycle)

    return dominant_cycles, mean_dominant_cycles


def _get_analysis_filename(algorithm_id: str, settings: ConfigDict) -> Path:
    if algorithm_id == "algorithm_0":
        return _get_analysis_filename_0(settings)

    if algorithm_id == "algorithm_1":
        return _get_analysis_filename_1(settings)

    return _get_analysis_filename_2(settings)


def _get_analysis_filename_0(settings: ConfigDict) -> Path:
    filename_prefix = get_filename_prefix(_ANALYSIS_PREFFIX, settings)

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


def _get_analysis_filename_1(settings: ConfigDict) -> Path:
    filename_prefix = get_filename_prefix(_ANALYSIS_PREFFIX, settings)

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


def _get_analysis_filename_2(settings: ConfigDict) -> Path:
    filename_prefix = get_filename_prefix(_ANALYSIS_PREFFIX, settings)

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
