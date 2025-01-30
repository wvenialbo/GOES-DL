"""
Provide a locator for the GridSat-B1 imagery dataset products.

Classes
-------
GridSatProductLocatorB1
    Represent the GridSat-B1 imagery dataset product locator.
"""

from datetime import datetime

from .constants import (
    B1_FILE_DATE_FORMAT,
    B1_FILE_DATE_PATTERN,
    B1_FILE_PREFIX,
    B1_PATH_DATE_FORMAT,
    B1_PATH_PREFIX,
    B1_PRODUCT_LATEST_VERSION,
    B1_PRODUCT_NAME,
)
from .locator import GridSatProductLocator


class GridSatProductLocatorB1(GridSatProductLocator):
    """
    Represent the GridSat-B1 imagery dataset product locator.

    This class implements the `GridSatProductLocator` abstract class for
    for the GridSat-B1 (Geostationary IR Channel Brightness Temperature
    - GridSat B1) imagery dataset product locator.

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

    The data in the GridSat-B1 dataset products comes from different
    sources and only a global view of the Earth is available, thus,
    the origin's name and scene identifier are not reflected in the
    product's path or filename, but the product's version is. The
    product's filename pattern is as follows:

    'GRIDSAT-B1.<yyyy>.<mm>.<dd>.<HH>.<version>.nc';

    where `<yyyy>` is the gregorian year number; `<mm>`, `<dd>` and
    `<HH>` are the month, day and hour, respectively, using two digits
    padded with zeros; and `<version>` is the product's version (e.g.
    'v02r01').

    The dataset is available from various services; see the Notes below
    for a list of supported sources. For Amazon Web Services (AWS) and
    Google Cloud Platform (GCP), the product's file path pattern is as
    follows:

    '<scheme>://<net-location>/data/<yyyy>',

    where `<scheme>` identifies the protocol's scheme (e.g. 's3', 'gs'),
    `<net-location>` is the hostname (e.g. 'noaa-cdr-gridsat-b1-pds' for
    's3', and 'noaa-cdr-gridsat-b1' for 'gs'), and  `<yyyy>` is the
    gregorian year number.

    The files are also hosted on the servers of the National Centers for
    Environmental Information (NCEI), the product's file path pattern is
    as follows:

    'https://www.ncei.noaa.gov/data/<path>/access/<yyyy>';

    where `<path>` is the project's data files folder name, i.e.
    'geostationary-ir-channel-brightness-temperature-gridsat-b1',
    and `<yyyy>` is the gregorian year number.

    Input is 3-hourly data from the International Satellite Cloud
    Climatology Project (ISCCP) with gridded 0.07°x0.07° spatial
    resolution that spans from 1980 to the present. Three total
    channels are available:

    - IR: CDR-quality infrared window (IRWIN) channel (near 11 μm);
    - WV: Infrared water vapor (IRWVP) channel (near 6.7 μm);
    - VIS: Visible channel (near 0.6 μm).

    For more information visit the following link and links therein:
    https://www.ncei.noaa.gov/products/gridded-geostationary-brightness-temperature

    Notes
    -----
    Only the AWS datasource is supported currently.

    Methods
    -------
    get_base_url(datasource: str)
        Get the base URL for the GridSat-B1 imagery dataset's products.
    next_time(current_time: datetime)
        Get the next time interval. GridSat-B1 dataset organises the
        data by year.
    normalize_times(datetime_ini: datetime, datetime_fin: datetime)
        Normalise the initial and final datetimes.
    truncate_to_year(time: datetime)
        Truncate the `datetime` to the current year.

    Caution
    -------
    Members of this class not defined by the `ProductLocator` interface
    are helper methods and can be considered as implementation details,
    even though they are defined as part of the public API. In future
    releases, these methods may be moved to a private scope, suffer
    name changes, or be removed altogether.
    """  # noqa: E501

    # Base URLs for the available datasources of the GridSat-B1 dataset
    # Products:
    AVAILABLE_DATASOURCES: dict[str, str] = {
        "AWS": "s3://noaa-cdr-gridsat-b1-pds/data/",
        "GCP": "gs://noaa-cdr-gridsat-b1/data/",
        "HTTP": "https://www.ncei.noaa.gov/data/geostationary-ir-"
        "channel-brightness-temperature-gridsat-b1/access/",
    }

    # Supported datasources of the GridSat-B1 dataset Products:
    SUPPORTED_DATASOURCES: set[str] = {"AWS", "HTTP"}

    # Supported versions of the GridSat-B1 dataset Products:
    SUPPORTED_VERSIONS: set[str] = {"v02r01"}

    def __init__(
        self, versions: str | list[str] = B1_PRODUCT_LATEST_VERSION
    ) -> None:
        """
        Initialise a GridSat-B1 imagery dataset product locator.

        Constructs a new GridSat-B1 imagery dataset product locator
        object.

        Parameters
        ----------
        versions : str | list[str], optional
            The version of the GridSat-B1 product; e.g., "v02r01". The
            version may be a single version or a list of versions. Only
            the latest version is available in the public repository.
            The default is the latest version ("v02r01").

        Raises
        ------
        ValueError
            If the provided version is not supported or unavailable.
        """
        if isinstance(versions, str):
            versions = [versions]

        if unsupported_version := set(versions) - set(self.SUPPORTED_VERSIONS):
            supported_versions: list[str] = sorted(self.SUPPORTED_VERSIONS)
            raise ValueError(
                f"Unsupported version: {sorted(unsupported_version)}. "
                f"Supported versions: {supported_versions}"
            )

        super().__init__(
            name=B1_PRODUCT_NAME,
            origins=[],
            versions=versions,
            file_date_format=B1_FILE_DATE_FORMAT,
            file_date_pattern=B1_FILE_DATE_PATTERN,
            file_prefix=B1_FILE_PREFIX,
            path_date_format=B1_PATH_DATE_FORMAT,
            path_prefix=B1_PATH_PREFIX,
        )

    def get_base_url(self, datasource: str) -> tuple[str, ...]:
        """
        Get the base URL for the GridSat-B1 imagery dataset's products.

        This method returns the base URL for the GridSat-B1 imagery
        dataset's products. The base URL is used to construct the full
        URL to the dataset's product files.

        Parameters
        ----------
        datasource : str
            The datasource identifier. This parameter is used to
            determine the base URL for the dataset's products. The
            available datasources are 'AWS', 'GCP', and 'NOAA'. Only
            the AWS datasource is supported so far.

        Returns
        -------
        tuple[str, ...]
            The base URL for the GridSat-B1 imagery dataset's products
            based on the requested datasource identifier.

        Raises
        ------
        ValueError
            If the requested datasource is not supported or unavailable.
        """
        if datasource not in self.SUPPORTED_DATASOURCES:
            supported_datasources: list[str] = sorted(
                self.SUPPORTED_DATASOURCES
            )
            raise ValueError(
                f"Unsupported datasource: '{datasource}'. "
                f"Supported datasources: {supported_datasources}"
            )

        return (self.AVAILABLE_DATASOURCES[datasource], "")

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
        next_year: int = current_time.year + 1

        return current_time.replace(year=next_year)

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
        start_time: datetime = self.truncate_to_year(datetime_ini)
        end_time: datetime = self.truncate_to_year(datetime_fin)

        return start_time, end_time

    @staticmethod
    def truncate_to_year(time: datetime) -> datetime:
        """
        Truncate the `datetime` to the current year.

        The `datetime` is truncated to the beginning of the current
        year.

        Parameters
        ----------
        time : datetime
            The `datetime` to be truncated to the current year.

        Returns
        -------
        datetime
            The `datetime` truncated to the current year.
        """
        return time.replace(
            month=1, day=1, hour=0, minute=0, second=0, microsecond=0
        )
