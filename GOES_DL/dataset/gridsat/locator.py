"""
Provide locator for GridSat family of imagery datasets products.

Classes:
    - GridSatProductLocator: Abstract a product locator for GridSat
      family of imagery datasets.
"""

from abc import abstractmethod
from dataclasses import dataclass
from datetime import datetime

from ..base import ProductLocatorGG
from .constants import GRIDSAT_FILE_SUFFIX


@dataclass(eq=False, frozen=True)
class GridSatProductLocator(ProductLocatorGG):
    """
    Abstract a product locator for GridSat family of imagery datasets.

    This abstract class implements the `ProductLocator` interface for
    a generic GridSat dataset product locator by inheriting from the
    `ProductLocatorGG` abstract class. The class implements the common
    specifications and naming conventions for products in the GridSat
    datasets, and serves as a base class for more specialised product
    locator classes. It also defines the common attributes and abstract
    methods for all GridSat dataset product locators.

    Instances of this class are responsible for generating a list of
    folder paths based on the dataset's directory structure and naming
    conventions, product details, and the specified date range. The
    generated paths cover each year or month interval within the
    required period according on the dataset's temporal granularity;
    paths to the folders containing the initial and final dates are
    included in the list.

    `GridSatProductLocator` objects are responsible for verifying if a
    given filename matches the product filename pattern based on the
    dataset's naming conventions and product specifications invoking the
    `match()` method, and for extracting the corresponding `datetime`
    information from the product's filename via the `get_datetime()`
    method.

    Also, the class provides the implementation for the abstract helper
    methods defined in the `ProductLocatorGG` abstract class. The
    `GridSatProductLocator` class is the workhorse for all GridSat
    dataset product locators.

    Notes
    -----
    Subclasses are responsible for initialising the attributes with the
    appropriate values for the dataset and product details, and provide
    implementation for the `get_base_url()` method declared by the
    `ProductLocator` interface. Definition for abstract methods declared
    by this class: `next_time()` and `normalize_times()` should also be
    provided. Refer to their individual documentation for details.

    Notes
    -----
    Currently, the 'Geostationary IR Channel Brightness Temperature
    - GridSat B1' and the 'Geostationary Operational Environmental
    Satellites - GOES/CONUS' datasets's products are supported.

    Caution
    -------
    Members of this class not defined by the `ProductLocator` interface
    are helper methods and can be considered as implementation details,
    even though they are defined as part of the public API. In future
    releases, these methods may be moved to a private scope, suffer name
    changes, or be removed altogether.

    Methods
    -------
    get_date_format()
        Return the date format specification for the GridSat product's
        filename.
    get_paths(datetime_ini: datetime, datetime_fin: datetime)
        Generate a list of paths containing the product files for the
        specified date range.
    get_prefix()
        Generate the prefix for the GridSat product's filename.
    get_suffix()
        Generate the suffix for the GridSat product's filename.
    get_timestamp_pattern()
        Return the timestamp pattern for the GridSat product's filename.
    next_time(current_time: datetime)
        Get the next time interval.
    normalize_times(datetime_ini: datetime, datetime_fin: datetime)
        Normalise the initial and final datetimes.

    Attributes
    ----------
    name : str
        The name of the GridSat dataset product. A dataset can have
        multiple products. E.g. "B1", "GOES". Due to how the GridSat
        dataset is structured, the name is always a single string.
    origins : list[str]
        The list of origins of the GridSat product, namely one or more
        satellite identifier, e.g. "goes08". Multi-origin datasets, like
        GridSat-B1, set this attribute to an empty list.
    versions : list[str]
        The version or list of versions of the GridSat product; e.g.
        "v01r01".
    file_date_format : str
        The specification of the date format used in the GridSat product
        filename.
    file_date_pattern : str
        The regex pattern of the date format used in the GridSat product
        filename.
    file_prefix : str
        The prefix for the GridSat product's filenames.
    path_date_format : str
        The specification of the path's date format convention used in
        the dataset.
    path_prefix : str
        The path prefix to the dataset directories.
    """  # noqa: E501

    name: str
    origins: list[str]
    versions: list[str]
    file_date_format: str
    file_date_pattern: str
    file_prefix: str
    path_date_format: str
    path_prefix: str

    def get_date_format(self) -> str:
        """
        Return the date format specification for the product's filename.

        Generates and returns the date format specification for
        the product's filename based on the GridSat dataset product
        filename's date and time format conventions. The date format
        specification string is used to parse the product's filename
        and extract the `datetime` information.

        Returns
        -------
        str
            The date format specification for the GridSat product's
            filename.
        """
        return self.file_date_format

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
            folder_path: str = current_time.strftime(self.path_date_format)
            folder_paths.append(f"{self.path_prefix}{folder_path}/")

            current_time = self.next_time(current_time)

        return folder_paths

    def get_prefix(self) -> str:
        """
        Return the prefix for the product's filename.

        Generates and returns the prefix for the GridSat product's
        filename based on product-specific information like dataset
        and product's name, instrument and origin's identifier, etc.

        Returns
        -------
        str
            The prefix for the GridSat product's filename.
        """
        sorted_origins: list[str] = sorted(self.origins)
        origins: str = (
            rf"\.(?:{'|'.join(sorted_origins)})" if self.origins else ""
        )

        return rf"{self.file_prefix}-{self.name}{origins}\."

    def get_suffix(self) -> str:
        """
        Return the suffix for the product's filename.

        Generates and returns the suffix for the product's filename
        based on product-specific information like product's version
        origin's identifier, and file suffix (extension).

        Returns
        -------
        str
            The suffix for the GridSat product's filename.
        """
        sorted_versions: list[str] = sorted(self.versions)

        return rf"\.(?:{'|'.join(sorted_versions)})\{GRIDSAT_FILE_SUFFIX}"

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
            The timestamp regex pattern for the GridSat product's
            filename.
        """
        return f"({self.file_date_pattern})"

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
