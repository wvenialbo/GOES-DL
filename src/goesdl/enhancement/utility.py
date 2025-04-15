"""Provide utilities for helping color enhancement routines."""

from collections.abc import Sequence

from .shared import ColorSegment


def compress_color_data(
    color_data: list[ColorSegment],
) -> list[ColorSegment]:
    """
    Compress color data by removing duplicate entries.

    Parameters
    ----------
    color_data : list of tuple of float
        List of color segments.

    Returns
    -------
    list of tuple of float
        Compressed color table.
    """
    compressed: list[ColorSegment] = [color_data[0]]

    for x2, c2, d2 in color_data[1:]:
        x1, c1, _ = compressed[-1]
        if x1 == x2:
            compressed[-1] = (x1, c1, d2)
        else:
            compressed.append((x2, c2, d2))

    return compressed


def _interpv(x: float, x0: float, x1: float, y0: float, y1: float) -> float:
    slope = (y1 - y0) / (x1 - x0)
    return y0 + slope * (x - x0)


def _interp(x: float, xp: Sequence[float], yp: Sequence[float]) -> float:
    if x < xp[0] or x >= xp[-1]:
        raise ValueError("Value out of range")

    i = 0
    while i + 1 < len(xp) and x >= xp[i + 1]:
        i += 1

    x0, y0 = xp[i], yp[i]
    x1, y1 = xp[i + 1], yp[i + 1]

    return _interpv(x, x0, x1, y0, y1)


def interp(x: float, xp: Sequence[float], yp: Sequence[float]) -> float:
    """
    Interpolate x based on xp and yp using linear interpolation.

    Parameters
    ----------
    x : float
        The value to interpolate.
    xp : Sequence of float
        The x-coordinates of the data points.
    yp : Sequence of float
        The y-coordinates of the data points.

    Returns
    -------
    float
        The interpolated value.
    """
    return yp[-1] if x == xp[-1] else _interp(x, xp, yp)


def interpc(x: float, xp: Sequence[float], yp: Sequence[float]) -> float:
    """
    Interpolate x based on xp and yp using linear interpolation.

    Interpolate x based on xp and yp using linear interpolation with
    copying.

    Parameters
    ----------
    x : float
        The value to interpolate.
    xp : Sequence of float
        The x-coordinates of the data points.
    yp : Sequence of float
        The y-coordinates of the data points.

    Returns
    -------
    float
        The interpolated value.
    """
    if x <= xp[0]:
        return yp[0]

    return yp[-1] if x >= xp[-1] else _interp(x, xp, yp)


def interpx(x: float, xp: Sequence[float], yp: Sequence[float]) -> float:
    """
    Interpolate x based on xp and yp using linear interpolation.

    Interpolate x based on xp and yp using linear interpolation with
    extrapolation.

    Parameters
    ----------
    x : float
        The value to interpolate.
    xp : Sequence of float
        The x-coordinates of the data points.
    yp : Sequence of float
        The y-coordinates of the data points.

    Returns
    -------
    float
        The interpolated value.
    """
    if x < xp[0]:
        return _interpv(x, xp[0], xp[1], yp[0], yp[1])

    if x > xp[-1]:
        return _interpv(x, xp[-2], xp[-1], yp[-2], yp[-1])

    return interp(x, xp, yp)
