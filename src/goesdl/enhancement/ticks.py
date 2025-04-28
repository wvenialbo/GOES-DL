from .constants import CBTICKS_NMAX, CBTICKS_SMIN, CBTICKS_STEP
from .shared import DomainData, KeypointList


class ColorbarTicks:

    cticks: KeypointList
    nticks: int
    tickstep: int

    def __init__(
        self,
        extent: DomainData,
        nticks: int | None = None,
        tickstep: int | None = None,
    ) -> None:
        """
        Create a list of colorbar ticks for the given temperature range.

        Creates a list of ticks evenly spaced between tmin and tmax,
        with a minimum step of CBTICKS_SMIN=5.

        Parameters
        ----------
        extent: DomainData
            Tuple with minimum and maximum temperature.
        nticks : int
            Maximum number of ticks, used to estimate the tick step
            if not provided.
        tickstep : int, optional
            Tick step, by default None (automatic).

        Returns
        -------
        list[float]
            List of colorbar ticks.
        """
        if not nticks:
            nticks = CBTICKS_NMAX
        elif tickstep:
            raise ValueError(
                f"'nticks={nticks}' is not compatible with 'tickstep'"
            )

        if tickstep is None:
            tickstep = CBTICKS_STEP
        elif 0 < tickstep < CBTICKS_SMIN:
            raise ValueError(
                f"'tickstep' must have a minimum value of {CBTICKS_SMIN}; "
                "use 'tickstep=0' for automatic scpacing"
            )

        tmin, tmax = extent

        if tickstep == 0:
            tickstep = self._find_tick_step(
                tmin, tmax, max_ticks=nticks, min_step=CBTICKS_SMIN
            )

        cbmin = self._find_tick_min(tmin, tickstep)
        cbmax = self._find_tick_max(tmax, tickstep) + 1

        self.cticks = [float(tick) for tick in range(cbmin, cbmax, tickstep)]
        self.nticks = nticks
        self.tickstep = tickstep

    def get_ticklabels(self, offset: float = 0.0) -> KeypointList:
        return [tick + offset for tick in self.cticks]

    @staticmethod
    def _find_tick_max(vmax: float, step: int) -> int:
        """
        Finds the last multiple of `step` that is less or equal to `vmax`.

        Parameters
        ----------
        vmax : float
            The number from which the last multiple less or equal will be
            searched.
        step : int
            The number of which we want to find the multiples.

        Returns
        -------
        int
            The last multiple of `step` that is less or equal to `vmax`.
        """
        cociente = vmax // step
        return int(cociente) * step

    @staticmethod
    def _find_tick_min(vmin: float, step: int) -> int:
        """
        Finds the first multiple of `step` that is greater or equal to
        `vmin`.

        Parameters
        ----------
        vmin : float
            The number from which the first multiple greater or equal will
            be searched.
        step : int
            The number of which we want to find the multiples.

        Returns
        -------
        int
            The first multiple of `step` that is greater or equal to `vmin`.
        """
        quotient, remainder = divmod(vmin, step)
        return int(quotient + 1 if remainder else quotient) * step

    @classmethod
    def _find_tick_step(
        cls, tmin: float, tmax: float, max_ticks: int, min_step: int
    ) -> int:
        """
        Finds the step that divides the range [tmin, tmax] into `ticks`
        intervals.

        Parameters
        ----------
        tmin : float
            The minimum value of the range.
        tmax : float
            The maximum value of the range.
        max_ticks : int, optional
            The maximum number of intervals to divide the range.
        min_step : int, optional
            The minimum tick step to consider. Larger steps will be
            multiple of this value.

        Returns
        -------
        float
            The step that divides the range [tmin, tmax] into up
            to `max_ticks` intervals.
        """
        return cls._find_tick_min((tmax - tmin) / max_ticks, min_step)
