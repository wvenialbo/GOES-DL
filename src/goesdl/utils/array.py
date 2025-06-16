from collections.abc import Sequence
from typing import Any

from numpy import (
    bool_,
    complex64,
    complex128,
    dtype,
    float16,
    float32,
    float64,
    floating,
    int8,
    int16,
    int32,
    int64,
    integer,
    uint8,
    uint16,
    uint32,
    uint64,
    unsignedinteger,
)
from numpy.ma import MaskedArray
from numpy.typing import NDArray

_Bool = bool_
_CoBool = _Bool
_ToBool = _Bool | bool

ToBool = _ToBool
ArrayBool = NDArray[_CoBool]
SequenceBool = ArrayBool | Sequence[_ToBool]

_Uint = unsignedinteger[Any]
_CoUint = _Uint
_ToUint = _Uint

ToUint = _ToUint
ArrayUint = NDArray[_CoUint]
SequenceUint = ArrayUint | Sequence[_ToUint]

ArrayUint8 = NDArray[uint8]
ArrayUint16 = NDArray[uint16]
ArrayUint32 = NDArray[uint32]
ArrayUint64 = NDArray[uint64]

_Int = integer[Any]
_CoInt = _Int | _CoUint
_ToInt = _Int | _ToUint | int

ToInt = _ToInt
ArrayInt = NDArray[_CoInt]
SequenceInt = ArrayInt | Sequence[_ToInt]

ArrayInt8 = NDArray[int8]
ArrayInt16 = NDArray[int16]
ArrayInt32 = NDArray[int32]
ArrayInt64 = NDArray[int64]

_Index = _Int | _Uint
_CoIndex = _Index
_ToIndex = _Index | int

ToIndex = _ToIndex
ArrayIndex = NDArray[_CoIndex]
ListIndex = list[_CoIndex] | list[int]
SequenceIndex = ArrayIndex | ListIndex

_Float = floating[Any]
_CoFloat = _Float | _CoInt
_ToFloat = _Float | _ToInt | float

CoFloat = _CoFloat
ToFloat = _ToFloat
ArrayFloat = NDArray[_CoFloat]
SequenceFloat = ArrayFloat | Sequence[_ToFloat]

ArrayFloat16 = NDArray[float16]
ArrayFloat32 = NDArray[float32]
ArrayFloat64 = NDArray[float64]
# ArrayFloat128 = NDArray[float128]

_Complex = complex64 | complex128  # | complex192 | complex256
_CoComplex = _Complex
_ToComplex = _Complex | complex

CoComplex = _CoComplex
ToComplex = _ToComplex
ArrayComplex = NDArray[_CoComplex]
SequenceComplex = ArrayComplex | Sequence[_ToComplex]

ArrayComplex64 = NDArray[complex64]
ArrayComplex128 = NDArray[complex128]
# ArrayComplex192 = NDArray[complex192]
# ArrayComplex256 = NDArray[complex256]

MaskedFloat32 = MaskedArray[Any, dtype[float32]]
MaskedFloat64 = MaskedArray[Any, dtype[float64]]
