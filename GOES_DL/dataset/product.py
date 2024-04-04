from abc import ABC, abstractmethod
from datetime import datetime


class Product(ABC):
    """
    Abstract a satellite imagery dataset's product utility.

    This abstract base class defines the interface of a dataset's
    product utility for consumers of satellite imagery. Subclasses
    instances are responsible for verifying if a given filename
    matches the product filename pattern based on the dataset's naming
    conventions and product specifications, and for extracting the
    corresponding `datetime` information from the product's filename.

    Notes
    -----
    Subclasses must implement the following methods (refer to their
    individual documentation for details): `get_datetime(filename)`
    and `match(filename)`.

    Important
    ---------
    The `Product` interface assumes that the timestamp extracted from
    the product's filename is always in UTC timezone. Consumers of the
    product utilities should be aware of this assumption. Users could
    convert the `datetime` object to the desired timezone if needed.

    Methods
    -------
    get_datetime(filename: str) -> datetime:
        Extracts the `datetime` from the product's filename.
    match(filename: str) -> bool:
        Verify if a given filename matches the product's filename
        pattern.
    """

    @abstractmethod
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
        datetime:
            The `datetime` extracted from the filename.

        Raises
        ------
        ValueError:
            If the filename does not match the expected pattern or if
            the dataset's datetime format specification is ill-formed.
        """

    @abstractmethod
    def match(self, filename: str) -> bool:
        """
        Verify if a filename matches the product's filename pattern.

        This method checks the given filename against the dataset
        product filename pattern based on the dataset's naming
        conventions and product specifications.

        Parameters
        ----------
        filename : str
            The filename to match against the pattern.

        Returns
        -------
        bool:
            True if the filename matches the pattern, False otherwise.
        """
