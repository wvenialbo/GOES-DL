import inspect
from typing import TypeVar, cast

from .datarecord import DataFragment

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

    original_module = inspect.getmodule(recordclass)
    setattr(original_module, recordclass.__name__, _FragmentRecord)

    return cast(type[_T], _FragmentRecord)
