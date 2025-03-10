"""
Provide utility functions for extracting type annotations.

Functions
---------
get_annotations(object_instance: Any, root: type) -> dict[str, type]
    Extract all type annotations from an object instance up to a
    specified root class.
"""

from typing import Any


def get_annotations(object_instance: Any, root: type) -> dict[str, type]:
    """
    Extract type annotations from an object's class.

    Extract all type annotations from an object instance class up to,
    but not including, a specified root class. The annotations are
    collected from the class hierarchy in the order of method
    resolution.

    Parameters
    ----------
    object_instance : Any
        An instance of a class.
    root : type
        The root class from which to extract annotations.

    Returns
    -------
    dict[str, type]
        A dictionary of attribute names and their corresponding types.
    """
    all_attributes: dict[str, type] = {}
    mro_classes = object_instance.__class__.__mro__
    for cls in mro_classes:
        if not issubclass(cls, root) or cls is root:
            continue
        all_attributes |= {
            key: value
            for key, value in cls.__annotations__.items()
            if key not in all_attributes
        }
    return all_attributes
