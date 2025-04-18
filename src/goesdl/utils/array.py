from numpy import bool_, dtype, float32, float64, int8, ndarray
from numpy.ma import MaskedArray

ArrayBool = ndarray[tuple[int, ...], dtype[bool_]]
ArrayInt8 = ndarray[tuple[int, ...], dtype[int8]]
ArrayFloat32 = ndarray[tuple[int, ...], dtype[float32]]
ArrayFloat64 = ndarray[tuple[int, ...], dtype[float64]]

MaskedFloat32 = MaskedArray[tuple[int, ...], dtype[float32]]
