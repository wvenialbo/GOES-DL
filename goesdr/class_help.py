from typing import Any

from numpy import float32, ndarray
from numpy.typing import NDArray


def _get_attribute_names(this: Any, root: type) -> list[str]:
    all_attributes: list[str] = []
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
    shape: str = f"({array.size})" if array.ndim == 1 else f"{array.shape}"
    dtype = f"{array.dtype}"
    value = f"{type(array)}, shape={shape}, dtype={dtype}>"
    return value.replace(">,", ",")


def help_str(this: Any, root: type, indent: str = "    ") -> str:
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
