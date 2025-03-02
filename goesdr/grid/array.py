from numpy import (
    dtype,
    float32,
    float64,
    ndarray,
)
from numpy.ma import MaskedArray

ArrayFloat32 = ndarray[tuple[int, ...], dtype[float32]]
ArrayFloat64 = ndarray[tuple[int, ...], dtype[float64]]

MaskedFloat32 = MaskedArray[tuple[int, ...], dtype[float32]]
