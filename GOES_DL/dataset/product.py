from abc import ABC, abstractmethod
from datetime import datetime


class Product(ABC):
    """
    Abstract a generic dataset product filename checker.

    This class defines the interface for a dataset product filename
    checker. The checker is responsible for extracting the datetime from
    a dataset product filename and verifying if a given filename matches
    the expected pattern based on the products requested by the user.

    Methods
    -------
    get_datetime(filename: str) -> datetime:
        Extracts the datetime from a dataset product filename timestamp.
    match(filename: str) -> bool:
        Checks if a given filename matches the dataset products
        filename pattern.
    """

    @abstractmethod
    def get_datetime(self, filename: str) -> datetime:
        """
        Extract a datetime from the filename.

        Extracts a datetime object from the given filename string using
        a specified pattern.

        Parameters
        ----------
        filename : str
            The filename from which to extract the datetime.

        Returns
        -------
        datetime:
            The datetime extracted from the filename.

        Raises
        ------
        ValueError:
            If the filename does not match the expected pattern or if
            the timestamp format specification is ill-formed.
        """
        ...

    @abstractmethod
    def match(self, filename: str) -> bool:
        """
        Verify the format of a provided filename.

        Checks if the provided filename matches the expected based on
        the dataset products requested by the user.

        Parameters
        ----------
        filename : str
            The filename to match against the pattern.

        Returns
        -------
        bool:
            True if the filename matches the pattern, False otherwise.
        """
        ...
