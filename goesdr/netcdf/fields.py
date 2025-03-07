from abc import ABC, abstractmethod
from collections.abc import Callable
from typing import Any

from netCDF4 import Dataset  # pylint: disable=no-name-in-module
from numpy import ndarray
from numpy.ma import MaskedArray
from numpy.typing import NDArray

ConvertFn = Callable[..., Any] | type
FilterFn = Callable[..., Any]


class ClassField:
    """
    Placeholder for class attribute fields.

    Mark attributes that will be copied from the given value to the
    instance without any conversion.

    Attributes
    ----------
    value : Any
        The value to be copied.

    See Also
    --------
    computed :
        Placeholder for computed attributes.
    field :
        Placeholder for instance attributes.
    ViewField :
        Abstract base class for dataset view field placeholders.
    """

    value: Any

    def __init__(self, value: Any) -> None:
        """
        Initialize the class field.

        Parameters
        ----------
        value : Any
            The value to be copied.
        """
        self.value = value


def computed() -> Any:
    """
    Placeholder for computed instance attributes.

    Mark attributes that will be computed during the record
    initialization in the __post_init__ method.

    Returns
    -------
    Any
        An instance of 'ClassField(None)'.

    Examples
    --------
    >>> class Record(DatasetView):
    ...     field1: int = field(42)
    ...     field2: int = computed()
    ...

    The 'field1' attribute will be copied from the given value, while
    the 'field2' attribute will be computed during the record
    initialization.

    See Also
    --------
    attribute :
        Placeholder for dataset view attribute fields.
    data :
        Placeholder for dataset view array data fields.
    dimension :
        Placeholder proxy for dataset view dimension fields.
    field :
        Placeholder for instance attributes.
    variable :
        Placeholder proxy for dataset view variable fields.
    """
    return ClassField(None)


def field(value: Any) -> Any:
    """
    Placeholder for instance attributes.

    Mark attributes that will be copied from the given value to the
    instance without any conversion.

    Parameters
    ----------
    value : Any
        The value to be copied.

    Returns
    -------
    Any
        An instance of 'ClassField(value)'.

    Examples
    --------
    >>> class Record(DatasetView):
    ...     field1: int = field(42)
    ...     field2: int = computed()
    ...

    The 'field1' attribute will be copied from the given value, while
    the 'field2' attribute will be computed during the record
    initialization.

    See Also
    --------
    attribute :
        Placeholder for dataset view attribute fields.
    computed :
        Placeholder for computed attributes.
    data :
        Placeholder for dataset view array data fields.
    dimension :
        Placeholder proxy for dataset view dimension fields.
    variable :
        Placeholder proxy for dataset view variable fields.
    """
    return ClassField(value)


class ViewField(ABC):
    """
    Abstract base class for dataset view field placeholders.

    Attributes
    ----------
    id : str | None
        The name of the field to be copied.
    entry : str | None
        The name of the field entry to be copied.
    convert : ConvertFn
        The conversion function to be applied to the field entry value.

    See Also
    --------
    AttributeField :
        Represent a placeholder for dataset view attribute fields.
    DataField :
        Represent a placeholder for dataset view array data fields.
    DimensionField :
        Represent a placeholder for dataset view dimension fields.
    VariableField :
        Represent a placeholder for dataset view variable fields.
    """

    id: str | None
    entry: str | None
    convert: ConvertFn

    def __init__(
        self,
        id: str | None,
        entry: str | None,
        convert: ConvertFn | None,
    ) -> None:
        """
        Initialize the view field.

        Parameters
        ----------
        id : str | None
            The name of the field to be copied.
        entry : str | None
            The name of the field entry to be copied.
        convert : ConvertFn | None
            The conversion function to be applied to the field entry
            value, default to the identity function.
        """
        self.id = id
        self.entry = entry

        def _identity(x: Any) -> Any:
            return x

        self.convert = convert or _identity

    @abstractmethod
    def __call__(self, dataset: Dataset) -> Any:
        """
        Copy the field entry value from the dataset.

        This method must be implemented by the subclasses to copy the
        field entry value from the dataset.

        Parameters
        ----------
        dataset : Dataset
            The dataset to copy the field entry value from.

        Returns
        -------
        Any
            The field entry value copied from the dataset.
        """

    def set_entry(self, entry: str) -> None:
        """
        Set the field entry name.

        This method is used to set the field entry name when it is not
        provided explicitly. It does not override the existing entry
        name.

        Parameters
        ----------
        entry : str
            The name of the field entry to be copied.
        """
        self.entry = self.entry or entry


class AttributeField(ViewField):
    """
    Represent a placeholder for dataset view attribute field.

    Mark attributes that will be copied from existing attributes in the
    dataset to the instance with some optional conversion.

    See Also
    --------
    attribute :
        Placeholder for dataset view attribute fields.
    DataField :
        Represent a placeholder for dataset view array data fields.
    DimensionField :
        Represent a placeholder for dataset view dimension fields.
    VariableField :
        Represent a placeholder for dataset view variable fields.
    ViewField :
        Abstract base class for dataset view field placeholders.
    """

    def __init__(self, entry: str | None, convert: ConvertFn | None) -> None:
        """
        Initialize the attribute field.

        Parameters
        ----------
        entry : str | None
            The name of the attribute to be copied.
        convert : ConvertFn | None
            The conversion function to be applied to the attribute
            value, default to the identity function.

        Returns
        -------
        Any
            An instance of 'AttributeField(entry, convert)'.

        Raises
        ------
        ValueError
            If the attribute name is not provided or unknown.
        """
        super().__init__(None, entry, convert)

    def __call__(self, dataset: Dataset) -> Any:
        if self.entry is None:
            raise ValueError("Attribute name is required")
        try:
            value_ = getattr(dataset, self.entry)
            return self.convert(value_)
        except AttributeError as error:
            raise ValueError(f"Unknown attribute '{self.entry}'") from error


def attribute(
    entry: str | None = None, *, convert: ConvertFn | None = None
) -> Any:
    """
    Placeholder for dataset view attribute field.

    Mark attributes that will be copied from existing attributes in the
    dataset to the instance with some optional conversion.

    Parameters
    ----------
    entry : str | None, optional
        The name of the attribute to be copied.
    convert : ConvertFn | None, optional
        The conversion function to be applied to the attribute value,
        default to the identity function.

    Returns
    -------
    Any
        An instance of 'AttributeField(entry, convert)'.

    Examples
    --------
    >>> class Record(DatasetView):
    ...     attr0: str = attribute()  # use ds.attr0
    ...     attribute1: int = attribute("attr1")  # use ds.attr0
    ...     attribute2: str = attribute("attr2", convert=str)  # use str(ds.attr2)
    ...

    See Also
    --------
    AttributeField :
        Represent a placeholder for dataset view attribute fields.
    computed :
        Placeholder for computed attributes.
    data :
        Placeholder for dataset view array data fields.
    dimension :
        Placeholder proxy for dataset view dimension fields.
    field :
        Placeholder for instance attributes.
    variable :
        Placeholder proxy for dataset view variable fields.
    """
    return AttributeField(entry, convert)


class DimensionField(ViewField):
    """
    Represent a placeholder for dataset view dimension fields.

    Mark attributes that will be copied from existing dimensions in the
    dataset to the instance with some optional conversion.

    See Also
    --------
    dimension :
        Placeholder proxy for dataset view dimension fields.
    AttributeField :
        Represent a placeholder for dataset view attribute fields.
    DataField :
        Represent a placeholder for dataset view array data fields.
    DimensionProxy :
        Proxy for dataset view dimension fields.
    VariableField :
        Represent a placeholder for dataset view variable fields.
    ViewField :
        Abstract base class for dataset view field placeholders.
    """

    def __init__(
        self, id: str | None, entry: str | None, convert: ConvertFn | None
    ) -> None:
        """
        Initialize the dimension field.

        Parameters
        ----------
        id : str | None
            The name of the dimension to be copied.
        entry : str | None
            The name of the dimension entry to be copied.
        convert : ConvertFn | None
            The conversion function to be applied to the dimension entry
            value, default to the identity function.
        """
        super().__init__(id, entry, convert)

    def __call__(self, dataset: Dataset) -> Any:
        if self.id is None:
            raise ValueError("Dimension id is required")
        if self.entry is None:
            raise ValueError("Dimension entry is required")
        return self._get_dimension(dataset, self.id, self.entry)

    def _get_dimension(self, dataset: Dataset, id: str, entry: str) -> Any:
        try:
            dimension_ = dataset.dimensions[id]
            value_ = getattr(dimension_, entry)
            return self.convert(value_)
        except IndexError as error:
            raise ValueError(f"Unknown dimension '{id}'") from error
        except AttributeError as error:
            raise ValueError(
                f"Unknown dimension entry '{id}:{entry}'"
            ) from error

    def set_entry(self, entry: str) -> None:
        """
        Set the dimension field name.

        This method is used to set the field entry name when it is not
        provided explicitly. It does not override the existing entry
        name.

        Parameters
        ----------
        entry : str
            The name of the dimension field to be copied.
        """
        self.id = self.id or entry


class DimensionProxy:
    """
    Proxy class for dataset view dimension fields.

    Attributes
    ----------
    id : str | None
        The name of the dimension to be copied.

    See Also
    --------
    dimension :
        Placeholder proxy for dataset view dimension fields.
    DimensionField :
        Represent a placeholder for dataset view dimension fields.
    """

    id: str | None = None

    def __init__(self, id: str | None) -> None:
        """
        Initialize the dimension proxy.

        Parameters
        ----------
        id : str | None
            The name of the dimension to be copied.
        """
        self.id = id

    def __call__(self, id: str) -> "DimensionProxy":
        return DimensionProxy(id)

    def name(self, *, convert: ConvertFn | None = None) -> Any:
        """
        Placeholder for dataset dimension name attribute.

        Parameters
        ----------
        convert : ConvertFn | None, optional
            The conversion function to be applied to the dimension name,
            default to the identity function.

        Returns
        -------
        Any
            An instance of 'DimensionField(id, "name", convert)'.
        """
        return DimensionField(self.id, "name", convert)

    def size(self, *, convert: ConvertFn | None = None) -> Any:
        """
        Placeholder for dataset dimension size attribute.

        Parameters
        ----------
        convert : ConvertFn | None, optional
            The conversion function to be applied to the dimension size,
            default to the identity function.

        Returns
        -------
        Any
            An instance of 'DimensionField(id, "size", convert)'.
        """
        return DimensionField(self.id, "size", convert)


dimension = DimensionProxy(None)
"""
Placeholder proxy for dataset view dimension fields.

Examples
--------
>>> class Record(DatasetView):
...     row: int = dimension.size()  # use ds.dimensions["row"].size
...     time_value: float = dimension("time").size(float)
...     time_name: str = dimension("time").name()
...

See Also
--------
attribute :
    Placeholder for dataset view attribute fields.
computed :
    Placeholder for computed attributes.
data :
    Placeholder for dataset view array data fields.
field :
    Placeholder for instance attributes.
variable :
    Placeholder proxy for dataset view variable fields.
DimensionField :
    Represent a placeholder for dataset view dimension fields.
DimensionProxy :
    Proxy for dataset view dimension fields.
"""


ARRAY_PREFIX = "array:"
ARRAY = "array:*"
DATA = "array:data"
NODATA = "array:fill_value"
MASK = "array:mask"


class VariableField(ViewField):
    """
    Represent a placeholder for dataset view variable fields.

    Mark attributes that will be copied from existing variables in the
    dataset to the instance with some optional filtering and conversion.

    Attributes
    ----------
    filter : FilterFn
        The filter function to be applied to the variable entry.

    See Also
    --------
    variable :
        Placeholder proxy for dataset view variable fields.
    VariableProxy :
        Proxy for dataset view variable fields.
    AttributeField :
        Represent a placeholder for dataset view attribute fields.
    DataField :
        Represent a placeholder for dataset view array data fields.
    DimensionField :
        Represent a placeholder for dataset view dimension fields.
    ViewField :
        Abstract base class for dataset view field placeholders.
    """

    filter: FilterFn

    def __init__(
        self,
        id: str | None,
        entry: str | None,
        filter: FilterFn | None,
        convert: ConvertFn | None,
    ) -> None:
        """
        Initialize the variable field.

        Parameters
        ----------
        id : str | None
            The name of the variable to be copied.
        entry : str | None
            The name of the variable entry to be copied.
        filter : FilterFn | None
            The filter function to be applied to the variable entry.
        convert : ConvertFn | None
            The conversion function to be applied to the
            variable entry value.
        """
        super().__init__(id, entry, convert)

        def _extract_all(x: Any) -> Any:
            return x[:]

        self.filter = filter or _extract_all

    def __call__(self, dataset: Dataset) -> Any:
        if self.id is None:
            raise ValueError("Variable id is required")
        if self.entry is None:
            raise ValueError("Variable entry is required")
        return self._get_variable(dataset, self.id, self.entry)

    def _extract_array(self, variable_: Any, entry: str) -> Any:
        array_value = self.filter(variable_)
        if not isinstance(array_value, ndarray):
            raise TypeError("Unsuported variable entry type")
        if isinstance(array_value, MaskedArray):
            if entry == DATA:
                return array_value.data
            if entry == MASK:
                return array_value.mask
            if entry == NODATA:
                return array_value.fill_value
        if entry == ARRAY:
            return array_value
        raise AttributeError("Unknown array entry")

    def _get_variable(self, dataset: Dataset, id: str, entry: str) -> Any:
        try:
            variable_ = dataset.variables[id]
            if entry.startswith(ARRAY_PREFIX):
                value_ = self._extract_array(variable_, entry)
            else:
                value_ = getattr(variable_, entry)
            return self.convert(value_)
        except IndexError as error:
            raise ValueError(f"Unknown variable '{id}'") from error
        except AttributeError as error:
            raise ValueError(
                f"Unknown variable entry '{id}:{entry}'"
            ) from error
        except TypeError as error:
            raise ValueError(
                f"Unexpected variable entry type '{id}:{entry}'"
            ) from error


class VariableProxy:
    """
    Proxy class for dataset view variable fields.

    Attributes
    ----------
    id : str
        The name of the variable to be copied.

    See Also
    --------
    variable :
        Placeholder proxy for dataset view variable fields.
    VariableField :
        Represent a placeholder for dataset view variable fields.
    """

    id: str

    def __init__(self, id: str) -> None:
        """
        Initialize the variable proxy.

        Parameters
        ----------
        id : str
            The name of the variable to be copied.
        """
        self.id = id

    def array(
        self,
        entry: str | None = None,
        *,
        filter: FilterFn | None = None,
        convert: ConvertFn | None = None,
    ) -> Any:
        """
        Placeholder for dataset view variable array field.

        Parameters
        ----------
        entry : str | None, optional
            The name of the variable entry to be copied, choose: 'data'
            (default), 'mask', or 'fill_value'.
        filter : FilterFn | None, optional
            The filter function to be applied to the variable entry.
        convert : ConvertFn | None, optional
            The conversion function to be applied to the variable entry
            value.

        Returns
        -------
        Any
            An instance of 'VariableField(id, entry, filter, convert)'.

        Raises
        ------
        ValueError
            If the entry is not valid or unknown.
        """
        if entry not in {"*", "data", "mask", "flll_value", None}:
            raise ValueError(
                "Invalid 'entry', choose: '*', 'data', 'mask', or 'fill_value'"
            )
        entry = f"array:{entry or "data"}"
        return VariableField(self.id, entry, filter, convert)

    def attribute(
        self, entry: str | None = None, *, convert: ConvertFn | None = None
    ) -> Any:
        """
        Placeholder for dataset view variable attribute field.

        Parameters
        ----------
        entry : str | None, optional
            The name of the attribute to be copied.
        convert : ConvertFn | None, optional
            The conversion function to be applied to the
            attribute value.

        Returns
        -------
        Any
            An instance of 'VariableField(id, entry, None, convert)'.
        """
        return VariableField(self.id, entry, None, convert)

    def scalar(self, *, convert: ConvertFn | None = None) -> Any:
        """
        Placeholder for dataset view variable scalar field.

        This effectively retrieves the first element of the variable
        array, by calling to 'indexed(0, "data", convert)'.

        Parameters
        ----------
        convert : ConvertFn | None, optional
            The conversion function to be applied to the variable value.

        Returns
        -------
        Any
            The instance of 'VariableField' returned by 'indexed(0,
            "data", convert)'.
        """
        return self.indexed(0, "data", convert=convert)

    def indexed(
        self,
        index: int,
        entry: str | None = None,
        *,
        convert: ConvertFn | None = None,
    ) -> Any:
        """
        Placeholder for dataset view variable indexed field.

        This effectively retrieves the first element of the variable
        array, by calling to 'array(entry, filter=*, convert=convert)'.

        Parameters
        ----------
        index : int
            The index of the variable array to be copied.
        entry : str | None, optional
            The name of the variable entry to be copied, choose: 'data'
            (default) or 'mask'.
        convert : ConvertFn | None, optional
            The conversion function to be applied to the variable entry
            value.

        Returns
        -------
        Any
            The instance of 'VariableField' returned by 'array(entry,
            filter=*, convert=convert)'.

        Raises
        ------
        ValueError
            If the entry is not valid or unknown.
        """
        if entry not in {"data", "mask", None}:
            raise ValueError("Invalid 'entry', choose: 'data' or 'mask'")

        def filter_(x: NDArray[Any]) -> Any:
            return x.ravel()[index]

        return self.array(entry, filter=filter_, convert=convert)


def variable(name: str) -> VariableProxy:
    """
    Placeholder proxy for dataset view variable fields.

    Parameters
    ----------
    name : str
        The name of the variable to be copied.

    Returns
    -------
    VariableProxy
        An instance of 'VariableProxy(name)'.

    Examples
    --------
    >>> image = variable("image")
    ...
    ... class Record(DatasetView):
    ...     image: NDArray[float32] = image.array()  # or image.array("data")
    ...     # retrieve ds.variables["image"][:].data
    ...
    ...     mask: NDArray[bool] = image.array()  # or image.array("mask")
    ...     # retrieve ds.variables["image"][:].data
    ...
    ...     fill_value: float32 = image.array("fill_value")
    ...     # retrieve ds.variables["image"][0:1,0:1].fill_value
    ...
    ...     thumb: NDArray[uint8] = image.array(
    ...         filter=lambda x: x[::4, ::4],
    ...         convert=lambda x: x.astype(uint8),
    ...     )
    ...     # retrieve ds.variables["image"][::4, ::4].data.astype(uint8)
    ...
    ...     long_name: str = image.attribute()  # or image.attribute("long_name")
    ...     # retrieve ds.variables["image"].long_name
    ...
    ...     rows: int = image.scalar()  # or image.scalar("rows")
    ...     # retrieve ds.variables["rows"][0].data
    ...

    See Also
    --------
    attribute :
        Placeholder for dataset view attribute fields.
    computed :
        Placeholder for computed attributes.
    data :
        Placeholder for dataset view array data fields.
    dimension :
        Placeholder proxy for dataset view dimension fields.
    field :
        Placeholder for instance attributes.
    VariableField :
        Represent a placeholder for dataset view variable fields.
    VariableProxy :
        Proxy for dataset view variable fields.
    """
    return VariableProxy(name)


class DataField(VariableField):
    """
    Represent a placeholder for dataset view array data fields.

    Mark attributes that will be copied from existing variables in the
    dataset to the instance with some optional filtering and conversion.

    See Also
    --------
    variable :
        Placeholder proxy for dataset view variable fields.
    VariableProxy :
        Proxy for dataset view variable fields.
    AttributeField :
        Represent a placeholder for dataset view attribute fields.
    DimensionField :
        Represent a placeholder for dataset view dimension fields.
    VariableField :
        Represent a placeholder for dataset view variable fields.
    ViewField :
        Abstract base class for dataset view field placeholders.
    """

    def __init__(
        self,
        id: str | None,
        filter: FilterFn | None,
        convert: ConvertFn | None,
    ) -> None:
        """
        Initialize the variable data field.

        Parameters
        ----------
        id : str | None
            The name of the variable to be copied.
        filter : FilterFn | None
            The filter function to be applied to the variable entry.
        convert : ConvertFn | None
            The conversion function to be applied to the
            variable entry value.
        """
        super().__init__(id, DATA, filter, convert)

    def set_entry(self, entry: str) -> None:
        """
        Set the variable field name.

        This method is used to set the field entry name when it is not
        provided explicitly. It does not override the existing entry
        name.

        Parameters
        ----------
        entry : str
            The name of the variable field to be copied.
        """
        self.id = self.id or entry


def data(
    id: str | None = None,
    *,
    filter: FilterFn | None = None,
    convert: ConvertFn | None = None,
) -> Any:
    """
    Placeholder for dataset view array data fields.

    Parameters
    ----------
    id : str | None, optional
        The name of the variable entry to be copied, choose: 'data'
        (default), 'mask', or 'fill_value'.
    filter : FilterFn | None, optional
        The filter function to be applied to the variable entry.
    convert : ConvertFn | None, optional
        The conversion function to be applied to the variable entry
        value.

    Returns
    -------
    Any
        An instance of 'DataField(id, filter, convert)'.

    See Also
    --------
    attribute :
        Placeholder for dataset view attribute fields.
    computed :
        Placeholder for computed attributes.
    dimension :
        Placeholder proxy for dataset view dimension fields.
    field :
        Placeholder for instance attributes.
    variable :
        Placeholder proxy for dataset view variable fields.
    DataField :
        Represent a placeholder for dataset view array data fields.
    """
    return DataField(id, filter, convert)
