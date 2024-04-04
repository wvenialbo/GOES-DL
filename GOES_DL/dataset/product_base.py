from abc import abstractmethod
from datetime import datetime, timezone
from re import Match, findall, fullmatch

from .product import Product


class ProductBase(Product):
    """
    Abstract a satellite imagery datasets product utility.

    This abstract base class implements the `Product` interface and
    defines a common abstract methods for the GridSat and GOES-R
    series dataset product utilities.

    Subclasses must implement the following methods (refer to their
    individual documentation for details): `get_date_format()`,
    `get_prefix()`, `get_suffix()`, and `get_timestamp_pattern()`.

    Methods
    -------
    get_date_format() -> str:
        Generate the date format for the product's filename.
    get_datetime(filename: str) -> datetime:
        Extracts the `datetime` from the product's filename.
    get_filename_pattern() -> str:
        Returns the regex pattern for the product's filename.
    get_prefix():
        Returns the prefix for the product's filename.
    get_suffix():
        Returns the suffix for the product's filename.
    get_timestamp_pattern() -> str:
        Returns the timestamp pattern for the product's filename.
    match(filename: str) -> bool:
        Verify if a given filename matches the product's filename
        pattern.
    timestamp_to_datetime(timestamp: str) -> datetime:
        Converts the product's filename timestamp string to a
        `datetime` object.
    """

    @abstractmethod
    def get_date_format(self) -> str:
        """
        Return the date format specification for the product's filename.

        Returns
        -------
        str
            The date format specification for the product's filename.
        """
        ...

    def get_datetime(self, filename: str) -> datetime:
        """
        Extract the `datetime` from the product's filename.

        This method parses the given filename and extracts the
        corresponding `datetime` object from the product's filename
        using the dataset's date/time format conventions.

        Parameters
        ----------
        filename : str
            The filename from which to extract the `datetime`.

        Returns
        -------
        datetime:
            The `datetime` extracted from the filename.

        Raises
        ------
        ValueError
            If the filename does not match the expected pattern.
        """
        pattern: str = self.get_filename_pattern()
        matches: list[str] = findall(pattern, filename)

        if len(matches) != 1:
            raise ValueError(f"Incompatible product filename: '{filename}'")

        return self.timestamp_to_datetime(matches[0])

    def get_filename_pattern(self) -> str:
        """
        Generate a regular expression pattern for the product's filename.

        Generates a filename regex pattern based on the prefix, date
        pattern, and suffix.

        Returns
        -------
        str
            The generated filename pattern.
        """
        prefix: str = self.get_prefix()
        suffix: str = self.get_suffix()
        timestamp_pattern: str = self.get_timestamp_pattern()

        return f"{prefix}{timestamp_pattern}{suffix}"

    @abstractmethod
    def get_prefix(self) -> str:
        """
        Generate the prefix for the product's filename.

        Generates the prefix for the product's filename based on the
        dataset name and origin.

        Returns
        -------
        str
            The generated prefix for the filename.
        """
        ...

    @abstractmethod
    def get_suffix(self) -> str:
        """
        Generate the suffix for the product's filename.

        Generates the suffix for the product's filename based on the
        version and file suffix.

        Returns
        -------
        str
            The generated suffix for the filename.
        """
        ...

    @abstractmethod
    def get_timestamp_pattern(self) -> str:
        """
        Generate the timestamp pattern for the product's filename.

        Returns
        -------
        str
            The generated timestamp pattern for the filename.
        """
        ...

    def match(self, filename: str) -> bool:
        """
        Verify the format of a provided filename.

        Checks if the provided filename matches the dataset product
        filename pattern for the dataset product.

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
        Convert a timestamp to a datetime object.

        Converts the provided timestamp string to a datetime object in
        UTC timezone.

        Parameters
        ----------
        timestamp : str
            The timestamp string to convert to a datetime object.

        Returns
        -------
        datetime
            The converted datetime object in UTC timezone.

        Raises
        ------
        ValueError
            The framework raises an exception if the timestamp does not
            match the expected format or if the format specification is
            ill-formed.
        """
        # File dates are always in UTC.
        file_timestamp: str = f"{timestamp}+0000"
        date_format: str = self.get_date_format()
        file_date_format: str = f"{date_format}%z"
        file_date: datetime = datetime.strptime(
            file_timestamp, file_date_format
        )

        return file_date.astimezone(timezone.utc)
