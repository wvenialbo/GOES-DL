import warnings
from collections.abc import Sequence
from typing import cast

from numpy import (
    abs,
    array,
    complex128,
    float64,
    isnan,
    linspace,
    nan_to_num,
    nanmax,
    nanmean,
    nonzero,
)
from scipy.signal import butter, detrend, filtfilt

from ..utils.array import (
    ArrayComplex,
    ArrayFloat,
    ArrayInt,
    CoComplex,
    CoFloat,
    SequenceComplex,
    SequenceFloat,
    ToFloat,
    ToInt,
)
from .helper import validate_1d_signal


class Sequencer:

    sampling_rate: float

    def __init__(self, sampling_rate: float) -> None:
        """
        Initialize the Sequencer object.

        Parameters
        ----------
        sampling_rate : float
            The sampling rate of the signal, in cycles (observations)
            per hour.
        """
        if sampling_rate <= 0:
            raise ValueError(
                "`sampling_rate` must be a positive number, "
                f"got {sampling_rate}"
            )

        self.sampling_rate = sampling_rate

    @staticmethod
    def average(signals: Sequence[SequenceFloat]) -> ArrayFloat:
        dtype: type[CoFloat] = getattr(signals[0], "dtype", float64)
        data_matrix = array(signals, dtype=dtype)
        with warnings.catch_warnings():
            # Ignore all NaN column warning
            warnings.simplefilter("ignore", category=RuntimeWarning)
            return array(nanmean(data_matrix, axis=0), dtype=dtype)

    @staticmethod
    def average_complex(signals: Sequence[SequenceComplex]) -> ArrayComplex:
        dtype: type[CoComplex] = getattr(signals[0], "dtype", complex128)
        data_matrix: ArrayComplex = array(signals, dtype=dtype)
        with warnings.catch_warnings():
            # Ignore all NaN column warning
            warnings.simplefilter("ignore", category=RuntimeWarning)
            mean_data = nanmean(data_matrix, axis=0, dtype=dtype)
            return cast(ArrayComplex, mean_data)

    def bandpass_filter(
        self,
        signal: ArrayFloat,
        lowcut_freq: ToFloat,
        highcut_freq: ToFloat,
        sample_rate: ToFloat | None = None,
        order: ToInt = 4,
    ) -> ArrayFloat:
        if sample_rate is None:
            sample_rate = self.sampling_rate

        nyquist = 0.5 * sample_rate
        low = lowcut_freq / nyquist
        high = highcut_freq / nyquist

        if low >= high:
            raise ValueError(
                "The lower cutoff frequency must be lower than the upper cutoff frequency"
            )
        if low <= 0 or high >= 1:
            raise ValueError(
                "Cutoff frequencies must be between 0 and the Nyquist frequency (excluding limits)"
            )

        b, a = butter(order, [low, high], btype="band")

        return filtfilt(b, a, nan_to_num(signal, nan=0.0))

    def build_frequencies(
        self, min_freq: float, max_freq: float | None = None, size: int = 1024
    ) -> ArrayFloat:
        if max_freq is None:
            max_freq = self.sampling_rate / 2

        return linspace(min_freq, max_freq, size)

    def build_times(self, signal_lenght: ToInt) -> ArrayFloat:
        duration_hours = signal_lenght / self.sampling_rate
        return linspace(0, duration_hours, signal_lenght, endpoint=False)

    @classmethod
    def detrend(cls, signal: SequenceFloat) -> ArrayFloat:
        """
        Fully detrend the input signal.

        Parameters
        ----------
        signal : ArrayFloat
            The input signal to be detrended.
        mode

        Returns
        -------
        ArrayFloat
            The detrended signal.
        """
        signal = validate_1d_signal(signal)
        valid_indices = cls.valid_indices(signal)

        detrended_signal = signal.copy()
        detrended_signal[valid_indices] = detrend(
            signal[valid_indices], type="linear"
        )

        # > detrended_signal[valid_indices] = detrend(
        # >     detrended_signal[valid_indices], type="constant"
        # > )

        return detrended_signal - nanmean(detrended_signal)

    def gap_indices(self, signal: SequenceFloat) -> ArrayInt:
        signal = validate_1d_signal(signal)
        return nonzero(isnan(signal))[0]

    @staticmethod
    def normalize(signal: SequenceFloat) -> ArrayFloat:
        signal = validate_1d_signal(signal)
        norm = nanmax(abs(signal))
        return signal if norm == 0 else signal / norm

    @staticmethod
    def trim(signal: SequenceFloat) -> tuple[ArrayFloat, int, int]:
        signal = validate_1d_signal(signal)
        not_nan_indices = nonzero(~isnan(signal))[0]

        begin = not_nan_indices[0]
        end = not_nan_indices[-1] + 1

        offset_right = len(signal) - end

        return signal[begin:end], begin, offset_right

    @staticmethod
    def valid_indices(signal: SequenceFloat) -> ArrayInt:
        signal = validate_1d_signal(signal)
        return nonzero(~isnan(signal))[0]
