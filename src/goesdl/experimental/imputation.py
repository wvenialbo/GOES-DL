from numpy import empty, float64, isnan, nanmean, nanmedian, nonzero
from scipy.interpolate import interp1d

from ..utils.array import (
    ArrayFloat,
    SequenceFloat,
    SequenceIndex,
    ToFloat,
    ToIndex,
    ToInt,
)
from .helper import validate_1d_signal

SUPPORTED_FILL_METHODS = {"mean", "median"}


class NaNFill:

    fill_method: str
    signal_data: ArrayFloat

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

        self.signal_data: ArrayFloat = empty(0, dtype=float64)

    def fill(self, signal: SequenceFloat) -> ArrayFloat:
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

    def _validate_signal(self, signal: SequenceFloat) -> ArrayFloat:
        return validate_1d_signal(signal)


class SignalImputator:
    """
    A class to handle the interpolation of NaN values in time series data
    using sparse spline interpolation.
    """

    control_points: ToInt
    half_interval: ToInt
    sampling_rate: ToFloat
    sample_step: ToInt
    signal_data: ArrayFloat
    total_samples: ToInt

    def __init__(self, sampling_rate: ToFloat, control_points: ToInt) -> None:
        """
        Initializes the NaNInterpolator with interpolation parameters.

        Parameters
        ----------
        sampling_rate : int
            The sampling rate of the signal (samples per unit time).
        control_points : int
            The number of control points (samples per unit time).
        """
        sample_step = int(sampling_rate // control_points)

        self.sampling_rate = sampling_rate
        self.control_points = control_points
        self.sample_step = max(sample_step, 1)
        self.half_interval = control_points // 2

        self.signal_data = empty(0, dtype=float64)
        self.total_samples = 0

    def fill(self, signal: SequenceFloat) -> ArrayFloat:
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
            self._apply_interpolation(
                int(nan_idx), signal_filled, relevant_indices
            )

        return signal_filled

    def _apply_interpolation(
        self,
        nan_idx: ToIndex,
        signal_filled: ArrayFloat,
        relevant_indices: SequenceIndex,
    ) -> None:
        if len(relevant_indices) >= 2:
            # Perform cubic spline interpolation if at least two known
            # points are available Use indices directly as 'time' points
            # since data is equally spaced
            t_known = relevant_indices

            # Use instance's signal_data
            y_known = self.signal_data[relevant_indices]

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
        self, start_idx: ToIndex, step_direction: ToIndex, boundary: ToIndex
    ) -> list[int]:
        known_points: list[int] = []
        current_idx = int(start_idx + step_direction)

        while (
            len(known_points) < self.half_interval
            and (step_direction >= 0 or current_idx >= boundary)
            and (step_direction <= 0 or current_idx < boundary)
        ) and 0 <= current_idx < self.total_samples:
            if not isnan(self.signal_data[current_idx]):
                known_points.append(current_idx)
            current_idx += int(step_direction)

        return known_points

    def _validate_signal(self, signal: SequenceFloat) -> ArrayFloat:
        return validate_1d_signal(signal)
