"""
Provide a base class for data records extracted from netCDF datasets.

Defines the DataFragment class, which represents a data record extracted
from a netCDF dataset. The class provides methods for initializing
attributes from the dataset, validating preconditions and
postconditions, and preventing accidental modification of attributes.

Classes
-------
DataFragment
    Represents a data record extracted from a netCDF dataset.
"""

from inspect import currentframe, getmodule
from typing import Any, NoReturn, TypeVar, cast

from netCDF4 import Dataset  # pylint: disable=no-name-in-module

from .annotations import get_annotations
from .class_help import help_str
from .fields import BaseField, ClassField
from .hinting import get_annotated, get_typehint
from .validation import validate_type


class DataFragment:
    """
    Represent a data fragment extracted from a netCDF dataset.

    Attributes are dynamically set based on the annotations and field
    specifications defined in the class and the corresponding records
    present in the provided netCDF dataset.
    """

    def __init__(self, record: Dataset) -> None:
        """
        Initialize the DataFragment object.

        Use annotations and field specification to initialize the
        DataFragment object with the provided netCDF dataset.

        Parameters
        ----------
        record : Dataset
            The netCDF dataset containing the data to be extracted.
        """
        self._validate_preconditions()
        self._init_class_attributes(record)
        self._init_record_attributes(record)
        self._init_field_attributes(record)
        self._perform_post_init_setup(record)
        self._validate_postconditions()

    def __post_init__(self, record: Dataset) -> None:
        """
        Perform post-initialization setup.

        This method is called after the initialization of the DataFragment
        object. It can be overridden by subclasses to perform additional
        setup tasks.
        """

    def _perform_post_init_setup(self, record: Dataset) -> None:
        self.__post_init__(record)

    def __delattr__(self, name: str) -> NoReturn:
        # Prevents deletion of attributes.
        raise AttributeError(f"Cannot delete attribute '{name}'")

    def __setattr__(self, name: str, value: Any) -> None:
        # Prevents setting of attributes outside of the __post_init__
        # method. Note tha this can always be bypassed by calling
        # object.__setattr__, but the goal is to prevent accidental
        # assignment of attributes to the instance not to guarantee
        # immutability.
        current = currentframe()
        frame = current.f_back if current else None
        while frame:
            if (
                frame.f_code.co_name == "__post_init__"
                and frame.f_locals.get("self") is self
            ):
                object.__setattr__(self, name, value)
                return
            frame = frame.f_back
        raise AttributeError(f"Cannot set attribute '{name}'")

    def __str__(self) -> str:
        # Returns a string representation of the DataFragment object.
        return help_str(self, DataFragment)

    def _init_class_attributes(self, record: Dataset) -> None:
        # Initializes class attributes from the provided dataset. Copy
        # class attributes to the instance provided they are not field
        # attributes.
        annotations = get_annotations(self, DataFragment)
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
        # Initializes record attributes from the provided dataset. Copy
        # record attributes to the instance.
        annotations = get_annotations(self, DataFragment)
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
        # Initializes field attributes from the provided dataset. Copy
        # record field attributes to the instance, convert the data if
        # necessary.
        for name in get_annotations(self, DataFragment):
            value = getattr(self, name)
            if not isinstance(value, BaseField):
                continue
            object.__setattr__(self, name, value(record, name))

    def _validate_preconditions(self) -> None:
        # Validates preconditions before initialization.
        if self.__dict__:
            raise TypeError(f"Datarecord {self.__class__.__name__} is corrupt")

    def _validate_postconditions(self) -> None:
        # Validates postconditions after initialization.
        all_annotations = get_annotations(self, DataFragment)
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


_T = TypeVar("_T")


def netcdf_fragment(recordclass: type[_T]) -> type[_T]:
    class _FragmentRecord(DataFragment):
        pass

    _FragmentRecord.__annotations__ = recordclass.__annotations__.copy()
    _FragmentRecord.__module__ = recordclass.__module__
    _FragmentRecord.__name__ = recordclass.__name__
    _FragmentRecord.__qualname__ = recordclass.__qualname__

    for name in recordclass.__annotations__:
        if hasattr(recordclass, name):
            value = getattr(recordclass, name)
            setattr(_FragmentRecord, name, value)

    __post_init__ = getattr(recordclass, "__post_init__", None)
    if callable(__post_init__):
        setattr(_FragmentRecord, "__post_init__", __post_init__)

    original_module = getmodule(recordclass)
    setattr(original_module, recordclass.__name__, _FragmentRecord)

    return cast(type[_T], _FragmentRecord)
