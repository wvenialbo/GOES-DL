from collections.abc import Iterator
from math import nan
from pathlib import Path
from types import UnionType
from typing import (
    Any,
    Protocol,
    TypeVar,
    cast,
    get_args,
    get_origin,
    runtime_checkable,
)

_T = TypeVar("_T")

_Settings = dict[str, Any]


_U = TypeVar("_U", contravariant=True)
_V = TypeVar("_V", covariant=True)


@runtime_checkable
class CastableToType(Protocol[_U, _V]):
    """
    A protocol for type objects (like int, str, float) that are callable
    with one argument of type _InputT and return an instance of type T.
    """

    def __call__(self, __arg: _U) -> _V: ...


class ConfigDict:
    """
    A class to load configuration from a YAML file and access values
    using dot-separated string keys.
    """

    type Settings = _Settings

    _config_data: _Settings

    def __init__(self, config_data: Any) -> None:
        """
        Initializes the YamlConfig object by loading the YAML file.

        Parameters
        ----------
        config_data : Any
            Dictionary containing configuration valuess.
        """

        if not isinstance(config_data, dict):
            raise TypeError("Invalid configuration data")

        self._config_data = config_data

    def __contains__(self, key_path: str) -> bool:
        """
        Allows checking for the existence of a key path using the 'in' operator.

        Parameters
        ----------
        key_path : str
            A dot-separated string representing the path to check (e.g., "section.subsection.value").

        Returns
        -------
        bool
            True if the key path exists and is traversable, False otherwise.
        """
        keys = key_path.split(".")
        current_data: Any = self._config_data

        for key in keys:
            if isinstance(current_data, dict) and key in current_data:
                current_section = cast(_Settings, current_data)
                current_data = current_section[key]
            else:
                return False

        return True

    def __getitem__(self, key_path: str) -> Any:
        """
        Allows accessing configuration values using dictionary-like
        syntax with dot-separated keys.

        Parameters
        ----------
        key_path : str
            A dot-separated string representing the path to the desired
            configuration value (e.g., "section.subsection.value").

        Returns
        -------
        Any
            The value found at the specified key path.

        Raises
        ------
        KeyError
            If any part of the key path does not exist.
        TypeError
            If an intermediate part of the path is not a dictionary.
        """
        keys = key_path.split(".")
        current_data: Any = self._config_data

        for i, key in enumerate(keys):
            if not isinstance(current_data, dict):
                raise TypeError(
                    f"Intermediate key '{'.'.join(keys[:i])}' "
                    f"is not a section. Cannot access '{key}'."
                )
            current_section = cast(_Settings, current_data)
            if key in current_section:
                current_data = current_section[key]
            else:
                raise KeyError(
                    f"Key '{key}' not found in "
                    f"path '{'.'.join(keys[:i+1])}'"
                )

        return current_data

    def __iter__(self) -> Iterator[str]:
        """
        Returns an iterator over the top-level keys of the configuration.
        """
        return iter(self._config_data)

    def __len__(self) -> int:
        """
        Returns the number of top-level keys in the configuration.
        """
        return len(self._config_data)

    def __setitem__(self, key_path: str, value: Any) -> None:
        """
        Allows setting configuration values using dictionary-like syntax
        with dot-separated keys. Creates intermediate dictionaries if they
        do not exist along the path.

        Parameters
        ----------
        key_path : str
            A dot-separated string representing the path to the configuration
            value to set (e.g., "section.subsection.value").
        value : Any
            The value to set at the specified key path.

        Raises
        ------
        TypeError
            If an intermediate part of the path exists but is not a dictionary.
        """
        keys = key_path.split(".")
        current_data: Any = self._config_data

        # Traverse all keys except the last one
        for i, key in enumerate(keys[:-1]):
            if not isinstance(current_data, dict):
                raise TypeError(
                    f"Intermediate key '{'.'.join(keys[:i])}' "
                    f"is not a section. Cannot set '{key}'"
                )

            current_section = cast(_Settings, current_data)

            if key not in current_section:
                current_section[key] = {}
            elif not isinstance(current_section[key], dict):
                raise TypeError(
                    f"Intermediate key '{'.'.join(keys[:i+1])}' "
                    "exists but is not a section"
                )

            current_data = current_section[key]

        # Set the value at the last key
        final_key = keys[-1]

        if not isinstance(current_data, dict):
            raise TypeError(
                f"Intermediate key '{'.'.join(keys[:-1])}' "
                f"is not a section. Cannot set '{final_key}'"
            )

        current_data[final_key] = value

    def as_bool(self, key_path: str, default: bool | None = None) -> bool:
        return bool(self.get(key_path, default))

    def as_float(self, key_path: str, default: float = nan) -> float:
        return float(self.get(key_path, default))

    def as_int(self, key_path: str, default: int | None = None) -> int:
        return int(self.get(key_path, default))

    def as_path(self, key_path: str, default: Path | None = None) -> Path:
        return Path(self.get(key_path, default))

    def as_str(self, key_path: str, default: str = "N/A") -> str:
        return str(self.get(key_path, default))

    def astype(self, key_path: str, expected_type: type[_T]) -> _T:
        value = self.__getitem__(key_path)
        if isinstance(value, expected_type):
            return value
        converter = cast(CastableToType[Any, _T], expected_type)
        return converter(value)

    def get(self, key_path: str, default: Any | None = None) -> Any:
        """
        Retrieves a configuration value using a dot-separated string key,
        with an optional default value if the key is not found.

        Parameters
        ----------
        key_path : str
            A dot-separated string representing the path to the desired configuration value.
        default : any, optional
            The value to return if the key path is not found. Defaults to None.

        Returns
        -------
        any
            The value found at the specified key path, or the default value if the
            key path is not found.
        """
        try:
            return self.__getitem__(key_path)
        except (KeyError, TypeError):
            return default

    def get_astype(self, key_path: str, expected_type: type[_T]) -> _T:
        """
        Retrieves a configuration value and attempts to cast it to the
        specified type.  Raises an error if the key is not found or if
        the type conversion fails.

        This version uses standard Python type casting and does not
        include special string-to-boolean conversions beyond Python's
        default behavior.

        Parameters
        ----------
        key_path : str
            A dot-separated string representing the path to the desired
            configuration value.
        expected_type : type[T]
            The target Python type to cast the retrieved value to (e.g.,
            int, str, bool, float).  The return type of this method will
            be inferred as T.

        Returns
        -------
        T
            The value found at the specified key path, cast to the
            expected type.

        Raises
        ------
        KeyError
            If any part of the key path does not exist.
        TypeError
            If an intermediate part of the path is not a dictionary, or
            if the retrieved value cannot be converted to the
            `expected_type`.
        ValueError
            If the retrieved value exists but cannot be meaningfully
            converted to the `expected_type` (e.g., trying to convert
            "hello" to an int).
        """
        value = self.__getitem__(key_path)

        self._astype_check(key_path, expected_type, value)

        return cast(_T, value)

    def get_like(self, key_path: str, default: _T) -> _T:
        """
        Retrieves a configuration value using a dot-separated string key,
        with an optional default value if the key is not found.

        Parameters
        ----------
        key_path : str
            A dot-separated string representing the path to the desired configuration value.
        default : any, optional
            The value to return if the key path is not found. Defaults to None.

        Returns
        -------
        any
            The value found at the specified key path, or the default value if the
            key path is not found.
        """
        try:
            return self.astype(key_path, type(default))
        except (KeyError, TypeError):
            return default

    def items(self) -> Iterator[tuple[str, Any]]:
        """
        Returns an iterator over the top-level key-value pairs of the configuration.
        """
        return iter(self._config_data.items())

    def keys(self) -> Iterator[str]:
        """
        Returns an iterator over the top-level keys of the configuration.
        """
        return iter(self._config_data.keys())

    @classmethod
    def load(cls, settings_filepath: Path | str) -> "ConfigDict":
        """
        Initializes the YamlConfig object by loading the YAML file.

        Parameters
        ----------
        yaml_filepath : Path or str
            The path to the YAML configuration file.
        """
        _config_data = cls._load_file(settings_filepath)

        if not isinstance(_config_data, dict):
            raise TypeError(
                f"Invalid configuration file '{settings_filepath}'"
            )

        return cls(_config_data)

    def section(self, key_path: str, create: bool = False) -> "ConfigDict":
        try:
            section_data = self.__getitem__(key_path)
        except KeyError as error:
            if create:
                self.__setitem__(key_path, {})
                return self.section(key_path)
            raise error

        if not isinstance(section_data, dict):
            raise TypeError(f"Key '{key_path}' is not a section")

        return ConfigDict(section_data)

    def to_dict(self) -> _Settings:
        """
        Returns the entire configuration as a dictionary.
        """
        return self._config_data

    def update(self, config: "ConfigDict | _Settings") -> None:
        config_data = (
            config.to_dict() if isinstance(config, ConfigDict) else config
        )
        self._config_data |= config_data

    def values(self) -> Iterator[Any]:
        """
        Returns an iterator over the top-level values of the configuration.
        """
        return iter(self._config_data.values())

    @staticmethod
    def _astype_check(key_path: str, expected_type: type, value: Any) -> None:
        runtime_expected_type: type | tuple[type, ...]

        origin = get_origin(expected_type)

        if origin is UnionType:
            runtime_expected_type = tuple(
                arg for arg in get_args(expected_type) if isinstance(arg, type)
            )
            if not runtime_expected_type:
                raise TypeError(
                    f"Union type {expected_type} contains no valid "
                    "concrete types for runtime check."
                )
        elif origin is not None:
            runtime_expected_type = origin
        else:
            runtime_expected_type = expected_type

        if not isinstance(value, runtime_expected_type):
            expected_type_display = str(expected_type)
            if origin is UnionType:
                union_args_names = []
                for arg in get_args(expected_type):
                    if hasattr(arg, "__name__"):
                        union_args_names.append(arg.__name__)
                    elif arg is type(None):
                        union_args_names.append("None")
                    else:
                        union_args_names.append(str(arg))
            raise TypeError(
                f"Value at '{key_path}' ('{value}') "
                f"is of type {type(value).__name__}, "
                f"but expected type is '{expected_type_display}'."
            )

    @staticmethod
    def _load_file(settings_filepath: Path | str) -> Any:
        """Loads the configuration from a YAML file."""
        from yaml import YAMLError, safe_load

        try:
            config_filepath = Path(settings_filepath)
            with config_filepath.open("r", encoding="utf-8") as file:
                _config_data = safe_load(file)

        except FileNotFoundError as error:
            raise FileNotFoundError(
                f"The configuration file '{settings_filepath}' was not found"
            ) from error

        except YAMLError as error:
            raise ValueError(
                "Error parsing configuration file "
                f"'{settings_filepath}': {error}"
            ) from error

        return _config_data
