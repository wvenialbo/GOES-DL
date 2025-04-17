import numpy as np
import numpy.fft as fft


def parabolic_interpolation(power_spectrum, peak_index):
    # Cannot interpolate across edges
    if peak_index <= 0 or peak_index >= len(power_spectrum) - 1:
        return 0, 0

    # Power values at three consecutive points
    y0 = power_spectrum[peak_index - 1]
    y1 = power_spectrum[peak_index]
    y2 = power_spectrum[peak_index + 1]

    # Avoid division by zero
    denominator = y0 - 2 * y1 + y2

    if np.abs(denominator) < 1e-10:
        return 0, 0

    numerator = y0 - y2

    # Calculating delta shift using parabolic interpolation formula
    delta = 0.5 * numerator / denominator

    true_index = peak_index + delta
    true_power = y1 - 0.25 * numerator * delta

    return delta, true_index, true_power


def find_frequencies2(
    signal,
    sampling_rate,
    num_freqs=1,
    apply_window=True,
    interp=True,
    min_amplitude=None,
):
    # Compute signal size
    signal_size = len(signal)

    # Apply window to reduce spectral leakage
    if apply_window:
        window = np.hanning(signal_size)
        signal = signal * window
        # Compensation factor
        scale = 1.0 / (window**2).mean()
    else:
        # Standard windowless normalization
        scale = 1.0 / signal_size

    # Calculate FFT and power spectrum
    fft_result = fft.rfft(signal)
    power_spectrum = np.abs(fft_result) ** 2 * scale

    # Peak detection with threshold (excluding DC component)
    all_indices = np.arange(1, len(power_spectrum))

    # Apply amplitude threshold if specified
    if min_amplitude is None:
        candidate_indices = all_indices
    else:
        valid_mask = power_spectrum[1:] >= min_amplitude
        candidate_indices = all_indices[valid_mask]

    # Find the indices of the strongest peaks (excluding DC component)
    ordered_indices = np.argsort(-power_spectrum[candidate_indices])
    sorted_indices = candidate_indices[ordered_indices]

    # Select dominant frequencies
    selected_indices = (
        sorted_indices[:num_freqs] if num_freqs else sorted_indices
    )

    # Get base frequencies
    frequencies = fft.rfftfreq(signal_size, d=1.0 / sampling_rate)

    # Case management without detected peaks
    if len(selected_indices) == 0:
        return np.array([]), frequencies, power_spectrum

    # Apply parabolic interpolation to each selected peak
    if interp:
        refined_freqs = []
        bin_resolution = sampling_rate / signal_size
        for idx in selected_indices:
            # Only interpolate valid peaks
            if 0 < idx < len(power_spectrum) - 1:
                delta = parabolic_interpolation(power_spectrum, idx)
                refined_freq = frequencies[idx] + delta * bin_resolution
                refined_freqs.append(refined_freq)
            else:
                refined_freqs.append(frequencies[idx])
        dominant_freqs = np.array(refined_freqs)
    else:
        dominant_freqs = frequencies[selected_indices]

    return dominant_freqs, frequencies, power_spectrum


def find_dominant_frequency(signal, sampling_rate, num_freqs):
    fft_result = fft.rfft(signal)
    frequencies = fft.rfftfreq(len(signal), d=1 / sampling_rate)
    idxs = np.argsort(np.abs(fft_result[1:]))[::-1][:num_freqs] + 1
    dominant_freqs = frequencies[idxs]
    dominant_freqs = dominant_freqs[dominant_freqs > 0]
    return dominant_freqs, frequencies, fft_result


def reduce_frequency_space(signal, n=3):
    fft_result = fft.fft(signal)
    fft_result[0] = 0
    fft_ordered = np.argsort(np.abs(fft_result))[::-1]
    fft_filtered = np.zeros_like(fft_result)
    fft_filtered[fft_ordered[:n]] = fft_result[fft_ordered[:n]]
    return fft.ifft(fft_filtered).real
