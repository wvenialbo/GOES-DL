"""
Provide a locator for the GridSat-GOES/CONUS imagery dataset products.

Attributes
----------
MONTHS_IN_YEAR : int
    The number of months in a year, used for date calculations.

Classes
-------
GridSatProductLocatorGC
    Represent the GridSat-GOES/CONUS imagery dataset product locator.
"""

from datetime import datetime

from .constants import (
    GOES_FILE_DATE_FORMAT,
    GOES_FILE_DATE_PATTERN,
    GOES_FILE_PREFIX,
    GOES_PATH_DATE_FORMAT,
    GOES_PRODUCT_LATEST_VERSION,
)
from .locator import GridSatProductLocator

# Define a constant for the number of months in a year
MONTHS_IN_YEAR = 12


class GridSatProductLocatorGC(GridSatProductLocator):
    """
    Represent the GridSat-GOES/CONUS imagery dataset product locator.

    This class implements the `GridSatProductLocator` abstract class
    for the GridSat-GOES/CONUS (Geostationary Operational Environmental
    Satellites - GOES/CONUS) dataset product locator.

    Instances of this class are responsible for generating a list of
    folder paths based on the dataset's directory structure and naming
    conventions, product details, and a specified date range. The
    generated paths cover each year within the date range. Paths to the
    folders containing the initial and final dates are included in the
    list.

    Instances of this class are also responsible for verifying if a
    given filename matches the product filename pattern based on the
    dataset's naming conventions and product specifications, and for
    extracting the corresponding `datetime` information from the
    product's filename.

    The data in the GridSat-GOES/CONUS dataset products comes from GOES
    second generation (GOES-I to GOES-M) series, GOES-8 to GOES-15. The
    dataset provides data for two separate scenes: the entire GOES
    domain (Full Disk) and the CONUS domain (Contiguous United States).
    The scene and origin names are reflected in the product's path and
    filename, as does the product's version. The product's filename
    pattern is as follows:

    'GridSat-<SCENE>.<origin>.<yyyy>.<mm>.<dd>.<HH><MM>.<version>.nc',

    where `<SCENE>` is the scene name in uppercase (e.g. 'CONUS' or
    'GOES'); `<origin>` is the satellite identifier in lowercase (e.g.
    'goes08' to 'goes15'); `<yyyy>` is the gregorian year number;
    `<mm>`, `<dd>`, `<HH>` and <MM> are the month, day, hour and minute,
    respectively, using two digits padded with zeros; and `<version>` is
    the product's version(e.g. 'v01').

    The dataset's files are hosted on the servers of the NOAA's National
    Centers for Environmental Information (NCEI), the product's file
    path pattern is as follows:

    'https://<net-location>/data/gridsat-goes/access/<scene>/<yyyy>/<mm>/',

    where `<net-location>` is 'www.ncei.noaa.gov', and `<scene>` is the
    scene name in lowercase (e.g. 'conus' or 'goes'). `<yyyy>` and
    `<mm>` are, respectively, the gregorian year number and the month
    number using two digits padded with zeros.

    Input is half-hourly data from the GOES second generation satellite
    series with gridded 0.04°x0.04° spatial resolution that spans from
    1994 to 2017. Six total channels are available

    For more information visit the following link and links therein:
    https://www.ncei.noaa.gov/products/satellite/gridded-goes-conus

    Notes
    -----
    No datasource is supported yet.

    Methods
    -------
    get_base_url(datasource: str) -> str:
        Get the base URL for the GridSat-GOES/CONUS imagery dataset's
        products.
    next_time(current_time: datetime) -> datetime
        Get the next time interval. GridSat-GOES/CONUS dataset organises
        the data by month.
    normalise_times(datetime_ini: datetime, datetime_fin: datetime)
        -> tuple[datetime, datetime]
        Normalise the initial and final datetimes.
    truncate_to_month(time: datetime) -> datetime
        Truncate the `datetime` to the current month.

    Caution
    -------
    Members of this class not defined by the `ProductLocator` interface
    are helper methods and can be considered as implementation details,
    even though they are defined as part of the public API. In future
    releases, these methods may be moved to a private scope, suffer
    name changes, or be removed altogether.
    """

    # Satellites in the GOES 2nd generation (GOES-I to GOES-M) series
    # are identified by the following IDs:
    AVAILABLE_ORIGINS: dict[str, str] = {
        f"G{idn:02d}": f"goes{idn:02d}" for idn in range(8, 16)
    }

    # Available scenes for the GridSat-GOES/CONUS imagery dataset
    # products:
    #
    # NOTE: In its strictest sense, “Contiguous United States” refers
    # to the lower 48 states in North America (including the District
    # of Columbia), and “Continental United States” refers to 49 states
    # (including Alaska and the District of Columbia).
    AVAILABLE_SCENES: dict[str, str] = {
        "F": "Full Disk",
        "C": "CONUS (Contiguous United States)",
    }

    # Mapping between scene IDs and dataset group names:
    SCENE_TO_NAME: dict[str, str] = {
        "F": "GOES",
        "C": "CONUS",
    }

    # Base URLs for the available datasources of the GridSat-GOES/CONUS
    # imagery dataset products:
    AVAILABLE_DATASOURCES: dict[str, str] = {
        "HTTP": "https://www.ncei.noaa.gov/data/gridsat-goes/access/",
    }

    # Supported datasources of the GridSat-GOES/CONUS imagery dataset
    # products:
    SUPPORTED_DATASOURCES: set[str] = set(AVAILABLE_DATASOURCES)

    # Available versions of the GridSat-GOES/CONUS imagery dataset
    # products:
    SUPPORTED_VERSIONS: set[str] = {"v01"}

    def __init__(
        self,
        scene: str,
        origins: str | list[str],
        versions: str | list[str] = GOES_PRODUCT_LATEST_VERSION,
    ) -> None:
        """
        Initialise a GridSat-GOES/CONUS imagery dataset product locator.

        Constructs a GridSat-GOES/CONUS imagery dataset product locator
        object.

        Parameters
        ----------
        scene : str
            The scene ID for the dataset. Supported scenes are "F" (Full
            Disk) and "C" (CONUS, Contiguous United States). Due to how
            the GridSat-GOES/CONUS dataset directories are organised,
            only a single scene may be provided.
        origins : str | list[str]
            The origin of the GridSat-GOES/CONUS imagery dataset
            product, namely a satellite identifier, e.g. "G08".
            The origin may be a single origin or a list of origins.
        versions : str | list[str]
            The version of the GridSat-GOES/CONUS imagery dataset
            product; e.g., "v01". The version may be a single version
            or a list of versions. Only the latest version is available
            in the public repository. The default is the latest version
            ("v01").

        Raises
        ------
        ValueError
            If the provided origin, scene, or version is invalid.
        """
        self._validate_scene(scene, self.AVAILABLE_SCENES)

        if isinstance(origins, str):
            origins = [origins]

        if unavailable_origin := set(origins) - set(self.AVAILABLE_ORIGINS):
            available_origins: list[str] = sorted(self.AVAILABLE_ORIGINS)
            raise ValueError(
                f"Invalid origin IDs: {sorted(unavailable_origin)}. "
                f"Available origin IDs: {available_origins}"
            )

        if isinstance(versions, str):
            versions = [versions]

        if unsupported_version := set(versions) - set(self.SUPPORTED_VERSIONS):
            supported_versions: list[str] = sorted(self.SUPPORTED_VERSIONS)
            raise ValueError(
                f"Unsupported versions: {sorted(unsupported_version)}. "
                f"Supported versions: {supported_versions}"
            )

        product_name: str = self.SCENE_TO_NAME[scene]
        data_origin: list[str] = [
            self.AVAILABLE_ORIGINS[orig] for orig in origins
        ]

        goes_path_prefix: str = f"{product_name.lower()}/"

        super().__init__(
            name=product_name,
            origins=data_origin,
            versions=versions,
            file_date_format=GOES_FILE_DATE_FORMAT,
            file_date_pattern=GOES_FILE_DATE_PATTERN,
            file_prefix=GOES_FILE_PREFIX,
            path_date_format=GOES_PATH_DATE_FORMAT,
            path_prefix=goes_path_prefix,
        )

    def get_base_url(self, datasource: str) -> tuple[str, ...]:
        """
        Get the base URL for the GridSat-GOES/CONUS dataset's products.

        This method returns the base URL for the GridSat-GOES/CONUS
        imagery dataset's products. The base URL is used to construct
        the full URL to the dataset's product files.

        Parameters
        ----------
        datasource : str
            The datasource identifier. This parameter is used to
            determine the base URL for the dataset's products. The only
            available datasource is 'NOAA'. No datasource is supported
            yet.

        Returns
        -------
        tuple[str, ...]
            The base URL for the GridSat-GOES/CONUS imagery dataset's
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

        return (self.AVAILABLE_DATASOURCES[datasource],)

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
        next_month: int = current_time.month + 1
        next_year: int = current_time.year
        if next_month > MONTHS_IN_YEAR:
            next_month = 1
            next_year += 1

        return current_time.replace(year=next_year, month=next_month)

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
        start_time: datetime = self.truncate_to_month(datetime_ini)
        end_time: datetime = self.truncate_to_month(datetime_fin)

        return start_time, end_time

    @staticmethod
    def truncate_to_month(time: datetime) -> datetime:
        """
        Truncate the `datetime` to the current month.

        The `datetime` is truncated to the beginning of the current
        month.

        Parameters
        ----------
        time : datetime
            The `datetime` to be truncated to the current month.

        Returns
        -------
        datetime
            The `datetime` truncated to the current month.
        """
        return time.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
