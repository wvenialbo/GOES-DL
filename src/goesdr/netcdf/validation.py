"""
Provide utility functions for type validation.

Validate a value against a provided type annotation. Include special
handling for NumPy arrays and homogeneous collections.

Functions
---------
validate_value_type(value: Any, annotation: type) -> bool
    Validate the type of a given value against a specified annotation.
"""

import re
from collections.abc import Iterable
from typing import Any, Literal, cast, get_args, get_origin

from numpy import dtype, ndarray


def _validate_ndarray_shape(
    shape: tuple[int, ...], annotation: type | Any
) -> bool:
    # Validate the shape of a NumPy ndarray against an annotation.
    origin = get_origin(annotation)

    if not origin:
        return annotation is Any

    if not issubclass(origin, tuple):
        return False

    specs = get_args(annotation)

    if specs == (int, ...):
        return True

    pattern = ""
    for type_ in specs:
        if type_origin := get_origin(type_):
            if type_origin is not Literal:
                return False
            size = str(get_args(type_)[0])
            if not size.isdigit():
                return False
            lpattern = [f"[{c}]" for c in size]
            pattern += f"{''.join(lpattern)},"
        elif type_ is Ellipsis:
            pattern += r"[\d,]+,"
        elif issubclass(type_, int):
            pattern += r"\d+,"
        else:
            return False

    pattern = pattern.strip(",")
    shape_string = str(shape).strip("(,)").replace(" ", "")

    print(pattern, shape_string)

    return bool(re.fullmatch(pattern, shape_string))


def _validate_ndarray(value: Any, annotation: type) -> bool:
    # Validate a NumPy ndarray against a specified annotation.

    # NOTE: We only expect arrays with scalar numeric content
    # in our project!

    if not isinstance(value, ndarray):
        return False

    # NOTE: According to NumPy's documentation, as of version
    # 2.1.0, the correct way to annotate an 'ndarray' is:
    #
    #        numpy.ndarray[shape, dtype].
    #
    # The 'NDArray' of the 'numpy.typing' module is defined as:
    #
    #  NDArray = numpy.ndarray[tuple[int, ...], dtype].
    #
    # Where 'dtype = numpy.dtype[scalar_type]', 'scalar_type'
    # can be any of 'numpy.int32', 'numpy.float32', etc.
    #
    # Shape typing has been added to NumPy. 'shape' types are
    # covariant and they must be 'tuple[int]', 'tuple[int, int]',
    # 'tuple[int, ...]', etc. 'Any' is accepted for backward
    # compatibility. This allows things like 'tuple[Literal[3]]'
    # to be valid shape type hinting. 'Any' can be used for
    # typing arrays with a given 'dtype' and unspecified shape.

    if dtype[value.dtype] != get_args(annotation)[1]:
        return False

    return _validate_ndarray_shape(value.shape, get_args(annotation)[0])


def validate_type(value: Any, annotation: type) -> bool:
    """
    Validate the type of a given value against a specified annotation.

    Validate the type of a given value against a specified annotation,
    including special handling for NumPy arrays and homogeneous
    collections.

    Parameters
    ----------
    value : Any
        The value to be validated.
    annotation : type
        The annotation to be validated against.

    Returns
    -------
    bool
        True if the value matches the annotation, False otherwise.
    """
    if isinstance(annotation, type(Any)):
        return True

    origin: type | None = get_origin(annotation)

    if not origin:
        return isinstance(value, annotation)

    if not isinstance(value, origin):
        return False

    if isinstance(value, ndarray):
        return _validate_ndarray(value, annotation)

    # NOTE: We only expect collections containing only
    # homogeneous scalar content in our project!
    # No nested structures are expected.

    # If it reached here, we are witnessing a sequence or
    # iterable (set or dictionary). We could collect the
    # types of each element and check if they match the
    # types in the annotation. However, depending on the
    # size of these collections, this would be excessive.
    # Therefore, we just ignore the content. The case of
    # an 'ndarray' is different, as it is homogeneous and
    # its dimensions and element type are annotated through
    # the 'shape' and 'dtype' attributes, respectively.

    arguments: tuple[type, ...] = get_args(annotation)

    if len(arguments) > 1 or get_origin(arguments[0]):
        return False

    # We know it is an iterable, so we can cast it.
    value = cast(Iterable[Any], value)

    return all(isinstance(item, arguments[0]) for item in value)
