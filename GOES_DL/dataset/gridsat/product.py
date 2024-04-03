from dataclasses import dataclass
from datetime import datetime, timezone
from re import Match, findall, fullmatch

from ..product import Product
from .constants import GRIDSAT_FILE_SUFFIX, GRIDSAT_PREFIX


@dataclass(eq=False, frozen=True)
class GridSatProduct(Product):
    """
    Represent a product utility for GridSat dataset's product consumers.

    This class implements the `Product` interface for a generic GridSat
    dataset product utility. Instances of this class are responsible
    for verifying if a given filename matches the product filename
    pattern based on the dataset's naming conventions and product
    specifications, and for extracting the corresponding `datetime`
    information from the product's filename.

    Note: Currently, only the 'Geostationary IR Channel Brightness
    Temperature - GridSat B1' and the 'Geostationary Operational
    Environmental Satellites - GOES/CONUS' datasets's products are
    supported.

    Attributes
    ----------
    name : str
        The name of the GridSat dataset product. A dataset can have
        multiple products. E.g. "B1", "GOES". Due to how the GridSat
        dataset is structured, the name is always a single string.
    origin : list[str]
        The list of origins of the GridSat product, namely one or more
        satellite identifier, e.g. "goes08". Multi-origin data may set
        this attribute to an empty list.
    version : list[str]
        The version or list of versions of the GridSat product; e.g.
        "v01r01".
    date_format : str
        The specification of the date format used in the GridSat product
        filename.
    date_pattern : str
        The regex pattern of the date format used in the GridSat product
        filename.
    file_prefix : str
        The prefix for the GridSat product's filenames.
    file_suffix : str
        The suffix for the GridSat product's filenames.

    Methods
    -------
    get_datetime(filename: str) -> datetime:
        Extracts the datetime from a GridSat product's filename.
    get_filename_pattern() -> str:
        Returns the regex pattern for the GridSat product's filename.
    get_prefix():
        Returns the prefix for the GridSat product's filename.
    get_suffix():
        Returns the suffix for the GridSat product's filename.
    match(filename: str) -> bool:
        Checks if a given filename matches the GridSat product
        filename pattern.
    timestamp_to_datetime(timestamp: str) -> datetime:
        Converts a GridSat product's filename timestamp string to a
        datetime object.
    """

    name: str
    origin: list[str]
    version: list[str]
    date_format: str
    date_pattern: str
    file_prefix: str = GRIDSAT_PREFIX
    file_suffix: str = GRIDSAT_FILE_SUFFIX

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

        return rf"{prefix}({self.date_pattern}){suffix}"

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
        sorted_origin: list[str] = sorted(self.origin)
        origin: str = f".(?:{'|'.join(sorted_origin)})" if self.origin else ""

        return f"{self.file_prefix}-{self.name}{origin}."

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
        sorted_version: list[str] = sorted(self.version)

        return f".(?:{'|'.join(sorted_version)}){self.file_suffix}"

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
            ill-formed (which is, indeed, a bug!).
        """
        # File dates are always in UTC.
        file_timestamp: str = f"{timestamp}+0000"
        file_date_format: str = f"{self.date_format}%z"
        file_date: datetime = datetime.strptime(
            file_timestamp, file_date_format
        )

        return file_date.astimezone(timezone.utc)


if __name__ == "__main__":
    FILENAME_1: str = "GRIDSAT-B1.1980.01.01.00.v02r01.nc"
    FILENAME_2: str = "GRIDSAT-B1.2023.09.30.21.v02r01.nc"
    product: GridSatProduct = GridSatProduct(
        name="B1",
        origin=[],
        version=["v02r01"],
        file_prefix="GRIDSAT",
        date_format="%Y.%m.%d.%H",
        date_pattern=r"\d{4}\.\d{2}\.\d{2}\.\d{2}",
    )
    print(product)
    print(FILENAME_2.startswith(product.get_prefix()))
    print(FILENAME_2.endswith(product.get_suffix()))
    print(product.match(FILENAME_1))
    print(product.get_datetime(FILENAME_1))
    print(product.get_datetime(FILENAME_2).astimezone())
