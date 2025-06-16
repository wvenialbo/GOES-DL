from numpy import asarray, float64

from ..utils.array import ArrayFloat, CoFloat, SequenceFloat, ToFloat, ToIndex


def _parabolic_interpolation(
    y_x: ArrayFloat, x_1: ToFloat, x_ref: ToIndex
) -> tuple[ToFloat, ToFloat]:
    # Formula for the parabolic peak (vertex of the parabola):
    #
    #   x_peak = x_center + 0.5 * (y_0 - y_2) / (y_0 - 2 * y_1 + y_2)
    #
    # In our case, x_center=x_1 is the integer peak index (0 for the
    # local system) and the distances are +/- 1.
    #
    # The peak value is:
    #
    #   y_peak = y_center - 0.5**3 * (y_0 - y_2)**2
    #                / (y_0 - 2 * y_1 + y_2)
    y_1 = y_x[x_ref]

    # Make sure the peak is not at the extremes so you can interpolate
    if x_ref in {0, len(y_x) - 1}:
        # If the peak is at an extreme, just use the value at the end,
        # cannot interpolate with 2 points
        return x_1, y_1

    y_0: float = y_x[x_ref - 1]
    y_2: float = y_x[x_ref + 1]

    denominator = y_0 - 2 * y_1 + y_2

    # If the denominator is very small, the peak is flat or not
    # parabolic
    if abs(denominator) < 1e-10:
        # Just return the current value
        return x_1, y_1

    numerator = 0.5 * (y_0 - y_2)

    delta_x = numerator / denominator
    delta_y = -0.5 * numerator * delta_x

    x_value = x_1 + delta_x
    y_value = y_1 + delta_y

    return x_value, y_value


def parabolic_interpolation_xy(
    x_k: ArrayFloat, y_k: ArrayFloat, k_ref: ToIndex
) -> tuple[ToFloat, ToFloat]:
    # Formula for the parabolic peak (vertex of the parabola)
    #
    #   x_peak = x_center + (y_0 - y_2) / (2 * (y_0 - 2 * y_1 + y_2))
    #
    # In our case, x_center=x_k[k_ref] is the integer peak index (0 for
    # the local system)
    return _parabolic_interpolation(y_k, x_k[k_ref], k_ref)


def parabolic_interpolation_y(
    y_x: ArrayFloat, x_ref: ToIndex
) -> tuple[ToFloat, ToFloat]:
    # Formula for the parabolic peak (vertex of the parabola)
    #
    #   x_peak = x_center + (y_0 - y_2) / (2 * (y_0 - 2 * y_1 + y_2))
    #
    # In our case, x_center=x_ref is the integer peak index (0 for the
    # local system)
    return _parabolic_interpolation(y_x, x_ref, x_ref)


def validate_1d_signal(signal: SequenceFloat) -> ArrayFloat:
    # Ensure the signal is a 1D array
    dtype: type[CoFloat] = getattr(signal, "dtype", float64)
    signal_data: ArrayFloat = asarray(signal, dtype=dtype)

    # Validate the signal dimensions and size
    if signal_data.ndim != 1:
        raise ValueError(
            f"Input signal must be a 1D array, got {signal_data.ndim}D"
        )

    if signal_data.size == 0:
        raise ValueError("Input signal is empty.")

    return signal_data
