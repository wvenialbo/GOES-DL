from typing import Any, cast

from numpy import floating, integer
from numpy.typing import NDArray

from .config import ConfigDict
from .report_tools import print_bar, print_filtering_parameters_report
from .utilities import fill_inner_missing_values

_Array = NDArray[floating[Any]]
_Series = list[_Array]

_Settings = dict[str, Any]


# ---------- Time series handling utilities ----------


def subsample_timeseries(
    input_series: _Series, settings: ConfigDict
) -> _Series:
    print_bar()

    subsampling = settings.section("subsampling")
    sampling_offset = subsampling.as_int("sampling_offset")

    if sampling_offset < 0:
        raise ValueError(
            "'subsampling.sampling_offset' must be a non-negative integer, "
            f"got {sampling_offset}"
        )

    output_series: _Series

    parameters = settings.section("parameters")
    sampling_interval = parameters.as_int("sampling_interval")

    if sampling_interval == 1:
        output_series = _extract_timeseries(input_series, sampling_offset)

    else:
        output_series = _subsample_timeseries(
            input_series, settings, sampling_interval, sampling_offset
        )

    parameters["sampling_offset"] = sampling_offset

    print("Subsampling finished!")
    print_bar()

    sequence_length = parameters.as_int("sequence_length")
    sampling_rate = subsampling.as_int("sampling_rate")
    series_length = parameters.as_int("series_length")

    print(f"Sequence length    : {sequence_length:>4d} samples")
    print(f"Sampling rate      : {sampling_rate:>4d} samples/d")
    print(f"Sampling offset    : {sampling_offset:>4d} samples")
    print(f"Sampling interval  : {sampling_interval:>4d} samples")
    print(f"Time series lenght : {series_length:>4d} samples")

    print_bar()

    return output_series


def _extract_timeseries(
    input_series: _Series, sampling_offset: int
) -> _Series:
    if sampling_offset == 0:
        print("No subsampling required, copying data...")
        return [time_series.copy() for time_series in input_series]

    print("No subsampling required, truncating data...")
    return [time_series[sampling_offset:] for time_series in input_series]


def _subsample_timeseries(
    input_series: _Series,
    settings: ConfigDict,
    sampling_interval: int,
    sampling_offset: int,
) -> _Series:
    print("Subsampling timeseries...")

    series_length = settings.as_int("parameters.series_length")

    step = sampling_interval
    begin = sampling_offset
    end = series_length + step

    return [time_series[begin:end:step] for time_series in input_series]


def trim_timeseries(
    input_series: list[list[float]], settings: ConfigDict
) -> _Series:
    from goesdl.experimental.sequence import Sequencer

    print_bar()
    print("Trimming timeseries...")

    parameters = settings.section("parameters")

    trimming_offset = None
    series_length = parameters.as_int("series_length")
    output_series: _Series = []

    for time_series in input_series:
        trimmed_time_series, start, _ = Sequencer.trim(time_series)
        if trimming_offset is None:
            trimming_offset = start
            series_length = len(trimmed_time_series)
        output_series.append(cast(_Array, trimmed_time_series))

    print("Trimming finished!")

    if trimming_offset is None:
        trimming_offset = 0

    # Update affected parameters
    if trimming_offset:
        _update_parameters_for_trimmed_timeseries(
            parameters, trimming_offset, series_length
        )
    else:
        print("No changes in timeseries")

    print_bar()

    return output_series


def _update_parameters_for_trimmed_timeseries(
    parameters: ConfigDict, trimming_offset: int, series_length: int
) -> None:
    sampling_offset = parameters.as_int("sampling_offset")
    sampling_interval = parameters.as_int("sampling_interval")

    sampling_offset += trimming_offset * sampling_interval

    parameters["sampling_offset"] = sampling_offset
    parameters["series_length"] = series_length

    sequence_length = parameters.as_int("sequence_length")

    print_bar()
    print(f"Sequence length    : {sequence_length:>4d} samples")
    print(f"Sampling offset    : {sampling_offset:>4d} samples")
    print(f"Time series lenght : {series_length:>4d} samples")


def fill_timeseries(
    input_series: _Series, settings: ConfigDict
) -> tuple[_Series, NDArray[integer[Any]]]:
    from goesdl.experimental.sequence import Sequencer

    print_bar()
    print("Imputing timeseries...")

    # Get the indices of the original gaps
    gap_indices = Sequencer.gap_indices(input_series[0])

    output_series: _Series = []

    # Fill missing data using sparse cubic spline interpolation
    for time_series in input_series:
        filled_time_series = time_series.copy()
        fill_inner_missing_values(filled_time_series)
        output_series.append(filled_time_series)

    print("Imputing finished!")

    if gap_indices.size:
        print_bar()
        print(f"Imputed values : {gap_indices.size:>4d} data points")
    else:
        print("No change in series content")

    print_bar()

    return output_series, gap_indices


def detrend_timeseries(input_series: _Series) -> tuple[_Series, _Series]:
    from goesdl.experimental.sequence import Sequencer

    print_bar()
    print("Detrending timeseries...")

    output_series: _Series = []
    output_tendencies: _Series = []

    for time_series in input_series:
        detrended_time_series = Sequencer.detrend(time_series)
        output_series.append(cast(_Array, detrended_time_series))

        tendency_component = time_series - detrended_time_series
        output_tendencies.append(tendency_component)

    print("Detrending finished!")
    print_bar()

    return output_series, output_tendencies


def calculate_mean_timeseries(
    original_time_series: _Series,
    detrended_time_series: _Series,
    settings: ConfigDict,
) -> dict[str, _Array]:
    from goesdl.experimental.align import SignalAligner
    from goesdl.experimental.sequence import Sequencer

    print_bar()
    print("Computing mean timeseries...")

    # Calculate the incoherent mean time series
    incoherent_mean_timeseries = Sequencer.average(original_time_series)

    # Calculate the detrended incoherent mean time series
    detrended_mean_timeseries = Sequencer.detrend(incoherent_mean_timeseries)

    # Calculate the coherent mean time series
    algorithm_id = settings.as_str("algorithm_id")
    reference_key = f"event.reference_frame.{algorithm_id}"
    reference_frame = settings.as_int(reference_key, 0)

    filter_order: int = settings.as_int("filter.order")

    filter_params = None

    if filter_order != 0:
        filter_lowcut = settings.as_float("parameters.frequency_lowcut")
        filter_highcut = settings.as_float("parameters.frequency_highcut")

        filter_params = (filter_lowcut, filter_highcut, filter_order)

    sampling_rate = settings.as_int("subsampling.sampling_rate")
    aligner = SignalAligner(sampling_rate / 24, filter_params)

    aligner.align(detrended_time_series, reference_frame)

    coherent_mean_timeseries = aligner.signal

    mean_timeseries: _Settings = {
        "incoherent_mean_timeseries": incoherent_mean_timeseries,
        "detrended_mean_timeseries": detrended_mean_timeseries,
        "coherent_mean_timeseries": coherent_mean_timeseries,
    }

    print("Mean timeseries computed successfully!")
    print_bar()

    return mean_timeseries


def filter_timeseries(
    detrended_timeseries: _Series,
    mean_timeseries: dict[str, _Array],
    settings: ConfigDict,
) -> tuple[_Series, dict[str, _Array]]:
    from goesdl.experimental.sequence import Sequencer

    print_filtering_parameters_report(settings)

    mean_series: dict[str, _Array] = {}

    filter_frequency = settings.as_float("filter.frequency")

    if filter_frequency == 0:
        print("No filtering required!")
        print_bar()
        return detrended_timeseries.copy(), mean_timeseries.copy()

    print("Filtering timeseries...")

    sampling_rate = settings.as_int("subsampling.sampling_rate")

    sequencer = Sequencer(sampling_rate / 24)

    filter_order = settings.as_int("filter.order")
    filter_lowcut = settings.as_float("parameters.frequency_lowcut")
    filter_highcut = settings.as_float("parameters.frequency_highcut")

    output_series: _Series = []

    for time_series in detrended_timeseries:
        filtered_time_series = sequencer.bandpass_filter(
            time_series, filter_lowcut, filter_highcut, order=filter_order
        )
        output_series.append(cast(_Array, filtered_time_series))

    for key, time_series in mean_timeseries.items():
        filtered_time_series = sequencer.bandpass_filter(
            time_series, filter_lowcut, filter_highcut, order=filter_order
        )
        mean_series[key] = cast(_Array, filtered_time_series)

    print("Filtering finished!")
    print_bar()

    return output_series, mean_series
