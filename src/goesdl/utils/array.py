from numpy import (
    bool_,
    dtype,
    float32,
    float64,
    int8,
    int16,
    int32,
    ndarray,
    uint16,
    uint32,
)
from numpy.ma import MaskedArray

ArrayBool = ndarray[tuple[int, ...], dtype[bool_]]
ArrayInt8 = ndarray[tuple[int, ...], dtype[int8]]
ArrayInt16 = ndarray[tuple[int, ...], dtype[int16]]
ArrayInt32 = ndarray[tuple[int, ...], dtype[int32]]
ArrayUint16 = ndarray[tuple[int, ...], dtype[uint16]]
ArrayUint32 = ndarray[tuple[int, ...], dtype[uint32]]
ArrayFloat32 = ndarray[tuple[int, ...], dtype[float32]]
ArrayFloat64 = ndarray[tuple[int, ...], dtype[float64]]

MaskedFloat32 = MaskedArray[tuple[int, ...], dtype[float32]]
