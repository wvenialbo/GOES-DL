from numpy import array, float64, interp

from ..utils.array import ArrayFloat64
from .track_info import TrackInfo


class EventTracker:

    timestamps: ArrayFloat64
    latitudes: ArrayFloat64
    longitudes: ArrayFloat64

    track_info: TrackInfo

    def __init__(self, track_info: TrackInfo) -> None:
        self.track_info = track_info

        # Convert to NumPy arrays
        self.timestamps = array(track_info.timestamps, dtype=float64)
        self.latitudes = array(track_info.latitudes, dtype=float64)
        self.longitudes = array(track_info.longitudes, dtype=float64)

    def get(self, t: float) -> tuple[float, float]:
        """
        Interpolate the longitude and latitude for a given timestamp.

        If the timestamp is outside the range of the track data,
        extrapolation is performed.

        Parameters
        ----------
        t : float
            The tage timestamp for which to interpolate the longitude
            and latitude.

        Returns
        -------
        tuple[float, float]
            A tuple containing the interpolated longitude and latitude.
        """
        return self._interpolate_coordinates(
            t, self.timestamps, self.longitudes, self.latitudes
        )

    @staticmethod
    def _interpolate_value(
        x: float, xp: ArrayFloat64, fp: ArrayFloat64
    ) -> float:
        """
        Perform linear interpolation or extrapolation.

        Performs a linear interpolation using np.interp and, if the
        point is outside the domain, performs a linear extrapolation.

        Parameters
        ----------
        x : float
            The x-coordinate for which to interpolate or extrapolate.
        xp : ArrayFloat64
            The x-coordinates of the data points.
        fp : ArrayFloat64
            The y-coordinates of the data points.

        Returns
        -------
        float
            The interpolated or extrapolated value.
        """
        if x < xp[0]:
            # Linear extrapolation to the left
            slope = (fp[1] - fp[0]) / (xp[1] - xp[0])
            return float(fp[0] + slope * (x - xp[0]))

        if x > xp[-1]:
            # Linear extrapolation to the right
            slope = (fp[-1] - fp[-2]) / (xp[-1] - xp[-2])
            return float(fp[-1] + slope * (x - xp[-1]))

        # Interpolation within the domain
        return float(interp(x, xp, fp))

    @classmethod
    def _interpolate_coordinates(
        cls,
        t: float,
        timestamps: ArrayFloat64,
        longitudes: ArrayFloat64,
        latitudes: ArrayFloat64,
    ) -> tuple[float, float]:
        """
        Interpolate or extrapolate coordinates for a given timestamp

        Interpolate the latitude and longitude for a given timestamp.
        If the timestamp is outside the range of the track data,
        extrapolation is performed.

        Parameters
        ----------
        t : float
            The timestamp for which to interpolate the latitude and
            longitude.
        timestamps : ArrayFloat64
            A sequence of timestamps representing the time of each track
            point.
        longitudes : ArrayFloat64
            A sequence of longitudes corresponding to the track points.
        latitudes : ArrayFloat64
            A sequence of latitudes corresponding to the track points.

        Returns
        -------
        tuple[float, float]
            A tuple containing the interpolated longitude and latitude.
        """
        # Interpolate or extrapolate for the given timestamp
        lon_interp = cls._interpolate_value(t, timestamps, longitudes)
        lat_interp = cls._interpolate_value(t, timestamps, latitudes)

        return lon_interp, lat_interp
