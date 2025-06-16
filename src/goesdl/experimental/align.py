from collections.abc import Sequence
from typing import cast

from numpy import argmax, asarray, empty, exp, float64, pi, zeros_like
from scipy.fft import irfft, rfft, rfftfreq
from scipy.signal import butter, correlate, correlation_lags, filtfilt

from ..utils.array import ArrayFloat, SequenceFloat, ToFloat, ToIndex, ToInt
from .helper import parabolic_interpolation_xy


class SignalAligner:

    sampling_rate: ToFloat
    signal: ArrayFloat
    delays: ArrayFloat

    filter_params: tuple[ToFloat, ToFloat, ToInt] | None

    def __init__(
        self,
        sampling_rate: ToFloat,
        filter_params: tuple[ToFloat, ToFloat, ToInt] | None = None,
    ) -> None:
        if sampling_rate <= 0:
            raise ValueError(
                "`sampling_rate` must be a positive number, "
                f"got {sampling_rate}"
            )

        self.sampling_rate = sampling_rate
        self.filter_params = filter_params
        self.signal = empty(0, dtype=float64)
        self.delay = empty(0, dtype=float64)

    def align(
        self, input_signals: Sequence[SequenceFloat], reference: ToIndex = 0
    ) -> None:
        # Number of series
        nseries = len(input_signals)

        if nseries == 0:
            return

        # Length of signals
        nsamples = len(input_signals[0])

        # Validate the reference index
        if not (0 <= reference < nseries):
            raise ValueError(
                "`reference` must be an integer number "
                f"between 0 and {nseries}, got {reference}"
            )

        # 1. Apply band-pass filter to all signals before delay
        #    estimation and FFT, if required
        processed_signals: list[ArrayFloat] = []

        if self.filter_params:
            lowcut, highcut, order = self.filter_params

            nyquist = 0.5 * self.sampling_rate

            b, a = butter(
                order, [lowcut / nyquist, highcut / nyquist], btype="band"
            )

            processed_signals.extend(
                filtfilt(b, a, signal) for signal in input_signals
            )

        else:
            processed_signals.extend(
                asarray(signal) for signal in input_signals
            )

        # Initialize a list for the correct sized delays
        delays: list[ToFloat] = [0.0] * nseries

        # Get the reference signal (filtered if applicable)
        reference_signal = processed_signals[reference]

        # 2. Estimate time delays using the pre-filtered signal if
        #    applicable
        for i in range(nseries):
            if i == reference:
                # The reference sensor has 0 delay with itself
                delays[i] = 0.0

            else:
                # Estimate the delay of the current i-th signal with
                # respect to the reference
                delay = self._estimate_delay(
                    processed_signals[i], reference_signal
                )

                delays[i] = delay

        self.delays = asarray(delays)

        # 3. Calculate FFT of each signal and generate the frequency
        #    vector (using the original signals if they were not
        #    globally filtered)

        # - If the idea is to reconstruct the entire aligned signal, the
        #   FFTs should be performed on the original signal
        # - Filtering is only for delay estimation
        # - If you want an already filtered reconstructed signal, then
        #   apply the filter here
        # - For the overall reconstruction, we will use the original
        #   signals for the final FFTs

        # We use the original signals here
        fft_results = [rfft(signal) for signal in input_signals]

        frequencies = rfftfreq(nsamples, d=1 / self.sampling_rate)

        # 4. Apply phase correction and average coherently
        fft_ref = fft_results[reference]

        # Initialize the complex zero-aligned average spectrum
        aligned_fft_average = zeros_like(fft_ref, dtype=fft_ref.dtype)

        delay_factor = 1j * 2 * pi * frequencies

        for i in range(nseries):
            # Phase correction factor: e^(j * 2 * pi * f * tau_i)

            # Make sure tau_i has the correct sign to "undo" the delay
            phase_correction_factor = exp(delay_factor * delays[i])

            # Apply phase correction
            aligned_fft_results = fft_results[i] * phase_correction_factor

            # Add to coherent average
            aligned_fft_average += aligned_fft_results

        # Normalize the average
        aligned_fft_average /= nseries

        # 5. Calculate the IFFT to reconstruct the aligned signal
        self.signal = irfft(aligned_fft_average, n=nsamples)

    def _estimate_delay(
        self, target_signal: ArrayFloat, reference_signal: ArrayFloat
    ) -> ToFloat:
        # Perform cross-correlation
        correlation = correlate(target_signal, reference_signal, mode="full")

        # Find correlation lags
        lags = correlation_lags(
            target_signal.size, reference_signal.size, mode="full"
        )

        # Find the peak (integer sample index)
        peak_idx = argmax(correlation)

        # Parabolic interpolation for subsample accuracy
        delay_samples, _ = parabolic_interpolation_xy(
            lags, cast(ArrayFloat, correlation), peak_idx
        )

        return delay_samples / self.sampling_rate
