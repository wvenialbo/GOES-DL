import warnings
from math import sqrt
from typing import Any, Literal, cast

from numpy import abs as npabs
from numpy import (
    any,
    argsort,
    array,
    asarray,
    clip,
    complex128,
    corrcoef,
    cos,
    diff,
    empty,
    float64,
    floor,
    full_like,
    int64,
    isnan,
    linspace,
)
from numpy import max as npmax
from numpy import (
    nan_to_num,
    nanargmin,
    nanmean,
    nanmedian,
    nonzero,
    pi,
    split,
)
from numpy import sum as npsum
from numpy import (
    var,
    zeros,
    zeros_like,
)
from scipy.fft import irfft, rfft, rfftfreq
from scipy.interpolate import interp1d
from scipy.linalg import LinAlgError
from scipy.signal import butter, detrend, filtfilt, periodogram, welch
from scipy.signal.windows import bartlett, blackman, boxcar, hamming, hann
from scipy.stats import chi2
from statsmodels.tsa.arima.model import ARIMA, ARIMAResults  # type: ignore

from ..utils.array import ArrayComplex128, ArrayFloat64, ArrayInt64

# > from scipy.signal.windows import bartlett, blackman, hamming, hanning

SUPPORTED_FILL_METHODS = {"mean", "median"}

SUPPORTED_WINDOW_FUNCTIONS = {
    "bartlett",
    "blackman",
    "boxcar",
    "hamming",
    "hann",
}

INVALID_SAMPLING_RATE = "Sampling rate must be positive number"

DeoffsetType = tuple[list[ArrayFloat64], list[int], list[float], int]
DeoffsetMode = Literal["minimize_shift", "maximize_correlation"]


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
            raise ValueError(INVALID_SAMPLING_RATE)

        self.sampling_rate = sampling_rate

    @staticmethod
    def average(signals: list[ArrayFloat64]) -> ArrayFloat64:
        data_matrix = array(signals, dtype=float64)
        with warnings.catch_warnings():
            # Ignore all NaN column warning
            warnings.simplefilter("ignore", category=RuntimeWarning)
            return array(nanmean(data_matrix, axis=0), dtype=float64)

    @staticmethod
    def average_complex(signals: list[ArrayComplex128]) -> ArrayComplex128:
        data_matrix = array(signals, dtype=complex128)
        with warnings.catch_warnings():
            # Ignore all NaN column warning
            warnings.simplefilter("ignore", category=RuntimeWarning)
            return array(nanmean(data_matrix, axis=0), dtype=complex128)

    def bandpass_filter(
        self,
        signal: ArrayFloat64,
        lowcut_freq: float,
        highcut_freq: float,
        sample_rate: float | None = None,
        order: int = 4,
    ) -> ArrayFloat64:
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

        filtered_signal = filtfilt(b, a, nan_to_num(signal, nan=0.0))

        return cast(ArrayFloat64, filtered_signal)

    def build_frequencies(
        self, min_freq: float, max_freq: float | None = None, size: int = 1024
    ) -> ArrayFloat64:
        if max_freq is None:
            max_freq = self.sampling_rate / 2

        frequencies = linspace(min_freq, max_freq, size)
        return cast(ArrayFloat64, frequencies)

    def build_times(self, signal_lenght: int) -> ArrayFloat64:
        duration_hours = signal_lenght / self.sampling_rate
        times = linspace(0, duration_hours, signal_lenght, endpoint=False)
        return cast(ArrayFloat64, times)

    @classmethod
    def detrend(cls, signal: ArrayFloat64) -> ArrayFloat64:
        """
        Fully detrend the input signal.

        Parameters
        ----------
        signal : ArrayFloat64
            The input signal to be detrended.
        mode

        Returns
        -------
        ArrayFloat64
            The detrended signal.
        """
        signal = _validate_1d_signal(signal)
        valid_indices = cls.valid_indices(signal)

        detrended_signal = signal.copy()
        detrended_signal[valid_indices] = detrend(
            signal[valid_indices], type="linear"
        )
        # > detrended_signal[valid_indices] = detrend(
        # >     detrended_signal[valid_indices], type="constant"
        # > )
        detrended_signal = detrended_signal - nanmean(detrended_signal)

        return detrended_signal

    def gap_indices(self, signal: ArrayFloat64) -> ArrayInt64:
        nan_indices = nonzero(isnan(signal))[0]
        return cast(ArrayInt64, nan_indices)

    @staticmethod
    def normalize(signal: ArrayFloat64) -> ArrayFloat64:
        norm = npmax(npabs(signal))
        return signal if norm == 0 else signal / norm

    @staticmethod
    def trim(signal: ArrayFloat64) -> tuple[ArrayFloat64, int, int]:
        not_nan_indices = nonzero(~isnan(signal))[0]

        begin = not_nan_indices[0]
        end = not_nan_indices[-1] + 1

        offset_right = len(signal) - end

        return signal[begin:end], begin, offset_right

    @staticmethod
    def valid_indices(signal: ArrayFloat64) -> ArrayInt64:
        valid_indices = nonzero(~isnan(signal))[0]
        return cast(ArrayInt64, valid_indices)


class FourierAnalysis:
    """
    Fourier Analysis class for time series data.

    This class performs Fourier analysis on time series data, allowing
    for the computation of the Fourier Transform, power spectrum,
    frequencies, and dominant frequencies. It also provides methods for
    filling missing data and applying window functions to reduce
    spectral leakage.
    """

    dewindow_threshold: float
    fft: ArrayComplex128
    fft_size: int
    frequencies: ArrayFloat64
    rank: ArrayInt64
    sampling_rate: float
    signal_size: int
    window: str

    density_spectrum: ArrayFloat64

    peak_boundaries: ArrayInt64
    peak_indices: ArrayInt64
    peak_values: ArrayFloat64

    def __init__(
        self,
        sampling_rate: float,
        signal_size: int,
        fft_size: int | None = None,
        window: str = "hann",
        dewindow_threshold: float = 0.1,
    ) -> None:
        """
        Initialize the FourierAnalysis object.

        Parameters
        ----------
        sampling_rate : float
            The sampling rate of the signal, in cycles (observations)
            per hour.
        signal_size : int
            The number of data point in the time series.
        fft_size : int, optional
            The size of the FFT. The default is None, which means the
            function will use `signal_size`.
        window : str, optional
            The window function to apply to the signal. Supported
            methods are: 'hann' (default), 'hamming', 'blackman',
            'bartlett', and 'none' or 'boxcar'. If 'none' is selected,
            the function will not apply any windowing to the signal.
        """
        if sampling_rate <= 0:
            raise ValueError(INVALID_SAMPLING_RATE)

        if signal_size <= 0:
            raise ValueError("`signal_size` must be a positive integer")

        if fft_size is None:
            fft_size = signal_size

        if fft_size < signal_size:
            raise ValueError(
                f"`fft_size` must be greater than or equal to {signal_size}"
            )

        if window not in SUPPORTED_WINDOW_FUNCTIONS:
            supported = "', '".join(SUPPORTED_WINDOW_FUNCTIONS)
            raise ValueError(
                f"Unsupported window function: '{window}', "
                f"supported methods are: '{supported}'"
            )

        nyquist_size = fft_size // 2 + 1

        self.fft = zeros(nyquist_size, dtype=complex128)
        self.dewindow_threshold = dewindow_threshold
        self.fft_size = fft_size
        self.frequencies = zeros(nyquist_size, dtype=float64)
        self.rank = zeros(nyquist_size, dtype=int64)
        self.sampling_rate = sampling_rate
        self.signal_size = signal_size
        self.window = window

        self.peak_boundaries = empty((0, 2), dtype=int64)
        self.peak_indices = empty(0, dtype=int64)
        self.peak_values = empty((0, 2), dtype=float64)

    def apply(
        self,
        signal: ArrayFloat64,
        nperseg: int | None = None,
        noverlap: int | None = None,
    ) -> None:
        """
        Perform Fourier Analysis on the input signal.

        This method computes the Fourier Transform of the input signal
        and calculates the power spectrum, frequencies, and dominant
        frequencies. The input signal is expected to be a 1D array.

        The method also applies a window function to reduce spectral
        leakage and handles missing data by filling NaN values using the
        specified fill method.

        The FFT size can be specified, or it will be automatically
        determined based on the input signal size. The default FFT size
        is 0, which means the function will use the next power of 2 for
        the FFT size.

        The method raises a ValueError if the input signal is not a 1D
        array, if the signal size is 0, or if the sampling rate is not
        positive. It also raises a ValueError if the fill method is not
        supported or if the window function is not supported.

        The method raises a ValueError if the input signal contains NaN
        values and the fill method is set to 'none'. If the fill method
        is set to 'mean' or 'median', the method fills the NaN values
        with the mean or median of the signal, respectively. If the fill
        method is set to 'interpolate', the method uses cubic spline
        interpolation to fill the NaN values.

        Parameters
        ----------
        signal : ArrayFloat64
            The input signal as a 1D array.
        """
        signal = self._validate_signal(signal)

        window = self._get_window(self.window, self.signal_size)
        windowed_signal = signal * window

        frequencies, density_spectrum = welch(
            x=signal,
            fs=self.sampling_rate,
            window=cast(Any, self.window),
            nperseg=self.signal_size,  # periodogram
            noverlap=0,  # no-overlap
            nfft=self.fft_size,  # fft_size >= signal_size
            detrend=False,  # already detrended
            return_onesided=True,
            scaling="density",
        )

        frequencies_1, density_spectrum_1 = periodogram(
            x=signal,
            fs=self.sampling_rate,
            window=cast(Any, self.window),
            nfft=self.fft_size,  # fft_size >= signal_size
            detrend=False,  # already detrended
            return_onesided=True,
            scaling="density",
        )

        # Compute the normalised unilateral FFT of the signal
        self.fft = cast(ArrayComplex128, rfft(windowed_signal, self.fft_size))
        self.density_spectrum = cast(ArrayFloat64, density_spectrum)
        self.frequencies = frequencies

        self._perform_analysis(self.density_spectrum)

    def average(
        self, analyzers: list["FourierAnalysis"], ignore_phase: bool = True
    ) -> None:
        sequencer = Sequencer(self.sampling_rate)
        if ignore_phase:
            amplitudes = [npabs(analyzer.fft) for analyzer in analyzers]
            average_amplitude = sequencer.average(amplitudes)
            average_fft = average_amplitude.astype(complex128)

        else:
            ffts = [analyzer.fft for analyzer in analyzers]
            average_fft = sequencer.average_complex(ffts)
            average_amplitude = npabs(average_fft)

        sampling_interval = 1 / self.sampling_rate
        frequencies = rfftfreq(self.fft_size, d=sampling_interval)

        window = self._get_window(self.window, self.signal_size)
        window_energy = npsum(window**2)
        scale = 1 / window_energy / self.sampling_rate
        density_spectrum = average_amplitude**2 * scale
        start, end = 1, -1 if self.has_nyquist else None
        density_spectrum[start:end] *= 2.0

        self.fft = average_fft
        self.density_spectrum = density_spectrum
        self.frequencies = frequencies

        self._perform_analysis(self.density_spectrum)

    def find_frequency(
        self, frequencies: list[float] | float | int, tolerance: float = 0.1
    ) -> list[int]:
        if isinstance(frequencies, (float, int)):
            frequencies = [float(frequencies)]

        indices: list[int] = []

        for frequency in frequencies:
            absdiff = npabs(self.dominant_frequencies - frequency)
            nearest_index = nanargmin(absdiff)
            if absdiff[nearest_index] > tolerance * frequency:
                continue
            indices.append(round(nearest_index))

        return indices

    def reconstruct_components(self, indices: list[int] | int) -> ArrayFloat64:
        if isinstance(indices, int):
            indices = [indices]

        fft_filtered = zeros_like(self.fft, dtype=complex128)
        power_spectrum = npabs(self.fft) ** 2

        for index in indices:
            if index < 0 or index >= len(self.peak_indices):
                raise ValueError(
                    "`indices` must contain integer values "
                    f"between 0 and {len(self.peak_indices)-1}"
                )

            peak_index = self.peak_indices[index]
            left_idx, right_idx = self.peak_boundaries[index, :]

            total_power = npsum(power_spectrum[left_idx : right_idx + 1])
            original_amplitude = npabs(self.fft[peak_index])

            if original_amplitude > 1e-10:
                new_amplitude = sqrt(total_power)

                fft_filtered[peak_index] = self.fft[peak_index] * (
                    new_amplitude / original_amplitude
                )

        return self._reconstruct_fft_signal(fft_filtered)

    def reconstruct_signal(self, size: float = 1.0) -> ArrayFloat64:
        if size <= 0 or size > 1:
            raise ValueError("`size` must be in the interval (0, 1]")

        norder = round(size * len(self.rank))

        selected_indices = self.rank[:norder]

        fft_filtered = zeros_like(self.fft)

        fft_filtered[selected_indices] = self.fft[selected_indices]

        if self.has_nyquist and int(size) == 1:
            fft_filtered[-1] = self.fft[-1]

        windowed_signal = self._reconstruct_fft_signal(fft_filtered)

        return self._remove_window(windowed_signal)

    @staticmethod
    def _get_window(window_type: str, signal_size: int) -> ArrayFloat64:
        if window_type == "boxcar":
            window = boxcar(signal_size)

        elif window_type == "hann":
            window = hann(signal_size)

        elif window_type == "hamming":
            window = hamming(signal_size)

        elif window_type == "blackman":
            window = blackman(signal_size)

        elif window_type == "bartlett":
            window = bartlett(signal_size)

        else:
            raise ValueError("Invalid windowing function")

        return cast(ArrayFloat64, window)

    def _perform_analysis(self, spectrum: ArrayFloat64) -> None:
        # Subset for sorting should exclude DC and Nyquist, if present
        start, end = 1, -1 if self.has_nyquist else None
        spectrum_subset = spectrum[start:end]

        # Find the locations and amplitudes of the peaks in the power
        # spectrum, excluding the DC component (index 0) and Nyquist
        indices, boundaries, values = _find_peaks(spectrum_subset)

        # Sort the frequency bins by their corresponding powers
        # Adjust rank to account for the DC component
        self.rank = argsort(spectrum_subset)[::-1] + start

        # Adjust indices and boundaries to account for the DC component
        self.peak_indices = indices + start
        self.peak_boundaries = boundaries + start

        # Adjust locations to account for the DC component and convert
        # to frequencies
        self.peak_values = values
        frequency_resolution = self.sampling_rate / self.fft_size
        self.peak_values[:, 0] = (values[:, 0] + start) * frequency_resolution

    def _reconstruct_fft_signal(
        self, fft_filtered: ArrayComplex128
    ) -> ArrayFloat64:
        fft_filtered[0] = self.fft[0]

        windowed_signal = irfft(fft_filtered, n=self.fft_size)
        windowed_signal = windowed_signal[: self.signal_size]

        return windowed_signal.astype(float64, copy=False)

    def _remove_window(self, windowed_signal: ArrayFloat64) -> ArrayFloat64:
        window = self._get_window(self.window, self.signal_size)
        non_zero_mask = window > self.dewindow_threshold

        dewindowed_signal = zeros_like(window)
        dewindowed_signal[non_zero_mask] = (
            windowed_signal[non_zero_mask] / window[non_zero_mask]
        )

        return dewindowed_signal.astype(float64)

    def _validate_signal(self, signal: ArrayFloat64) -> ArrayFloat64:
        signal_data = _validate_1d_signal(signal)

        if len(signal) != self.signal_size:
            raise ValueError(
                f"Invalid signal size, expected {self.signal_size}, "
                f"got {len(signal)}"
            )

        if isnan(signal_data).any():
            raise ValueError("Input signal contains NaN values")

        return signal_data

    @property
    def dominant_densities(self) -> ArrayFloat64:
        return self.peak_values[:, 1]

    @property
    def dominant_frequencies(self) -> ArrayFloat64:
        """
        Get the dominant frequencies in the signal.

        Returns
        -------
        ArrayFloat64
            The dominant frequencies in the signal.
        """
        return self.peak_values[:, 0]

    @property
    def has_nyquist(self) -> bool:
        return self.fft_size % 2 == 0


class NaNFill:

    fill_method: str
    signal_data: ArrayFloat64

    def __init__(self, fill_method: str = "mean") -> None:
        """
        Initialize the NaNFill object.

        Parameters
        ----------
        fill_method : str, optional
            The method to fill missing data in the signal. Supported
            methods are: 'mean' (default), 'median', and 'none'. If
            'none' is selected, the function will raise an error if NaN
            values are present in the signal.
        """
        if fill_method not in SUPPORTED_FILL_METHODS:
            supported = "', '".join(SUPPORTED_FILL_METHODS)
            raise ValueError(
                f"Unsupported fill method: '{fill_method}', "
                f"supported methods are: '{supported}'"
            )

        self.fill_method = fill_method

        self.signal_data: ArrayFloat64 = empty(0, dtype=float64)

    def fill(self, signal: ArrayFloat64) -> ArrayFloat64:
        signal_data = self._validate_signal(signal)

        self.signal_data = signal_data

        signal_filled = signal_data.copy()

        missing_mask = isnan(signal_data)

        if self.fill_method == "mean":
            signal_filled[missing_mask] = nanmean(signal_data)

        elif self.fill_method == "median":
            signal_filled[missing_mask] = nanmedian(signal_data)

        else:
            raise ValueError("Invalid fill method")

        return signal_filled

    def _validate_signal(self, signal: ArrayFloat64) -> ArrayFloat64:
        return _validate_1d_signal(signal)


class NaNInterpolator:
    """
    A class to handle the interpolation of NaN values in time series data
    using sparse spline interpolation.
    """

    control_points: int
    half_interval: int
    sampling_rate: int
    sample_step: int
    signal_data: ArrayFloat64
    total_samples: int

    def __init__(self, sampling_rate: int, control_points: int) -> None:
        """
        Initializes the NaNInterpolator with interpolation parameters.

        Parameters
        ----------
        sampling_rate : int
            The sampling rate of the signal (samples per unit time).
        control_points : int
            The number of control points (samples per unit time).
        """
        self.sampling_rate = sampling_rate
        self.control_points = control_points
        self.sample_step = max(sampling_rate // control_points, 1)
        self.half_interval = control_points // 2

        self.signal_data: ArrayFloat64 = empty(0, dtype=float64)
        self.total_samples: int = 0

    def fill(self, signal: ArrayFloat64) -> ArrayFloat64:
        """
        Fills NaN values in a signal using sparse cubic spline
        interpolation.

        Parameters
        ----------
        signal :ArrayFloat64
            The input signal data which may contain NaN values.

        Returns:
            ArrayFloat64: The signal data with NaN values filled.
        """
        # Set signal_data and total_samples as instance variables for
        # use by helper methods
        signal_data = self._validate_signal(signal)

        self.signal_data = signal_data
        self.total_samples = len(signal_data)

        signal_filled = signal_data.copy()

        # Find indices of NaN values that need to be filled
        nan_indices_to_fill = nonzero(isnan(signal_data))[0]

        # Iterate through each NaN index and fill it
        for nan_idx in nan_indices_to_fill:
            # Find known points before the NaN index
            known_points_before = self._find_known_points(
                start_idx=int(nan_idx),
                step_direction=-self.sample_step,
                boundary=0,
            )

            # Find known points after the NaN index
            known_points_after = self._find_known_points(
                start_idx=int(nan_idx),
                step_direction=self.sample_step,
                boundary=self.total_samples,
            )

            # Combine and sort unique relevant indices
            relevant_indices = sorted(
                set(known_points_before + known_points_after)
            )

            # Handle interpolation or direct assignment based on
            # available known points
            self._apply_interpolation_or_fill(
                int(nan_idx), signal_filled, relevant_indices
            )

        return signal_filled

    def _apply_interpolation_or_fill(
        self,
        nan_idx: int,
        signal_filled: ArrayFloat64,
        relevant_indices: list[int],
    ):
        if len(relevant_indices) >= 2:
            # Perform cubic spline interpolation if at least two known
            # points are available Use indices directly as 'time' points
            # since data is equally spaced
            t_known = relevant_indices
            y_known = self.signal_data[
                relevant_indices
            ]  # Use instance's signal_data
            f_interp = interp1d(
                t_known, y_known, kind="cubic", fill_value="extrapolate"
            )
            signal_filled[nan_idx] = f_interp(nan_idx)
        elif len(relevant_indices) == 1:
            # If only one known point, use its value to fill the NaN
            signal_filled[nan_idx] = self.signal_data[
                relevant_indices[0]
            ]  # Use instance's signal_data
        else:
            # Raise an error if no known points are found
            raise ValueError(
                "Not enough known points to fill NaN values. "
                "Consider using a smaller sampling interval."
            )

    def _find_known_points(
        self, start_idx: int, step_direction: int, boundary: int
    ) -> list[int]:
        known_points: list[int] = []
        current_idx = start_idx + step_direction

        while (
            len(known_points) < self.half_interval
            and (step_direction >= 0 or current_idx >= boundary)
            and (step_direction <= 0 or current_idx < boundary)
        ) and 0 <= current_idx < self.total_samples:
            if not isnan(self.signal_data[current_idx]):
                known_points.append(current_idx)
            current_idx += step_direction

        return known_points

    def _validate_signal(self, signal: ArrayFloat64) -> ArrayFloat64:
        return _validate_1d_signal(signal)


def _find_peak_boundaries(
    spectrum: ArrayFloat64, indices: ArrayInt64
) -> ArrayInt64:
    valleys = _find_peak_indices(-spectrum)
    valley_indices = asarray(valleys, dtype=int64)

    boundaries: list[tuple[int, int]] = []

    for index in indices:
        left_valleys = valley_indices[valley_indices < index]
        left_boundary = int(left_valleys.max()) if len(left_valleys) > 0 else 0

        right_valleys = valley_indices[valley_indices > index]
        right_boundary = (
            int(right_valleys.min())
            if len(right_valleys) > 0
            else len(spectrum) - 1
        )

        boundaries.append((left_boundary, right_boundary))

    return asarray(boundaries, dtype=int64)


def _find_peak_indices(spectrum: ArrayFloat64) -> ArrayInt64:
    spec_copy = spectrum.copy()
    labels = full_like(spec_copy, fill_value=-1, dtype=int64)

    indices: list[int] = []
    current_label = 1

    while any(spec_copy > 0):
        max_val = spec_copy.max()

        max_indices = nonzero(spec_copy == max_val)[0]

        splits = nonzero(diff(max_indices) > 1)[0] + 1
        blocks = split(max_indices, splits)

        for block in blocks:
            start, end = block[0], block[-1]
            left_idx = start - 1
            right_idx = end + 1

            left_label = labels[left_idx] if left_idx >= 0 else -1
            right_label = labels[right_idx] if right_idx < len(labels) else -1

            if left_label < 0 and right_label < 0:
                label_to_assign = current_label
                peak_index = int(round(block.mean()))
                indices.append(peak_index)
                current_label += 1
            elif left_label >= 0:
                label_to_assign = left_label
            else:
                label_to_assign = right_label

            labels[block] = label_to_assign

            spec_copy[block] = 0.0

    return asarray(indices, dtype=int64)


def _find_peak_values(
    spectrum: ArrayFloat64, indices: ArrayInt64
) -> ArrayFloat64:
    values: list[tuple[float, float]] = []

    for index in indices:
        true_location, true_value = _parabolic_interpolation(spectrum, index)
        values.append((true_location, true_value))

    return asarray(values, dtype=float64)


def _find_peaks(
    spectrum: ArrayFloat64,
) -> tuple[ArrayInt64, ArrayInt64, ArrayFloat64]:
    indices = _find_peak_indices(spectrum)
    boundaries = _find_peak_boundaries(spectrum, indices)
    values = _find_peak_values(spectrum, indices)

    return indices, boundaries, values


def _parabolic_interpolation(
    power_spectrum: ArrayFloat64, peak_index: int
) -> tuple[float, float]:
    y_1: float = power_spectrum[peak_index]

    if peak_index in {0, len(power_spectrum) - 1}:
        return float(peak_index), y_1

    y_0: float = power_spectrum[peak_index - 1]
    y_2: float = power_spectrum[peak_index + 1]

    denominator = y_0 - 2 * y_1 + y_2

    if abs(denominator) < 1e-10:
        return float(peak_index), y_1

    numerator = 0.5 * (y_0 - y_2)

    delta = numerator / denominator

    x_vertex = peak_index + delta

    y_vertex = y_1 - 0.5 * numerator * delta

    return x_vertex, y_vertex


def _validate_1d_signal(signal: ArrayFloat64 | list[float]) -> ArrayFloat64:
    # Ensure the signal is a 1D array
    signal_data = asarray(signal, dtype=float64)

    # Validate the signal dimensions and size
    if signal_data.ndim != 1:
        raise ValueError("Input signal must be a 1D array.")

    if signal_data.size == 0:
        raise ValueError("Input signal is empty.")

    return signal_data


def _estimate_ar1_parameters(time_series: ArrayFloat64) -> tuple[float, float]:
    try:
        model = ARIMA(time_series, order=(1, 0, 0))
        results = cast(ARIMAResults, model.fit())  # type: ignore
        phi_ar1 = cast(float, results.params[1])  # type: ignore

        innovation_variance = cast(float, results.params[2])  # type: ignore

    except (ValueError, LinAlgError):
        if len(time_series) > 1:
            phi_ar1 = corrcoef(time_series[:-1], time_series[1:])[0, 1]
            phi_ar1 = clip(phi_ar1, -0.999, 0.999)
        else:
            phi_ar1 = 0.0

        innovation_variance = cast(float, var(time_series))

    return phi_ar1, innovation_variance


def _red_noise_spectrum(
    frequencies_cph: ArrayFloat64,
    phi_ar1: float,
    innovation_variance: float,
    sampling_rate_cph: float,
) -> ArrayFloat64:
    frequencies_hz = frequencies_cph / 3600.0
    fs_hz = sampling_rate_cph / 3600.0

    dt_sec = 1 / fs_hz
    f_norm = frequencies_hz * dt_sec

    denominator = 1 + phi_ar1**2 - 2 * phi_ar1 * cos(2 * pi * f_norm)
    denominator = clip(denominator, 1e-15, None)

    ar1_psd_hz = 2.0 * dt_sec * innovation_variance / denominator

    return ar1_psd_hz / 3600.0


def _red_noise_adjust_spectrum(
    frequencies_cph: ArrayFloat64,
    null_curve_psd_cph: ArrayFloat64,
    phi_ar1: float,
):
    if (
        len(frequencies_cph) > 1
        and frequencies_cph[0] == 0
        and phi_ar1 > 0.995
    ) and (
        null_curve_psd_cph[0] > (null_curve_psd_cph[1] * 2)
        and null_curve_psd_cph[1] > 0
    ):
        adjusted_null_curve = null_curve_psd_cph.copy()
        adjusted_null_curve[0] = null_curve_psd_cph[1] * 1.5
        null_curve_psd_cph = adjusted_null_curve

    return null_curve_psd_cph


def _red_noise_null_hypothesis(
    time_series: ArrayFloat64,
    frequencies_cph: ArrayFloat64,
    sampling_rate_cph: float,
) -> ArrayFloat64:
    phi_ar1, innovation_variance = _estimate_ar1_parameters(time_series)

    null_curve_psd_cph = _red_noise_spectrum(
        frequencies_cph, phi_ar1, innovation_variance, sampling_rate_cph
    )

    return _red_noise_adjust_spectrum(
        frequencies_cph, null_curve_psd_cph, phi_ar1
    )


def _white_noise_spectrum(
    frequencies_cph: ArrayFloat64,
    innovation_variance: float,
    sampling_rate_cph: float,
) -> ArrayFloat64:
    fs_hz = sampling_rate_cph / 3600.0

    dt_sec = 1 / fs_hz

    psd_hz_constant = 2.0 * dt_sec * innovation_variance

    psd_cph_constant = psd_hz_constant / 3600.0

    return full_like(frequencies_cph, psd_cph_constant)


def _white_noise_null_hypothesis(
    time_series: ArrayFloat64,
    frequencies_cph: ArrayFloat64,
    sampling_rate_cph: float,
) -> ArrayFloat64:
    innovation_variance = cast(float, var(time_series))

    return _white_noise_spectrum(
        frequencies_cph, innovation_variance, sampling_rate_cph
    )


def null_hypothesis(
    time_series: ArrayFloat64,
    frequencies_cph: ArrayFloat64,
    sampling_rate_cph: float,
    noise_type: str = "white",
) -> ArrayFloat64:
    if noise_type == "white":
        return _white_noise_null_hypothesis(
            time_series, frequencies_cph, sampling_rate_cph
        )
    if noise_type == "red":
        return _red_noise_null_hypothesis(
            time_series, frequencies_cph, sampling_rate_cph
        )
    raise ValueError("Invalid `noise_type`, expected: 'red' or 'white'")


def degrees_of_freedom(
    nsamples: int,
    nperseg: int,
    noverlap: int,
    window_type: str,
) -> float:
    nu_eff_factor_mapping = {
        "bartlett": 2.0,
        "blackman": 1.667,
        "boxcar": 2.0,
        "hamming": 2.22,
        "hann": 2.667,
    }

    if window_type not in nu_eff_factor_mapping:
        raise ValueError("Invalid windowing function")

    nu_eff_factor = nu_eff_factor_mapping.get(window_type, 2.0)

    num_segments = (
        1
        if nperseg >= nsamples
        else (int(floor((nsamples - nperseg) / (nperseg - noverlap))) + 1)
    )

    nu_eff = nu_eff_factor * num_segments

    return max(nu_eff, 2.0)


def calculate_confidence_level(
    level: float, null_curve: ArrayFloat64, dof: float
) -> ArrayFloat64:
    chi2_factor_level = chi2.ppf(level, dof) / dof

    return null_curve * chi2_factor_level
