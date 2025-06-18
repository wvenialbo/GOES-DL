from math import floor, inf
from typing import Any, cast

from numpy import clip, corrcoef, cos, full_like, pi, sqrt, sum, var, where
from scipy.linalg import LinAlgError
from scipy.signal import correlate, get_window
from scipy.stats import chi2
from statsmodels.tsa.arima.model import ARIMA, ARIMAResults

from ..utils.array import ArrayFloat, ToFloat


def _estimate_ar1_parameters(time_series: ArrayFloat) -> tuple[float, float]:
    try:
        model = ARIMA(time_series, order=(1, 0, 0))
        results = cast(ARIMAResults, model.fit())
        phi_ar1 = cast(float, results.params[1])

        innovation_variance = cast(float, results.params[2])

    except (ValueError, LinAlgError):
        if len(time_series) > 1:
            phi_ar1 = corrcoef(time_series[:-1], time_series[1:])[0, 1]
            phi_ar1 = clip(phi_ar1, -0.999, 0.999)
        else:
            phi_ar1 = 0.0

        innovation_variance = cast(float, var(time_series))

    return phi_ar1, innovation_variance


def _red_noise_spectrum(
    frequencies_cph: ArrayFloat,
    phi_ar1: ToFloat,
    innovation_variance: ToFloat,
    sampling_rate_cph: ToFloat,
) -> ArrayFloat:
    frequencies_hz = frequencies_cph / 3600.0
    fs_hz = sampling_rate_cph / 3600.0

    dt_sec = 1 / fs_hz
    f_norm = frequencies_hz * dt_sec

    denominator: ArrayFloat = (
        1 + phi_ar1**2 - 2 * phi_ar1 * cos(2 * pi * f_norm)
    )
    denominator = clip(denominator, 1e-15, None)

    ar1_psd_hz = 2.0 * dt_sec * innovation_variance / denominator

    return cast(ArrayFloat, ar1_psd_hz / 3600.0)


def _red_noise_adjust_spectrum(
    frequencies_cph: ArrayFloat,
    null_curve_psd_cph: ArrayFloat,
    phi_ar1: float,
) -> ArrayFloat:
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
    time_series: ArrayFloat,
    frequencies_cph: ArrayFloat,
    sampling_rate_cph: float,
) -> ArrayFloat:
    phi_ar1, innovation_variance = _estimate_ar1_parameters(time_series)

    null_curve_psd_cph = _red_noise_spectrum(
        frequencies_cph, phi_ar1, innovation_variance, sampling_rate_cph
    )

    return _red_noise_adjust_spectrum(
        frequencies_cph, null_curve_psd_cph, phi_ar1
    )


def _white_noise_spectrum(
    frequencies_cph: ArrayFloat,
    innovation_variance: float,
    sampling_rate_cph: float,
) -> ArrayFloat:
    fs_hz = sampling_rate_cph / 3600.0

    dt_sec = 1 / fs_hz

    psd_hz_constant = 2.0 * dt_sec * innovation_variance

    psd_cph_constant = psd_hz_constant / 3600.0

    return full_like(frequencies_cph, psd_cph_constant)


def _white_noise_null_hypothesis(
    time_series: ArrayFloat,
    frequencies_cph: ArrayFloat,
    sampling_rate_cph: float,
) -> ArrayFloat:
    innovation_variance = cast(float, var(time_series))

    return _white_noise_spectrum(
        frequencies_cph, innovation_variance, sampling_rate_cph
    )


def _get_nu_welch_params(
    nsamples: int, nperseg: int, noverlap: int, window_type: str
) -> tuple[ArrayFloat, int, int, bool]:
    try:
        win_id = cast(Any, window_type)
        raw_window = get_window(win_id, nperseg)
    except ValueError as error:
        raise ValueError(
            f"Error al generar la ventana '{window_type}' con nperseg={nperseg}: {error}"
        ) from error

    raw_window_sqr = raw_window**2
    sum_window_sqr = sum(raw_window_sqr)

    if sum_window_sqr > 0:
        norm_window = sqrt(raw_window_sqr / sum(raw_window_sqr))
    else:
        norm_window = raw_window

    nshift = nperseg - noverlap

    if nshift <= 0:
        return norm_window, 0, 0, True

    if nperseg >= nsamples:
        nblocks = 1
    else:
        nblocks = int(floor((nsamples - nperseg) / nshift)) + 1

    if nblocks < 1:
        return norm_window, 0, 0, True

    return norm_window, nblocks, nshift, False


def _calculate_nu_factor_welch(
    window: ArrayFloat, nblocks: int, nshift: int
) -> float:
    nperseg = len(window)

    autocorr_full = correlate(window, window, mode="full")

    sum_m_terms = 0.0
    for m_val in range(1, nblocks):
        mn_lag = m_val * nshift

        autocorr_idx = nperseg - 1 + mn_lag
        if autocorr_idx < len(autocorr_full):
            inner_sum_product = autocorr_full[autocorr_idx]
            term = (1 - m_val / nblocks) * (abs(inner_sum_product) ** 2)
            sum_m_terms += float(term)

    denominator = 1.0 + 2.0 * sum_m_terms

    return inf if denominator <= 0 else 2.0 / denominator


def null_hypothesis(
    time_series: ArrayFloat,
    frequencies_cph: ArrayFloat,
    sampling_rate_cph: float,
    noise_type: str = "white",
) -> ArrayFloat:
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
    nsamples: int, nperseg: int, noverlap: int, window_type: str
) -> float:
    window, nblocks, nshift, is_invalid = _get_nu_welch_params(
        nsamples, nperseg, noverlap, window_type
    )

    if is_invalid:
        return 2.0

    nu_eff_factor = _calculate_nu_factor_welch(window, nblocks, nshift)

    nu_eff = nblocks * nu_eff_factor

    return max(nu_eff, 2.0)


def calculate_confidence_level(
    level: float, null_curve: ArrayFloat, dof: float
) -> ArrayFloat:
    chi2_factor_level = chi2.ppf(level, dof) / dof

    return null_curve * chi2_factor_level


def calculate_p_values(
    psd_observed: ArrayFloat, psd_null: ArrayFloat, dof: float
) -> ArrayFloat:
    null_curve_safe = where(psd_null < 1e-9, 1e-9, psd_null)

    chi2_stat = dof * psd_observed / null_curve_safe

    p_values = 1 - chi2.cdf(chi2_stat, df=dof)

    return cast(ArrayFloat, p_values)
