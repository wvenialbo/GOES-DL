from datetime import datetime, timedelta
from typing import ClassVar

from ..base import ProductLocatorGG
from .constants import (
    GOESR_FILE_DATE_FORMAT,
    GOESR_FILE_DATE_PATTERN,
    GOESR_FILE_SUFFIX,
    GOESR_PATH_DATE_FORMAT,
)


class GOESProductLocator(ProductLocatorGG):
    """
    Abstract a product locator for GOES-R Series imagery dataset.

    This abstract class implements the `ProductLocator` interface for
    specific GOES-R Series imagery dataset product locators by
    inheriting from the `ProductLocatorGG` abstract class. The class
    implements the common specifications and naming conventions for
    products in the GOES-R dataset, and serves as a base class for more
    specialised product locator classes. It also defines the common
    attributes and abstract methods for all GOES-R Series imagery
    dataset product locators.

    Instances of this class are responsible for generating a list of
    folder paths based on the dataset's directory structure and naming
    conventions, product details, and the specified date range. The
    generated paths cover each hour interval within the required period
    according on the dataset's temporal granularity; paths to the
    folders containing the initial and final dates are included in the
    list.

    `GOESProductLocator` objects are responsible for verifying if a
    given filename matches the product filename pattern based on the
    dataset's naming conventions and product specifications using the
    `match()` method, and for extracting the corresponding `datetime`
    information from the product's filename by dint of the method
    `get_datetime()`.

    Also, the class provides the implementation for the abstract helper
    methods defined in the `ProductLocatorGG` abstract class. The
    `GOESProductLocator` class is the workhorse for all GOES-R Series
    imagery dataset product locators.

    Notes
    -----
    Subclasses are responsible for initialising the attributes with the
    appropriate values for the dataset and product details.

    Attributes
    ----------
    name : str
        The name of the GOES-R Series imagery dataset product. Due to
        how the dataset directories are organised, only a single product
        can be provided.
    level : str
        The level of the GOES-R Series imagery dataset product, e.g.
        "L1b" or "L2".
    scene : str
        The scene of the GOES-R Series imagery dataset product, e.g.
        "F" or "C".
    instrument : str
        The instrument of the GOES-R Series imagery dataset product,
        e.g. "ABI" or "GLM".
    modes : list[str]
        The list of modes of the GOES-R Series imagery dataset product,
        e.g. "M3" or "M6".
    channels : list[str]
        The list of channels of the GOES-R Series imagery dataset
        product, e.g. "C08" or "C13".
    origin : str
        The  origin identifier of the GOES-R Series imagery dataset
        product, e.g. "G16". Due to how the dataset directories are
        organised, only a single origin may be provided.

    Methods
    -------
    get_base_url(datasource: str) -> str:
        Get the base URL for the GOES-R Series imagery dataset's
        products.
    get_date_format() -> str:
        Return the date format specification for the GOES-R Series
        imagery dataset product's filename.
    get_paths(datetime_ini: datetime, datetime_fin: datetime) -> list[str]:
        Generate a list of paths containing the product files for the
        specified date range.
    get_prefix() -> str:
        Generate the prefix for the GOES-R Series imagery dataset
        product's filename.
    get_product_tag() -> str:
        Generate the product prefix for the GOES-R Series imagery
        dataset product's filename.
    get_mode_tag() -> str:
        Generate the scan mode and channel number identifier part of the
        GOES-R Series imagery dataset product's filename.
    get_suffix() -> str:
        Generate the suffix for the GOES-R Series imagery dataset
        product's filename.
    get_timestamp_pattern() -> str:
        Return the timestamp pattern for the GOES-R Series imagery
        dataset product's filename.
    next_time(current_time: datetime) -> datetime:
        Get the next time interval. GOES-R Series dataset organises the
        data by hour.
    normalize_times(datetime_ini: datetime, datetime_fin: datetime) -> tuple[datetime, datetime]:
        Normalise the initial and final datetimes.
    truncate_to_hour(time: datetime) -> datetime:
        Truncate the `datetime` to the current hour.

    Caution
    -------
    Members of this class not defined by the `ProductLocator` interface
    are helper methods and can be considered as implementation details,
    even though they are defined as part of the public API. In future
    releases, these methods may be moved to a private scope, suffer name
    changes, or be removed altogether.
    """  # noqa: E501

    # Supported datasources of the GOES-R Series imagery dataset
    # products:
    SUPPORTED_DATASOURCES: ClassVar[set[str]] = {"AWS"}

    # Satellites in the GOES-R Series are identified by the following
    # IDs:
    AVAILABLE_ORIGINS: dict[str, str] = {
        f"G{id:02d}": f"goes{id:02d}" for id in range(16, 19)
    }

    # Supported instruments from the GOES-R series:
    AVAILABLE_INSTRUMENTS: dict[str, str] = {
        "ABI": "Advanced Baseline Imager",
        "GLM": "Geostationary Lightning Mapper",
    }

    # Supported product levels from the GOES-R series:
    # - Level 1b (calibrated and geographically corrected, radiance
    #             units)
    # - Level 2  (calibrated and geographically corrected,
    #             reflectance/brightness [Kelvin] units)
    AVAILABLE_LEVELS: set[str] = {"L1b", "L2"}

    def __init__(
        self,
        name: str,
        level: str,
        scene: str,
        instrument: str,
        modes: list[str],
        channels: list[str],
        origin: str,
    ) -> None:
        """
        Initialise a GOES-R Series imagery dataset product locator.

        Constructs a GOES-R Series imagery dataset product locator
        object.

        Parameters
        ----------
        name : str
            The name of the GOES-R Series imagery dataset ABI product.
            Due to how the dataset directories are organised, only a
            single product can be provided.
        level : str
            The level of the GOES-R Series imagery dataset product, e.g.
            "L1b" or "L2".
        scene : str
            The scene of the GOES-R Series imagery dataset product, e.g.
            "F" or "C".
        instrument : str
            The instrument of the GOES-R Series imagery dataset product,
            e.g. "ABI" or "GLM".
        modes : list[str]
            The list of modes of the GOES-R Series imagery dataset
            product, e.g. "M3" or "M6".
        channels : list[str]
            The list of channels of the GOES-R Series imagery dataset
            ABI product, e.g. "C08" or "C13".
        origin : str
            The origin of the GOES-R Series imagery dataset ABI product,
            namely a satellite identifier, e.g. "G16". Due to how the
            dataset directories are organised, only a single origin may
            be provided.

        Raises
        ------
        ValueError
            If the provided origin, level or instrument is invalid. Or
            if an unexpected or unsupported setting is required for an
            instrument that does not support it.
        """
        if origin not in self.AVAILABLE_ORIGINS:
            available_origins: list[str] = sorted(self.AVAILABLE_ORIGINS)
            raise ValueError(
                f"Invalid origin ID: '{origin}'. "
                f"Available origin IDs: {available_origins}"
            )

        if instrument not in self.AVAILABLE_INSTRUMENTS:
            available_instruments: list[str] = sorted(
                self.AVAILABLE_INSTRUMENTS
            )
            raise ValueError(
                f"Invalid instrument ID: '{instrument}'. "
                f"Available instrument IDs: {available_instruments}"
            )

        if level not in self.AVAILABLE_LEVELS:
            available_levels: list[str] = sorted(self.AVAILABLE_LEVELS)
            raise ValueError(
                f"Invalid level ID: '{level}'. "
                f"Available level IDs: {available_levels}"
            )

        self.name: str = name
        self.level: str = level
        self.scene: str = scene
        self.instrument: str = instrument
        self.modes: list[str] = modes
        self.channels: list[str] = channels
        self.origin: str = origin

    def get_base_url(self, datasource: str) -> tuple[str, ...]:
        """
        Get the base URL for the GOES-R Series dataset's products.

        This method returns the base URL for the GOES-R Series imagery
        dataset's products. The base URL is used to construct the full
        URL to the dataset's product files.

        Parameters
        ----------
        datasource : str
            The datasource identifier. This parameter is used to
            determine the base URL for the dataset's products.

        Returns
        -------
        str:
            The base URL for the GOES-R Series imagery dataset's
            products based on the requested datasource identifier.

        Raises
        ------
        ValueError
            If the provided datasource is not supported or unavailable.
        """
        if datasource not in self.SUPPORTED_DATASOURCES:
            supported_datasources: list[str] = sorted(
                self.SUPPORTED_DATASOURCES
            )
            raise ValueError(
                f"Unsupported datasource: '{datasource}'. "
                f"Supported datasources: {supported_datasources}"
            )

        AVAILABLE_SCENES: dict[str, str] = {
            "F": "F",
            "C": "C",
            "M1": "M",
            "M2": "M",
        }

        scene: str = AVAILABLE_SCENES[self.scene] if self.scene else ""
        product: str = f"{self.instrument}-{self.level}-{self.name}{scene}"
        satellite: str = self.AVAILABLE_ORIGINS[self.origin]

        AVAILABLE_DATASOURCES: dict[str, str] = {
            "AWS": f"s3://noaa-{satellite}/{product}/"
        }

        return (AVAILABLE_DATASOURCES[datasource], "")

    def get_date_format(self) -> str:
        """
        Return the date format specification for the product's filename.

        Generates and returns the date format specification for the
        product's filename based on the GOES-R Series imagery dataset
        product filename's date and time format conventions. The date
        format specification string is used to parse the product's
        filename and extract the `datetime` information.

        Returns
        -------
        str
            The date format specification for the GOES-R Series imagery
            dataset product's filename.
        """
        return GOESR_FILE_DATE_FORMAT

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
            A list of strings representing the paths to the dataset
            directories containing the product files for the specified
            date range.
        """
        current_time: datetime
        end_time: datetime
        current_time, end_time = self.normalize_times(
            datetime_ini, datetime_fin
        )

        folder_paths: list[str] = []

        while current_time <= end_time:
            folder_path: str = current_time.strftime(GOESR_PATH_DATE_FORMAT)
            folder_paths.append(f"{folder_path}/")

            current_time = self.next_time(current_time)

        return folder_paths

    def get_prefix(self) -> str:
        """
        Return the prefix for the product's filename.

        Generates and returns the prefix for the GOES-R Series imagery
        dataset product's filename based on product-specific information
        like dataset and product's name, instrument and origin's
        identifier, etc.

        Returns
        -------
        str
            The prefix for the GOES-R Series imagery dataset product's
            filename.
        """
        product_prefix: str = self.get_product_tag()
        scan_band: str = self.get_mode_tag()

        if scan_band:
            scan_band = f"-{scan_band}"
        origin: str = f"_{self.origin}"

        return f"OR_{product_prefix}{scan_band}{origin}"

    def get_product_tag(self) -> str:
        """
        Return a product identifier for the product's filename.

        Generates and returns the product identifier to be used as part
        of the prefix for the GOES-R Series imagery dataset product's
        filename based on information like product's name, instrument
        and origin's identifier, etc.

        Returns
        -------
        str
            The product identifier for the GOES-R Series imagery dataset
            product's filename.
        """
        product_id: str = f"{self.level}-{self.name}{self.scene}"

        return f"{self.instrument}-{product_id}"

    def get_mode_tag(self) -> str:
        """
        Return the scan mode and band names for the product's filename.

        Generates and returns a regex pattern for the requested scan
        modes and channels that appear as tags in the product's filename
        based on product-specific scan modes and band channel
        identifiers.

        Returns
        -------
        str
            The scan mode and band names for the GOES-R Series imagery
            dataset product's filename.
        """
        sorted_modes: list[str] = sorted(self.modes)
        modes: str = f"(?:{'|'.join(sorted_modes)})" if self.modes else ""

        sorted_channels: list[str] = sorted(self.channels)
        channels: str = (
            f"(?:{'|'.join(sorted_channels)})" if self.channels else ""
        )

        return f"{modes}{channels}"

    def get_suffix(self) -> str:
        """
        Return the suffix for the product's filename.

        Generates and returns the suffix for the product's filename
        based on product-specific information like product's version
        origin's identifier, and file suffix (extension).

        Returns
        -------
        str
            The suffix for the GOES-R Series imagery dataset product's
            filename.
        """
        return GOESR_FILE_SUFFIX

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
            The timestamp regex pattern for the GOES-R Series imagery
            dataset product's filename.
        """
        start_date: str = f"_s({GOESR_FILE_DATE_PATTERN})"
        end_date: str = f"_e{GOESR_FILE_DATE_PATTERN}"
        creation_date: str = f"_c{GOESR_FILE_DATE_PATTERN}"

        return f"{start_date}{end_date}{creation_date}"

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
        return current_time + timedelta(hours=1)

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
        start_time: datetime = self.truncate_to_hour(datetime_ini)
        end_time: datetime = self.truncate_to_hour(datetime_fin)

        return start_time, end_time

    def truncate_to_hour(self, time: datetime) -> datetime:
        """
        Truncate the `datetime` to the current hour.

        The `datetime` is truncated to the beginning of the current
        hour.

        Parameters
        ----------
        time : datetime
            The `datetime` to be truncated to the current hour.

        Returns
        -------
        datetime
            The `datetime` truncated to the current hour.
        """
        return time.replace(minute=0, second=0, microsecond=0)
