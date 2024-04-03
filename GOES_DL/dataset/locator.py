from abc import ABC, abstractmethod
from datetime import datetime

from ..datasource import Datasource
from .product import Product


class ProductLocator(ABC):
    """
    Abstract a product locator for satellite imagery dataset consumers.

    This abstract base class defines the interface for consumers of
    satellite imagery datasets. Subclasses instances are responsible for
    generating a list of folder paths based on the dataset's directory
    structure and naming conventions, product details, and a specified
    date range.

    The generated paths must cover the time interval defined by the
    dataset's directory temporal granularity within the date range.
    Paths to the folders containing the initial and final dates must
    be included in the list.

    Additionally, this interface provides methods to get references to
    objects implementing the `Datasource` and `Product` interfaces. The
    `Datasource` class is used to list the contents of a dataset's
    repository and retrieve files from it. The `Product` class is used
    to verify if a given filename matches the dataset product filename
    pattern and to extract the `datetime` from the product's filename.

    Subclasses must implement the following methods (refer to their
    individual documentation for details): `get_datasource()`,
    `get_paths(datetime_ini, datetime_fin)`, and `get_product()`.

    Methods
    -------
    get_datasource() -> Datasource:
        Get a reference to an object implementing the `Datasource`
        interface.
    get_paths(datetime_ini: datetime, datetime_fin: datetime) -> list[str]:
        Generate a list of paths containing the product files for the
        specified date range.
    get_product() -> Product:
        Get a reference to an object implementing the `Product`
        interface.
    """

    @abstractmethod
    def get_datasource(self) -> Datasource:
        """
        Get a reference to a `Datasource` object.

        The returned instance provides methods to list the contents of a
        local or remote dataset's directory and retrieve files from that
        location. A dataset may be available from different sources, the
        `ProductLocator` subclass should provide a way to configure the
        appropriate source location if the dataset can be accessed from
        multiple locations.

        Returns
        -------
        Datasource
            An instance of a class implementing the `Datasource`
            interface.
        """
        ...

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
        ...

    @abstractmethod
    def get_product(self) -> Product:
        """
        Get a reference to a `Product` object.

        The returned instance provides methods for verifying filenames
        against the dataset product filename pattern based on the
        dataset's naming conventions and user specifications, and
        extracting the corresponding `datetime` information from the
        product's filename.

        Returns
        -------
        Product
            An instance of a class implementing the `Product` interface.
        """
        ...
