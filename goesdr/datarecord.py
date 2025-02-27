from typing import Any, NoReturn

from netCDF4 import Dataset  # pylint: disable=no-name-in-module

from .annotations import get_annotations
from .class_help import help_str
from .fields import BaseField, ClassField
from .hinting import get_annotated, get_typehint
from .validation import validate_type


class DataRecord:

    def __init__(self, record: Dataset) -> None:
        self._validate_preconditions()
        self._init_class_attributes(record)
        self._init_record_attributes(record)
        self._init_field_attributes(record)
        self._validate_postconditions()

    def __delattr__(self, name: str) -> NoReturn:
        raise AttributeError(f"Cannot delete attribute '{name}'")

    def __setattr__(self, name: str, _: Any) -> NoReturn:
        # This can always be bypassed by calling object.__setattr__(),
        # but the goal is to prevent accidental assignment of attributes
        # to the instance not to guarantee immutability.
        raise AttributeError(f"Cannot set attribute '{name}'")

    def __str__(self) -> str:
        return help_str(self, DataRecord)

    def _init_class_attributes(self, record: Dataset) -> None:
        # Copy class attributes to the instance provided they are not
        # field attributes
        annotations = get_annotations(self, DataRecord)
        for name, annotation in annotations.items():
            if hasattr(self, name):
                value = getattr(self, name)
                if isinstance(value, BaseField):
                    continue
                if isinstance(value, ClassField):
                    value = value.value
                elif hasattr(record, name):
                    # This is a name clash, rename the attribute or
                    # explicitly make it a class field (ClassField).
                    atype = get_annotated(annotation)
                    raise AttributeError(
                        f"Attribute '{name}: {atype}' "
                        "collides with record attribute of the same name"
                    )
                object.__setattr__(self, name, value)

    def _init_record_attributes(self, record: Dataset) -> None:
        # Copy record attributes to the instance
        annotations = get_annotations(self, DataRecord)
        for name, annotation in annotations.items():
            if hasattr(self, name):
                continue
            if not hasattr(record, name):
                atype = get_annotated(annotation)
                raise AttributeError(
                    f"Attribute '{name}: {atype}' is undefined"
                )
            value = getattr(record, name)
            object.__setattr__(self, name, value)

    def _init_field_attributes(self, record: Dataset) -> None:
        # Copy record field attributes to the instance, do not overwrite
        # existing instance attributes
        for name in get_annotations(self, DataRecord):
            value = getattr(self, name)
            if not isinstance(value, BaseField):
                continue
            object.__setattr__(self, name, value(record, name))

    def _validate_preconditions(self) -> None:
        if self.__dict__:
            raise TypeError(f"Datarecord {self.__class__.__name__} is corrupt")

    def _validate_postconditions(self) -> None:
        all_annotations = get_annotations(self, DataRecord)
        for name, annotation in all_annotations.items():
            value = getattr(self, name)
            if validate_type(value, annotation):
                continue
            vtype = get_typehint(value)
            atype = get_annotated(annotation)
            raise TypeError(
                f"Attribute '{name}: {atype}' "
                f"does not match the given type '{vtype}'"
            )
