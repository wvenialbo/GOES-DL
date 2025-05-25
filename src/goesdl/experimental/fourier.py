from typing import cast

from numpy import (
    abs,
    argsort,
    asarray,
    bartlett,
    blackman,
    complex128,
    empty,
    float64,
    hamming,
    hanning,
    int64,
    isnan,
    nanmean,
    nanmedian,
    nonzero,
    ones,
    sum,
    zeros_like,
)
from scipy.fft import irfft, rfft, rfftfreq
from scipy.interpolate import interp1d

from ..utils.array import ArrayComplex128, ArrayFloat64, ArrayInt64

# > from numpy.fft import irfft, rfft, rfftfreq
# > from scipy.fft import fft, ifft, rfft, rfftfreq
# > from scipy.signal.windows import bartlett, blackman, hamming, hanning

SUPPORTED_FILL_METHODS = {"mean", "median"}

SUPPORTED_WINDOW_FUNCTIONS = {
    "bartlett",
    "blackman",
    "boxcar",
    "hamming",
    "hann",
    "none",
}


class FourierAnalysis:
    """
    Fourier Analysis class for time series data.

    This class performs Fourier analysis on time series data, allowing
    for the computation of the Fourier Transform, power spectrum,
    frequencies, and dominant frequencies. It also provides methods for
    filling missing data and applying window functions to reduce
    spectral leakage.

    Attributes
    ----------
    amplitudes : ArrayFloat64
        The normalised magnitudes of the FFT result.
    fft : ArrayComplex128
        The Fourier Transform of the signal.
    frequencies : ArrayFloat64
        The frequency bins corresponding to the Fourier Transform.
    frequency_order : ArrayInt64
        The indices ordered by dominant frequencies.
    power_spectrum : ArrayFloat64
        The normalised unilateral power spectrum.
    sampling_rate : float
        The sampling rate of the signal, in cycles (observations) per
        hour.
    signal : ArrayFloat64
        The input signal with NaN values filled.
    window_function : str
        The window function applied to the signal to reduce spectral
        leakage.  Supported methods are: 'hanning', 'hamming',
        'blackman', 'bartlett', and 'none'.
    """

    amplitudes: ArrayFloat64
    fft: ArrayComplex128
    fft_size: int
    frequencies: ArrayFloat64
    frequency_order: ArrayInt64
    has_nyquist: bool
    power_spectrum: ArrayFloat64
    sampling_rate: float
    signal: ArrayFloat64
    window_function: str

    def __init__(
        self, sampling_rate: float, window_function: str = "hann"
    ) -> None:
        """
        Initialize the FourierAnalysis object.

        Parameters
        ----------
        sampling_rate : float
            The sampling rate of the signal, in cycles (observations)
            per hour.
        window_function : str, optional
            The window function to apply to the signal. Supported
            methods are: 'hann' (default), 'hamming', 'blackman',
            'bartlett', and 'none' or 'boxcar'. If 'none' is selected,
            the function will not apply any windowing to the signal.
        """
        if sampling_rate <= 0:
            raise ValueError("Sampling rate must be positive number")

        if window_function not in SUPPORTED_WINDOW_FUNCTIONS:
            supported = "', '".join(SUPPORTED_WINDOW_FUNCTIONS)
            raise ValueError(
                f"Unsupported window function: '{window_function}', "
                f"supported methods are: '{supported}'"
            )

        self.amplitudes = empty(0, dtype=float64)
        self.fft = empty(0, dtype=complex128)
        self.fft_size = 0
        self.frequencies = empty(0, dtype=float64)
        self.frequency_order = empty(0, dtype=int64)
        self.has_nyquist = False
        self.power_spectrum = empty(0, dtype=float64)
        self.sampling_rate = sampling_rate
        self.signal = empty(0, dtype=float64)
        self.window_function = window_function

    def apply(self, signal: ArrayFloat64, fft_size: int = 0) -> None:
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
        fft_size : int, optional
            The size of the FFT. If not provided, the function will
            automatically determine the size based on the input signal
            and the next power of 2. The default is 0, which means the
            function will use the next power of 2 for the FFT size.
        """
        self.signal = self._validate_signal(signal)

        self.fft_size = self._validate_fft_size(signal.size, fft_size)

        self.has_nyquist = self.fft_size % 2 == 0
        sampling_period = 1 / self.sampling_rate

        # Apply a window to the signal to reduce spectral leakage
        window = self._get_window_function(signal.size)
        windowed_signal = self.signal * window

        # Sum of window for normalization
        window_sum = sum(window)

        # Compute the normalised unilateral FFT of the signal
        #
        # Note: rfft will zero-pad if fft_size > len(windowed_signal)
        self.fft = cast(ArrayComplex128, rfft(windowed_signal, self.fft_size))

        # Normalize by window sum to account for the windowing effect
        fft_result = self.fft / window_sum

        # Compute the normalised magnitudes (amplitudes)
        self.amplitudes: ArrayFloat64 = abs(fft_result)

        # Compute the normalised unilateral power spectrum
        self.power_spectrum: ArrayFloat64 = self.amplitudes**2

        # Adjust power spectrum for unilateral representation
        #
        # Note: DC component (index 0) and Nyquist component (if
        # present) are not doubled.
        if self.has_nyquist:
            # Exclude DC (0) and Nyquist (last element) for even signal
            # size
            self.power_spectrum[1:-1] *= 2
            # power_subset for sorting should also exclude DC and
            # Nyquist
            power_subset = self.power_spectrum[1:-1]
        else:
            # Exclude DC (0) only for odd signal size
            self.power_spectrum[1:] *= 2
            # power_subset for sorting should exclude DC
            power_subset = self.power_spectrum[1:]

        # Compute the frequency (in sampling_period units) bins
        self.frequencies = cast(
            ArrayFloat64, rfftfreq(self.fft_size, d=sampling_period)
        )

        self.frequency_order = argsort(power_subset)[::-1] + 1

    def recontruct_signal(self, nfirst: int) -> ArrayFloat64:
        if nfirst <= 0 or nfirst > len(self.frequency_order):
            raise ValueError(
                "`nfirst` must be between "
                f"1 and {len(self.frequency_order)}"
            )

        fft_filtered = zeros_like(self.fft)

        sorted_indices = self.frequency_order[:nfirst]

        fft_filtered[sorted_indices] = self.fft[sorted_indices]

        fft_filtered[0] = self.fft[0]

        return irfft(fft_filtered).astype(float64)

    def _get_window_function(self, sampling_size: int) -> ArrayFloat64:
        if self.window_function in {"none", "boxcar"}:
            window = ones(sampling_size)

        elif self.window_function == "hann":
            window = hanning(sampling_size)

        elif self.window_function == "hamming":
            window = hamming(sampling_size)

        elif self.window_function == "blackman":
            window = blackman(sampling_size)

        elif self.window_function == "bartlett":
            window = bartlett(sampling_size)

        else:
            raise ValueError("Invalid windowing function")

        return cast(ArrayFloat64, window)

    def _validate_fft_size(self, signal_size: int, fft_size: int) -> int:
        if fft_size < 0:
            raise ValueError("FFT size must be non-negative.")

        return (
            min(1 << (signal_size - 1).bit_length(), 4096)
            if fft_size == 0
            else max(fft_size, signal_size)
        )

    def _validate_signal(self, signal: ArrayFloat64) -> ArrayFloat64:
        signal_data = _validate_1d_signal(signal)

        if isnan(signal_data).any():
            raise ValueError("Input signal contains NaN values")

        return signal_data

    @property
    def dominant_frequencies(self) -> ArrayFloat64:
        """
        Get the dominant frequencies in the signal.

        Returns
        -------
        ArrayFloat64
            The dominant frequencies in the signal.
        """
        return self.frequencies[self.frequency_order]

    @property
    def dominant_periods(self) -> ArrayFloat64:
        """
        Get the periods corresponding to the dominant frequencies.

        Returns
        -------
        ArrayFloat64
            The dominant periods.
        """
        return 1 / self.dominant_frequencies


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
                start_idx=nan_idx,
                step_direction=-self.sample_step,
                boundary=0,
            )

            # Find known points after the NaN index
            known_points_after = self._find_known_points(
                start_idx=nan_idx,
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
                nan_idx, signal_filled, relevant_indices
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


def _validate_1d_signal(signal: ArrayFloat64) -> ArrayFloat64:
    # Ensure the signal is a 1D array
    signal_data = asarray(signal, copy=False, dtype=float64)

    # Validate the signal dimensions and size
    if signal_data.ndim != 1:
        raise ValueError("Input signal must be a 1D array.")

    if signal_data.size == 0:
        raise ValueError("Input signal is empty.")

    return signal_data


def parabolic_interpolation(power_spectrum: ArrayFloat64, peak_index: int):
    # Cannot interpolate across edges
    if peak_index <= 0 or peak_index >= len(power_spectrum) - 1:
        return 0, 0

    # Power values at three consecutive points
    y0 = power_spectrum[peak_index - 1]
    y1 = power_spectrum[peak_index]
    y2 = power_spectrum[peak_index + 1]

    # Avoid division by zero
    denominator = y0 - 2 * y1 + y2

    if abs(denominator) < 1e-10:
        return 0, 0

    numerator = y0 - y2

    # Calculating delta shift using parabolic interpolation formula
    delta = 0.5 * numerator / denominator

    true_index = peak_index + delta
    true_power = y1 - 0.25 * numerator * delta

    return delta, true_index, true_power
