from numpy import (
    bool_,
    complex128,
    dtype,
    float32,
    float64,
    int8,
    int16,
    int32,
    int64,
    ndarray,
    uint8,
    uint16,
    uint32,
    uint64,
)
from numpy.ma import MaskedArray

ArrayBool = ndarray[tuple[int, ...], dtype[bool_]]
ArrayInt8 = ndarray[tuple[int, ...], dtype[int8]]
ArrayInt16 = ndarray[tuple[int, ...], dtype[int16]]
ArrayInt32 = ndarray[tuple[int, ...], dtype[int32]]
ArrayInt64 = ndarray[tuple[int, ...], dtype[int64]]
ArrayUint8 = ndarray[tuple[int, ...], dtype[uint8]]
ArrayUint16 = ndarray[tuple[int, ...], dtype[uint16]]
ArrayUint32 = ndarray[tuple[int, ...], dtype[uint32]]
ArrayUint64 = ndarray[tuple[int, ...], dtype[uint64]]
ArrayFloat32 = ndarray[tuple[int, ...], dtype[float32]]
ArrayFloat64 = ndarray[tuple[int, ...], dtype[float64]]
ArrayComplex128 = ndarray[tuple[int, ...], dtype[complex128]]

MaskedFloat32 = MaskedArray[tuple[int, ...], dtype[float32]]
