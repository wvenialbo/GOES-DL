from typing import Any


def get_annotations(object_instance: Any, root: type) -> dict[str, type]:
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
