"""
Provide utility functions for generating type hints.

Generate type hints for various collections and data types. The type
hints are generated as strings that can be used for type annotations in
Python code. Include special handling for NumPy arrays and homogeneous
collections.

Functions
---------
get_value_typehint(value: Any) -> str
    Generate a type hint for a given value.
"""

from collections.abc import Iterable, Sequence
from typing import Any

from numpy import dtype, ndarray


def _get_multitype_typehint(multitype: Iterable[Any], union: str) -> str:
    # Generate a type hint for a collection with multiple types.
    type_hints: set[str] = set()
    for element in multitype:
        type_hint = get_value_typehint(element)
        type_hints.add(type_hint)
    return union.join(type_hints)


def _get_iterable_typehint(iterable: Iterable[Any]) -> str:
    # Generate a type hint for an iterable collection.
    return _get_multitype_typehint(iterable, " | ") or "Any"


def _get_sequence_typehint(sequence: Sequence[Any]) -> str:
    # Generate a type hint for a sequence collection.
    return _get_multitype_typehint(sequence, ", ") or "Any, ..."


def _get_mixedtype_typehint(collection: Iterable[Any]) -> str:
    # Generate a type hint for a collection with mixed types.
    origin_type = type(collection).__name__
    type_hinter = (
        _get_sequence_typehint
        if isinstance(collection, tuple)
        else _get_iterable_typehint
    )
    arg_type_hint = type_hinter([*collection])
    return f"{origin_type}[{arg_type_hint}]" if arg_type_hint else origin_type


def _get_dict_typehint(dictionary: dict[Any, Any]) -> str:
    # Generate a type hint for a dictionary.
    keys = [*dictionary.keys()]
    values = [*dictionary.values()]
    keys_type_hint = _get_iterable_typehint(keys)
    vals_type_hint = _get_iterable_typehint(values)
    suffix = f"[{keys_type_hint}, {vals_type_hint}]"
    prefix = type(dictionary).__name__
    return f"{prefix}{suffix}"


def _get_ndarray_typehint(array: ndarray[tuple[int, ...], dtype[Any]]) -> str:
    # Generate a type hint for a NumPy ndarray.
    shape = "".join(f"Literal[{n}], " for n in array.shape[:-1])
    shape += f"Literal[{array.shape[-1]}]"
    suffix = f"[tuple[{shape}], dtype[{str(array.dtype)}]]"
    prefix = type(array).__name__  # str(type(array))[8:-2]
    return f"{prefix}{suffix}"


def _get_collection_typehint(collection: Iterable[Any]) -> str:
    # Generate a type hint for a generic collection.
    if isinstance(collection, dict):
        return _get_dict_typehint(collection)
    if isinstance(collection, ndarray):
        return _get_ndarray_typehint(collection)
    return _get_mixedtype_typehint(collection)


def get_value_typehint(value: Any) -> str:
    """
    Generate a type hint for a given value.

    Parameters
    ----------
    value : Any
        The value to generate a type hint for.

    Returns
    -------
    str
        The type hint for the given value.
    """
    # Generate a type hint for a given value.
    if isinstance(value, Iterable) and not isinstance(value, str):
        return _get_collection_typehint(value)
    return type(value).__name__
