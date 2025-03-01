"""
Utilities for generating string representation of classes.

Provide helper functions for generating string representations of class
instances and their attributes, particularly for classes that inherit
from a specified root class. It includes functions to retrieve attribute
names, format attribute values, and handle NumPy arrays.

Functions:
    help_str(this: Any, root: type, indent: str = "    ") -> str:
        Generate a formatted string representation of an instance,
        including its class name and attribute values, with indentation
        for readability.
"""

from typing import Any

from numpy import float32, ndarray
from numpy.typing import NDArray


def _get_attribute_names(this: Any, root: type) -> list[str]:
    # Retrieve a list of attribute names for a given instance and its
    # superclasses up to a specified root class.
    all_attributes: list[str] = list(this.__dict__.keys())
    mro_classes = this.__class__.__mro__
    for cls in mro_classes:
        if issubclass(cls, root) and cls != root:
            all_attributes.extend(
                [
                    key
                    for key in cls.__annotations__.keys()
                    if key not in all_attributes
                ]
            )
    return all_attributes


def _get_attribute_value(attribute_value: Any, root: type, indent: str) -> str:
    # Format the value of an attribute as a string, handling special
    # cases such as None, NumPy arrays, floats, strings, booleans, and
    # instances of the root class.
    if attribute_value is None:
        return "'not available'"
    if isinstance(attribute_value, ndarray):
        return _str_ndarray(attribute_value)
    if isinstance(attribute_value, float):
        return f"{attribute_value:.6f}"
    if isinstance(attribute_value, str):
        return f"'{attribute_value}'"
    if isinstance(attribute_value, bool):
        return f"{attribute_value}".lower()
    if isinstance(attribute_value, root):
        return help_str(attribute_value, root, f"{indent}    ")
    return str(attribute_value)


def _str_ndarray(array: NDArray[float32]) -> str:
    # Generates a string representation of a NumPy array, including its
    # shape and data type. Returns a string representation of a NumPy
    # array, including its type, shape, and data type.
    shape: str = f"({array.size})" if array.ndim == 1 else f"{array.shape}"
    dtype = f"{array.dtype}"
    value = f"{type(array)}, shape={shape}, dtype={dtype}>"
    return value.replace(">,", ",")


def help_str(this: Any, root: type = object, indent: str = "    ") -> str:
    """
    Generate a formatted string representation of an instance.

    Generate a formatted string representation of an instance, including
    its class name and attribute values, with indentation for
    readability.

    Parameters
    ----------
    this : Any
        An instance of a class.
    root : type
        The root class from which to extract attributes.
    indent : str, optional
        The indentation string, by default four spaces.

    Returns
    -------
    str
        A formatted string representation of the instance.
    """
    attributes = [str(this.__class__)]
    all_attributes = _get_attribute_names(this, root)
    for attribute_name in all_attributes:
        attribute_value = getattr(this, attribute_name, None)
        attribute_value = _get_attribute_value(attribute_value, root, indent)
        attributes.append(f"{indent}{attribute_name}: {attribute_value}")
    for attribute_name in dir(this.__class__):
        attribute_value = getattr(this.__class__, attribute_name)
        if isinstance(attribute_value, property):
            attribute_value = getattr(this, attribute_name, None)
            attribute_value = _get_attribute_value(
                attribute_value, root, indent
            )
            attributes.append(f"{indent}{attribute_name}: {attribute_value}")
    return "\n".join(attributes)
