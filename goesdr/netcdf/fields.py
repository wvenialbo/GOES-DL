from abc import ABC, abstractmethod
from collections.abc import Callable
from typing import Any, cast

from netCDF4 import Dataset, Variable  # pylint: disable=no-name-in-module
from numpy import int32, ndarray
from numpy.ma import MaskedArray
from numpy.typing import NDArray


class BaseField(ABC):

    entry: str | None
    record: str | None
    convert: Callable[..., Any]

    def __init__(
        self,
        record_name: str | None,
        entry: str | None,
        convert: Callable[..., Any] | None,
    ) -> None:
        self.record = record_name
        self.entry = entry

        def _identity(x: Any) -> Any:
            return x

        self.convert = convert or _identity

    @abstractmethod
    def __call__(self, dataset: Dataset, name: str) -> Any:
        pass


class ClassField:

    value: Any

    def __init__(self, value: Any) -> None:
        self.value = value


DIMENSION_ENTRY_NAME = "name"
DIMENSION_ENTRY_SIZE = "size"


class DimensionField(BaseField):

    def __call__(self, dataset: Dataset, name: str) -> Any:
        alias = self.record or name
        if alias not in dataset.dimensions:
            raise ValueError(f"Unknown dimension '{alias}'")
        dimension_ = dataset.dimensions[alias]
        if self.entry is None:
            return self.convert(dimension_)
        try:
            value_ = getattr(dimension_, self.entry)
            return self.convert(value_)
        except AttributeError as error:
            raise ValueError(
                f"Unknown dimension entry '{alias}:{self.entry}'"
            ) from error


class RecordField(BaseField):

    def __init__(
        self,
        record_name: str | None,
        convert: Callable[..., Any] | None,
    ) -> None:
        super().__init__(record_name, None, convert)

    def __call__(self, dataset: Dataset, name: str) -> Any:
        alias = self.record or name
        if not hasattr(dataset, alias):
            raise ValueError(f"Unknown record field '{name}'")
        value_ = getattr(dataset, alias)
        return self.convert(value_)


VARIABLE_ARRAY_PREFIX = "array:"
VARIABLE_ENTRY_ARRAY = "array:*"
VARIABLE_ENTRY_DATA = "array:data"
VARIABLE_ENTRY_FILL_VALUE = "array:fill_value"
VARIABLE_ENTRY_MASK = "array:mask"


class BaseVariableField(BaseField):

    step: tuple[int, int] | None

    def __init__(
        self,
        record_name: str | None,
        entry: str | None,
        step: tuple[int, int] | None,
        convert: Callable[..., Any] | None,
    ) -> None:
        super().__init__(record_name, entry, convert)
        self.step = step

    def _extract_array(
        self, variable_: Any, alias: str, step: tuple[int, int] | None
    ) -> Any:
        array_value = (
            variable_[:: step[0], :: step[1]] if step else variable_[:]
        )
        if not isinstance(array_value, (MaskedArray, ndarray)):
            raise TypeError("Unsuported variable entry type")
        if isinstance(array_value, MaskedArray):
            if alias == VARIABLE_ENTRY_DATA:
                return array_value.data
            if alias == VARIABLE_ENTRY_MASK:
                return array_value.mask
            if alias == VARIABLE_ENTRY_FILL_VALUE:
                return array_value.fill_value
        if alias == VARIABLE_ENTRY_ARRAY:
            return array_value
        raise AttributeError("Unknown array entry")

    def _get_variable(
        self,
        dataset: Dataset,
        alias: str,
        entry: str | None,
        step: tuple[int, int] | None,
    ) -> Any:
        if alias not in dataset.variables:
            raise ValueError(f"Unknown variable '{alias}'")
        variable_: Variable[Any] = dataset.variables[alias]
        if entry is None:
            return self.convert(variable_)
        try:
            if entry.startswith(VARIABLE_ARRAY_PREFIX):
                value_ = self._extract_array(variable_, entry, step)
            else:
                value_ = getattr(variable_, entry)
            return self.convert(value_)
        except AttributeError as error:
            raise ValueError(
                f"Unknown variable entry '{alias}:{entry}'"
            ) from error
        except TypeError as error:
            raise ValueError(
                f"Unexpected variable entry type '{alias}:{entry}'"
            ) from error


class VariableField(BaseVariableField):

    def __call__(self, dataset: Dataset, name: str) -> Any:
        alias = self.record or name
        return self._get_variable(dataset, alias, self.entry, self.step)


class BaseNamedVariableField(BaseVariableField):

    def __init__(
        self,
        record_name: str,
        entry: str | None,
        step: tuple[int, int] | None,
        convert: Callable[..., Any] | None,
    ) -> None:
        super().__init__(record_name, entry, step, convert)


class NamedVariableField(BaseNamedVariableField):

    def __call__(self, dataset: Dataset, name: str) -> Any:
        if self.record is None:
            raise ValueError("Named variable field requires a record name")
        entry = self.entry or name
        return self._get_variable(dataset, self.record, entry, self.step)


class NamedArrayVariableField(BaseNamedVariableField):

    def __call__(self, dataset: Dataset, name: str) -> Any:
        if self.record is None:
            raise ValueError("Named variable field requires a record name")
        if name in {"data", "mask", "fill_value"}:
            name = f"array:{name}"
        entry = self.entry or name
        return self._get_variable(dataset, self.record, entry, self.step)


class IndexedVariableField(BaseVariableField):

    index: int

    def __init__(
        self,
        record_name: str | None,
        index: int,
        entry: str | None,
        step: tuple[int, int] | None,
    ) -> None:
        super().__init__(record_name, entry, step, None)
        self.index = index

    def __call__(self, dataset: Dataset, name: str) -> Any:
        alias = self.record or name
        if self.entry not in {"array:data", "array:mask"}:
            raise ValueError(
                "Indexed variable field requires a data or mask entry"
            )
        value: NDArray[int32] = self._get_variable(
            dataset, alias, self.entry, self.step
        )
        return value.ravel()[self.index]


class VariableType(ABC):

    @abstractmethod
    def __call__(
        self,
        *,
        entry: str | None = None,
        step: tuple[int, int] | None = None,
        convert: Callable[..., Any] | None = None,
    ) -> Any:
        pass


ARRAY = VARIABLE_ENTRY_ARRAY
DATA = VARIABLE_ENTRY_DATA
FILL = VARIABLE_ENTRY_FILL_VALUE
MASK = VARIABLE_ENTRY_MASK
SIZE = DIMENSION_ENTRY_SIZE


def computed() -> Any:
    """
    Placeholder for computed fields.

    Mark attributes that will be computed during the record
    initialization in the __post_init__ method.

    Returns
    -------
    Any
        Placeholder for computed fields, 'ClassField(None)'.
    """
    return ClassField(None)


def dimension(
    record_name: str | None = None,
    *,
    entry: str | None = SIZE,
    convert: Callable[..., Any] | None = None,
) -> Any:
    return DimensionField(record_name, entry, convert)


def field(value: Any) -> Any:
    """
    Placeholder for field attributes.

    Mark attributes that will be copied from the given value to the
    instance without any conversion.

    Parameters
    ----------
    value : Any
        The value to be copied.

    Returns
    -------
    Any
        Placeholder for field attributes, 'ClassField(value)'.
    """
    return ClassField(value)


def indexed(
    record_name: str | None = None,
    *,
    index: int,
    entry: str | None = DATA,
    step: tuple[int, int] | None = None,
) -> Any:
    return IndexedVariableField(record_name, index, entry, step)


def record(
    record_name: str | None = None,
    *,
    convert: Callable[..., Any] | None = None,
) -> Any:
    return RecordField(record_name, convert)


def scalar(
    record_name: str | None = None,
    *,
    entry: str | None = DATA,
) -> Any:
    return IndexedVariableField(record_name, 0, entry, None)


def variable(
    record_name: str | None = None,
    *,
    entry: str | None = DATA,
    step: tuple[int, int] | None = None,
    convert: Callable[..., Any] | None = None,
) -> Any:
    return VariableField(record_name, entry, step, convert)


def make_variable(record_name: str, *, array: bool = False) -> VariableType:
    def _variable(
        *,
        entry: str | None = None,
        step: tuple[int, int] | None = None,
        convert: Callable[..., Any] | None = None,
    ) -> Any:
        return (
            NamedArrayVariableField(record_name, entry, step, convert)
            if array
            else NamedVariableField(record_name, entry, step, convert)
        )

    return cast(VariableType, _variable)
