from math import ceil, log2, nan, sqrt
from typing import Any, cast

from numpy import (
    abs,
    any,
    argsort,
    asarray,
    complex128,
    diff,
    empty,
    float64,
    full_like,
    int64,
    isnan,
    nanargmin,
    nonzero,
    split,
    sum,
    where,
    zeros,
    zeros_like,
)
from scipy.fft import irfft, rfft
from scipy.signal import get_window, periodogram, welch

from ..utils.array import (
    ArrayBool,
    ArrayComplex,
    ArrayComplex128,
    ArrayFloat,
    ArrayIndex,
    ArrayInt,
    SequenceFloat,
    ToFloat,
    ToInt,
)
from .confidence import (
    calculate_confidence_level,
    calculate_p_values,
    degrees_of_freedom,
    null_hypothesis,
)
from .helper import parabolic_interpolation_y, validate_1d_signal

SUPPORTED_WINDOW_FUNCTIONS = {
    "bartlett",
    "blackman",
    "boxcar",
    "hamming",
    "hann",
}


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
    fft: ArrayComplex
    fft_size: int
    frequencies: ArrayFloat
    rank: ArrayInt
    sampling_rate: float
    signal_size: int
    window: str

    density_spectrum: ArrayFloat

    peak_boundaries: ArrayInt
    peak_indices: ArrayInt
    peak_values: ArrayFloat

    null: ArrayFloat
    p_value: ArrayFloat
    dof: float

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
            raise ValueError(
                "`sampling_rate` must be a positive number, "
                f"got {sampling_rate}"
            )

        if signal_size <= 0:
            raise ValueError(
                "`signal_size` must be a positive integer, "
                f"got {signal_size}"
            )

        if fft_size is None:
            fft_size = signal_size
        elif fft_size == 0:
            fft_size = int(2 ** ceil(log2(signal_size)))
        elif fft_size < signal_size:
            raise ValueError(
                "`fft_size` must be None, 0, or an integer greater "
                f"than or equal to {signal_size}, got {fft_size}"
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

        self.null = zeros(nyquist_size, dtype=float64)
        self.p_value = zeros(nyquist_size, dtype=float64)
        self.dof = nan

    def apply(
        self,
        signal: SequenceFloat,
        nperseg: ToInt | None = None,
        noverlap: ToInt | None = None,
        noise: str = "white",
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
        signal : ArrayFloat
            The input signal as a 1D array.
        """
        signal = self._validate_signal(signal)

        win_id = cast(Any, self.window)
        window = get_window(win_id, self.signal_size, False)
        windowed_signal = signal * window

        if nperseg is None:
            nperseg = self.signal_size
            noverlap = 0
            frequencies, density_spectrum = periodogram(
                x=signal,
                fs=self.sampling_rate,
                window=cast(Any, self.window),
                nfft=self.fft_size,
                detrend=False,
                return_onesided=True,
                scaling="density",
            )
        else:
            noverlap = 0 if noverlap is None else max(int(nperseg // 2), 1)
            frequencies, density_spectrum = welch(
                x=signal,
                fs=self.sampling_rate,
                window=cast(Any, self.window),
                nperseg=nperseg,
                noverlap=noverlap,
                nfft=self.fft_size,
                detrend=False,
                return_onesided=True,
                scaling="density",
            )

        # Compute the normalised unilateral FFT of the signal
        self.fft = cast(ArrayComplex128, rfft(windowed_signal, self.fft_size))
        self.density_spectrum = cast(ArrayFloat, density_spectrum)
        self.frequencies = frequencies

        self._perform_analysis(self.density_spectrum)

        nsamples = self.signal_size
        window_type = self.window

        dof = degrees_of_freedom(nsamples, int(nperseg), noverlap, window_type)
        self.dof = dof

        sampling_rate = self.sampling_rate

        psd_null = null_hypothesis(signal, frequencies, sampling_rate, noise)
        self.null = psd_null

        psd_observed = density_spectrum

        self.p_value = calculate_p_values(psd_observed, psd_null, dof)

    def confidence_threshold(self, level: float) -> ArrayFloat:
        return calculate_confidence_level(level, self.null, self.dof)

    def find_frequency(
        self, frequencies: list[float] | float | int, tolerance: float = 0.1
    ) -> list[int]:
        if isinstance(frequencies, (float, int)):
            frequencies = [float(frequencies)]

        indices: list[int] = []

        for frequency in frequencies:
            absdiff = abs(self.dominant_frequencies - frequency)
            nearest_index = nanargmin(absdiff)
            if absdiff[nearest_index] > tolerance * frequency:
                continue
            indices.append(round(nearest_index))

        return indices

    def reconstruct_components(self, indices: list[int] | int) -> ArrayFloat:
        if isinstance(indices, int):
            indices = [indices]

        fft_filtered = zeros_like(self.fft, dtype=complex128)
        power_spectrum = abs(self.fft) ** 2

        for index in indices:
            if index < 0 or index >= len(self.peak_indices):
                raise ValueError(
                    "`indices` must contain integer values "
                    f"between 0 and {len(self.peak_indices)-1}"
                )

            peak_index = self.peak_indices[index]
            left_idx, right_idx = self.peak_boundaries[index, :]

            total_power = sum(power_spectrum[left_idx : right_idx + 1])
            original_amplitude = abs(self.fft[peak_index])

            if original_amplitude > 1e-10:
                new_amplitude = sqrt(total_power)

                fft_filtered[peak_index] = self.fft[peak_index] * (
                    new_amplitude / original_amplitude
                )

        return self._reconstruct_fft_signal(fft_filtered)

    def reconstruct_signal(self, size: float = 1.0) -> ArrayFloat:
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

    def significant_densities(
        self, level: float, upper: float = 0.0
    ) -> ArrayFloat:
        peak_densities = self.dominant_densities
        is_dominant = self._is_dominant(level, upper)
        return peak_densities[is_dominant]

    def significant_frequencies(
        self, level: float, upper: float = 0.0
    ) -> ArrayFloat:
        peak_frequencies = self.dominant_frequencies
        is_dominant = self._is_dominant(level, upper)
        return peak_frequencies[is_dominant]

    def significant_peaks(self, level: float) -> ArrayFloat:
        psd_observed = self.density_spectrum
        threshold = self.confidence_threshold(level)
        return where(psd_observed > threshold, psd_observed, nan)

    def _is_dominant(self, level: float, upper: float) -> ArrayBool:
        threshold = self.confidence_threshold(level)
        peak_indices = self.peak_indices
        peak_densities = self.dominant_densities

        is_dominant = peak_densities > threshold[peak_indices]

        if upper > level:
            threshold = self.confidence_threshold(upper)
            is_dominant = is_dominant & (
                peak_densities <= threshold[peak_indices]
            )

        return is_dominant

    def _perform_analysis(self, spectrum: ArrayFloat) -> None:
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
        self, fft_filtered: ArrayComplex
    ) -> ArrayFloat:
        fft_filtered[0] = self.fft[0]

        windowed_signal = irfft(fft_filtered, n=self.fft_size)
        windowed_signal = windowed_signal[: self.signal_size]

        return windowed_signal.astype(float64, copy=False)

    def _remove_window(self, windowed_signal: ArrayFloat) -> ArrayFloat:
        win_id = cast(Any, self.window)
        window = get_window(win_id, self.signal_size, False)
        non_zero_mask = window > self.dewindow_threshold

        dewindowed_signal = zeros_like(window)
        dewindowed_signal[non_zero_mask] = (
            windowed_signal[non_zero_mask] / window[non_zero_mask]
        )

        return dewindowed_signal.astype(float64)

    def _validate_signal(self, signal: SequenceFloat) -> ArrayFloat:
        signal_data = validate_1d_signal(signal)

        if len(signal) != self.signal_size:
            raise ValueError(
                f"Invalid signal size, expected {self.signal_size}, "
                f"got {len(signal)}"
            )

        if isnan(signal_data).any():
            raise ValueError("Input signal contains NaN values")

        return signal_data

    @property
    def dominant_densities(self) -> ArrayFloat:
        return self.peak_values[:, 1]

    @property
    def dominant_frequencies(self) -> ArrayFloat:
        """
        Get the dominant frequencies in the signal.

        Returns
        -------
        ArrayFloat
            The dominant frequencies in the signal.
        """
        return self.peak_values[:, 0]

    @property
    def has_nyquist(self) -> bool:
        return self.fft_size % 2 == 0


def _find_peak_boundaries(spectrum: ArrayFloat, indices: ArrayInt) -> ArrayInt:
    valley_indices = _find_peak_indices(-spectrum)

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


def _find_peak_indices(spectrum: ArrayFloat) -> ArrayInt:
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


def _find_peak_values(spectrum: ArrayFloat, indices: ArrayIndex) -> ArrayFloat:
    values: list[tuple[ToFloat, ToFloat]] = []

    for index in indices:
        true_location, true_value = parabolic_interpolation_y(spectrum, index)
        values.append((true_location, true_value))

    return asarray(values, dtype=float64)


def _find_peaks(
    spectrum: ArrayFloat,
) -> tuple[ArrayInt, ArrayInt, ArrayFloat]:
    indices = _find_peak_indices(spectrum)
    boundaries = _find_peak_boundaries(spectrum, indices)
    values = _find_peak_values(spectrum, indices)

    return indices, boundaries, values
