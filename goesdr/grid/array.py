from numpy import (
    dtype,
    float32,
    float64,
    ndarray,
)

ArrayFloat32 = ndarray[tuple[int, ...], dtype[float32]]
ArrayFloat64 = ndarray[tuple[int, ...], dtype[float64]]
