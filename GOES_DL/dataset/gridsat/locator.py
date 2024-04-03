from abc import abstractmethod
from dataclasses import dataclass
from datetime import datetime

from ..locator import Datasource, ProductLocator
from .product import GridSatProduct


@dataclass(eq=False, frozen=True)
class GridSatProductLocator(ProductLocator):
    """
    Abstract a product locator for GridSat datasets' product consumers.

    This abstract class implements the `ProductLocator` interface for a
    generic GridSat dataset product locator. It also defines the common
    attributes and abstract methods for all GridSat dataset product
    locators.

    Instances of this class are responsible for generating a list of
    folder paths based on the dataset's directory structure and naming
    conventions, product details, and a specified date range.

    The generated paths cover each year or month interval within the
    date range, according on the dataset's temporal granularity. Paths
    to the folders containing the initial and final dates are included
    in the list.

    Additionally, this abstract class provides methods to get references
    to objects implementing the `Datasource` and `Product` interfaces.
    The `Datasource` class is used to list the contents of a dataset's
    repository and retrieve files from it. The `Product` class is used
    to verify if a given filename matches the dataset product filename
    pattern and to extract the `datetime` from the product's filename.

    Subclasses are responsible for initialising the attributes with the
    appropriate values for the dataset and product details and provide
    implementations for the following methods (refer to their individual
    documentation for details): `next_time(current_time)` and
    `normalize_times(datetime_ini, datetime_fin)`.

    Note: Currently, only the 'Geostationary IR Channel Brightness
    Temperature - GridSat B1' and the 'Geostationary Operational
    Environmental Satellites - GOES/CONUS' datasets's products are
    supported.

    Attributes
    ----------
    product : GridSatProduct
        The GridSat product utility class for this product locator.
    datasource : Datasource
        The datasource class to retrieve the products.
    date_format : str
        The directory date/time format convention used in the dataset.
    path_prefix : str
        The path prefix to the dataset directories.

    Methods
    -------
    get_datasource() -> Datasource:
        Get a reference to an object implementing the `Datasource`
        interface.
    get_paths(datetime_ini: datetime, datetime_fin: datetime) -> list[str]:
        Generate a list of paths containing the product files for the
        specified date range.
    get_product() -> GridSatProduct:
        Get a reference to an object implementing the `Product`
        interface.
    next_time(current_time: datetime) -> datetime:
        Get the next time interval.
    normalize_times(datetime_ini: datetime, datetime_fin: datetime) -> tuple[datetime, datetime]:
        Normalise the initial and final datetimes.
    """  # noqa: E501

    product: GridSatProduct
    datasource: Datasource
    date_format: str
    path_prefix: str

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
        return self.datasource

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
        current_time: datetime
        end_time: datetime
        current_time, end_time = self.normalize_times(
            datetime_ini, datetime_fin
        )

        folder_paths: list[str] = []

        while current_time <= end_time:
            folder_path = current_time.strftime(self.date_format)
            folder_paths.append(f"{self.path_prefix}{folder_path}/")

            current_time = self.next_time(current_time)

        return folder_paths

    def get_product(self) -> GridSatProduct:
        """
        Get a reference to a `GridSatProduct` object.

        The returned instance provides methods for verifying filenames
        against the dataset product filename pattern based on the
        dataset's naming conventions and user specifications, and
        extracting the corresponding `datetime` information from the
        product's filename.

        Returns
        -------
        Product
            An instance of a `GridSatProduct` class implementing the
            `Product` interface.
        """
        return self.product

    @abstractmethod
    def next_time(self, current_time: datetime) -> datetime:
        """
        Get the next time interval.

        Get the next time interval based on the current time interval.

        Parameters
        ----------
        current_time : datetime
            The current time interval.

        Returns
        -------
        datetime
            The next time interval.
        """
        ...

    @abstractmethod
    def normalize_times(
        self, datetime_ini: datetime, datetime_fin: datetime
    ) -> tuple[datetime, datetime]:
        """
        Normalise the initial and final datetimes.

        Normalise the initial and final datetimes to the nearest
        time interval based on the dataset. The initial datetime is
        normalised to the start of the time interval and the final
        datetime is normalised to the end of the time interval.

        Parameters
        ----------
        datetime_ini : datetime
            The initial datetime.
        datetime_fin : datetime
            The final datetime.

        Returns
        -------
        tuple[datetime, datetime]
            A tuple containing the normalised initial and final
            datetimes.
        """
        ...
