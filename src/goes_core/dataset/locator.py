"""
Provide product locator for satellite imagery dataset consumers.

Classes:
    - ProductLocator: Abstract a product locator for satellite imagery
      dataset consumers.
"""

from abc import ABC, abstractmethod
from datetime import datetime


class ProductLocator(ABC):
    """
    Abstract a product locator for satellite imagery dataset consumers.

    This abstract base class defines the product locator interface for
    consumers of satellite imagery datasets. Subclasses instances are
    responsible for:

    1) Generating a list of folder paths based on the dataset's
       directory structure and naming conventions, product details,
       and a specified date range. The generated paths must cover
       the time interval defined by the dataset's directory temporal
       granularity within the required period; paths to the folders
       containing the initial and final dates must be included in
       the list.

    2) Verifying if a given filename matches the product filename
       pattern based on the dataset file's naming conventions and
       product specifications.

    3) Extracting the corresponding UTC `datetime` information from a
       valid product's filename.

    Notes
    -----
    Subclasses must implement the following methods: `get_base_url()`,
    `get_datetime()`, `get_paths()`, and `match()`; refer to their
    individual documentation for details.

    Important
    ---------
    It is assumed that the timestamp extracted from the product's
    filename is always in UTC timezone. Consumers of the product
    utilities should be aware of this assumption. Users can convert the
    `datetime` object to the desired timezone if needed. Implementors
    of the `ProductLocator` interface should ensure that the extracted
    `datetime` object is in UTC timezone in the case that the filename's
    timestamp is in a different timezone.

    Methods
    -------
    get_base_url(datasource: str) -> tuple[str, ...]:
        Get the base URL for the dataset's products.
    get_datetime(filename: str) -> datetime:
        Extracts the `datetime` from the product's filename.
    get_paths(datetime_ini: datetime, datetime_fin: datetime) -> list[str]:
        Generate a list of paths containing the product files for the
        specified date range.
    match(filename: str) -> bool:
        Verify if a given filename matches the product's filename
        pattern.
    """

    @abstractmethod
    def get_base_url(self, datasource: str) -> tuple[str, ...]:
        """
        Get the base URL for the dataset's products.

        This method returns the base URL for the dataset's products. The
        base URL is used to construct the full URL to the dataset's
        product files.

        Parameters
        ----------
        datasource : str
            The datasource identifier. This parameter is used to
            determine the base URL for the dataset's products. E.g.
            'AWS', 'GCP', 'NOAA'.

        Returns
        -------
        tuple[str, ...]
            A tuple where the first element is the base URL for the
            dataset's products. Additional elements may be included if
            the dataset is distributed across multiple sources or the
            datasource requires additional information.
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
        datetime
            The `datetime` extracted from the filename.

        Notes
        -----
        ValueError is raised if the filename does not match the expected
        pattern or if the dataset's datetime format specification is
        ill-formed.
        """

    @abstractmethod
    def get_paths(
        self, datetime_ini: datetime, datetime_fin: datetime
    ) -> list[str]:
        """
        Generate a list of dataset directory paths.

        This method generates a list of directory paths within the
        dataset based on the folder structure and naming conventions,
        temporal granularity, and the specified date range. Paths to the
        folders containing the initial and final dates are included in
        the list.

        Parameters
        ----------
        datetime_ini : datetime
            The initial datetime for the desired data.
        datetime_fin : datetime
            The final datetime for the desired data.

        Returns
        -------
        list[str]
            A list of strings representing the paths to dataset
            directories containing the product files for the
            specified date range.
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
        bool
            True if the filename matches the pattern, False otherwise.
        """
