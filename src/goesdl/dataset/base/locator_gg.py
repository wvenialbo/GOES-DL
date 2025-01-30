"""
Provide GridSat or GOES-R series dataset product locator.

Classes:
    - ProductLocatorGG: Abstract a GridSat or GOES-R series dataset
      product locator.
"""

from abc import abstractmethod
from collections.abc import Iterable
from datetime import datetime, timezone
from re import Match, findall, fullmatch

from ..locator import ProductLocator


class ProductLocatorGG(ProductLocator):
    """
    Abstract a GridSat or GOES-R series dataset product locator.

    This class implements the `ProductLocator` interface and serves as
    a base class for product locators of the GridSat and GOES-R series
    datasets. It also defines common abstract methods that subclasses
    must implement to provide dataset-specific product utilities.

    Instances of this class are responsible for verifying if a given
    filename matches the product filename pattern based on the dataset's
    naming conventions and product specifications by means of its method
    `match()`, and for extracting the corresponding `datetime`
    information from the product's filename through the use of the
    `get_datetime()` method.

    Notes
    -----
    Subclasses must implement the following methods: `get_base_url()`
    and `get_paths()` declared by the `ProductLocator` interface.
    Implementations for abstract methods declared by this class:
    `get_date_format()`, `get_prefix()`, `get_suffix()`, and
    `get_timestamp_pattern()` should also be provided. Refer to their
    individual documentation for details.

    Methods
    -------
    get_date_format() -> str:
        Return the date format specification for the product's filename.
    get_datetime(filename: str) -> datetime:
        Extract the `datetime` from the product's filename.
    get_filename_pattern() -> str:
        Return a regular expression pattern for the product's filename.
    get_prefix():
        Return the prefix for the product's filename.
    get_suffix():
        Return the suffix for the product's filename.
    get_timestamp_pattern() -> str:
        Return the timestamp regex pattern for the product's filename.
    match(filename: str) -> bool:
        Verify if a provided filename matches the required format.
    timestamp_to_datetime(timestamp: str) -> datetime:
        Convert a timestamp string to a UTC `datetime` object.

    Caution
    -------
    Members of this class not defined by the `ProductLocator` interface
    are helper methods and can be considered as implementation details,
    even though they are defined as part of the public API. In future
    releases, these methods may be moved to a private scope, suffer name
    changes, or be removed altogether.
    """

    @abstractmethod
    def get_date_format(self) -> str:
        """
        Return the date format specification for the product's filename.

        Generates and returns the date format specification for the
        product's filename based on the dataset product filename's date
        and time format conventions. The date format specification
        string is used to parse the product's filename and extract the
        `datetime` information.

        Returns
        -------
        str
            The date format specification for the product's filename.
        """

    def get_datetime(self, filename: str) -> datetime:
        """
        Extract the `datetime` from the product's filename.

        This method parses the given filename and convert it to the
        corresponding `datetime` object from the product's filename
        using the dataset's date and time format conventions.

        Parameters
        ----------
        filename : str
            The filename from which to extract the `datetime`.

        Returns
        -------
        datetime
            The `datetime` extracted from the filename.

        Raises
        ------
        ValueError
            If the filename does not match the expected pattern.
        """
        pattern: str = self.get_filename_pattern()
        matches: list[str] = findall(pattern, filename)

        if len(matches) != 1:
            raise ValueError(
                f"Expected 1 timestamp field, found {len(matches)} fields"
            )

        return self.timestamp_to_datetime(matches[0])

    def get_filename_pattern(self) -> str:
        """
        Return a regular expression pattern for the product's filename.

        Generates and returns a regular expression pattern for the
        product's filename based on the prefix, date pattern, and
        suffix created with dataset-specific product information.

        Returns
        -------
        str
            The regular expression pattern for the product's filename
        """
        prefix: str = self.get_prefix()
        suffix: str = self.get_suffix()
        timestamp_pattern: str = self.get_timestamp_pattern()

        return f"{prefix}{timestamp_pattern}{suffix}"

    @abstractmethod
    def get_prefix(self) -> str:
        """
        Return the prefix for the product's filename.

        Generates and returns the prefix for the product's filename
        based on product-specific information like dataset and product's
        name, instrument and origin's identifier, etc.

        Returns
        -------
        str
            The prefix for the product's filename.
        """

    @abstractmethod
    def get_suffix(self) -> str:
        """
        Return the suffix for the product's filename.

        Generates and returns the suffix for the product's filename
        based on product-specific information like product's version
        origin's identifier, and file suffix (extension).

        Returns
        -------
        str
            The suffix for the product's filename.
        """

    @abstractmethod
    def get_timestamp_pattern(self) -> str:
        """
        Return the timestamp regex pattern for the product's filename.

        Generates and returns the timestamp regular expression
        pattern for the product's filename based on the dataset
        product filename's date and time format conventions. The
        timestamp regex pattern is used to extract the substring
        containing the timestamp from the product's filename
        before extracting the `datetime` information.

        Returns
        -------
        str
            The timestamp regex pattern for the product's filename.
        """

    def match(self, filename: str) -> bool:
        """
        Verify if a provided filename matches the required format.

        Checks if the provided filename matches the product's filename
        pattern for the dataset product.

        Parameters
        ----------
        filename : str
            The filename to match against the pattern.

        Returns
        -------
        bool
            True if the filename matches the pattern, False otherwise.
        """
        pattern: str = self.get_filename_pattern()
        match: Match[str] | None = fullmatch(pattern, filename)

        return match is not None

    def timestamp_to_datetime(self, timestamp: str) -> datetime:
        """
        Convert a timestamp string to a UTC `datetime` object.

        Parses and converts the provided timestamp string to a
        `datetime` object.

        Notes
        -----
        The timestamp string extracted from the product's filename are
        (or assumed to be) always in UTC timezone. Consumer of product
        utilities should be aware of this assumption. The user could
        convert the `datetime` object to the desired timezone if needed.

        The framework raises `ValueError` if the timestamp does not
        match the expected format or if the format specification is
        ill-formed.

        Parameters
        ----------
        timestamp : str
            The timestamp string to convert to a `datetime` object.

        Returns
        -------
        datetime
            The converted `datetime` object in UTC timezone.
        """
        # File dates are always in UTC.
        file_timestamp: str = f"{timestamp}+0000"
        date_format: str = self.get_date_format()
        file_date_format: str = f"{date_format}%z"
        file_date: datetime = datetime.strptime(
            file_timestamp, file_date_format
        )

        return file_date.astimezone(timezone.utc)

    @staticmethod
    def _validate_entity(
        name: str, entity: str, available_entities: Iterable[str]
    ) -> None:
        if entity not in available_entities:
            supported_entities: list[str] = sorted(available_entities)
            supported_ids = "', '".join(supported_entities)
            raise ValueError(
                f"Invalid {name} ID: '{entity}'. "
                f"Available {name} IDs: '{supported_ids}'"
            )

    @staticmethod
    def _validate_set(
        name: str,
        entities: str | Iterable[str],
        available_entities: Iterable[str],
    ) -> None:
        if not set(entities).issubset(available_entities):
            invalid_entities = set(entities) - set(available_entities)
            supported_entities: list[str] = sorted(available_entities)
            invalid_ids = "', '".join(invalid_entities)
            supported_ids = "', '".join(supported_entities)
            raise ValueError(
                f"Invalid {name} IDs: '{invalid_ids}'. "
                f"Available {name} IDs: '{supported_ids}'"
            )

    @classmethod
    def _validate_channels(
        cls: type["ProductLocatorGG"],
        channel: str | Iterable[str],
        available_channels: Iterable[str],
    ) -> None:
        cls._validate_set("channel", channel, available_channels)

    @classmethod
    def _validate_datasource(
        cls: type["ProductLocatorGG"],
        datasource: str,
        available_datasources: Iterable[str],
    ) -> None:
        cls._validate_entity("datasource", datasource, available_datasources)

    @classmethod
    def _validate_instrument(
        cls: type["ProductLocatorGG"],
        instrument: str,
        available_instruments: Iterable[str],
    ) -> None:
        cls._validate_entity("instrument", instrument, available_instruments)

    @classmethod
    def _validate_level(
        cls: type["ProductLocatorGG"], level: str, available_levels: set[str]
    ) -> None:
        cls._validate_entity("level", level, available_levels)

    @classmethod
    def _validate_origin(
        cls: type["ProductLocatorGG"],
        origin: str,
        available_origins: Iterable[str],
    ) -> None:
        cls._validate_entity("origin", origin, available_origins)

    @classmethod
    def _validate_product(
        cls: type["ProductLocatorGG"],
        name: str,
        available_products: Iterable[str],
    ) -> None:
        cls._validate_entity("product", name, available_products)

    @classmethod
    def _validate_scene(
        cls: type["ProductLocatorGG"],
        scene: str,
        available_scenes: Iterable[str],
    ) -> None:
        cls._validate_entity("scene", scene, available_scenes)
