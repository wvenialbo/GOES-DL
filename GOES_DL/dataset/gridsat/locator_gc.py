from datetime import datetime

from GOES_DL.dataset.gridsat.constants import (
    GOES_FILE_DATE_FORMAT,
    GOES_FILE_DATE_PATTERN,
    GOES_FILE_PREFIX,
    GOES_PATH_DATE_FORMAT,
    GOES_PRODUCT_LATEST_VERSION,
)
from GOES_DL.dataset.gridsat.locator import GridSatProductLocator


class GridSatProductLocatorGC(GridSatProductLocator):
    """
    Represent the GridSat-GOES/CONUS imagery dataset product locator.

    This class implements the `GridSatProductLocator` abstract class for
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
    invalid_datasource(datasource: list[str]) -> str
        Check for unsupported datasources in a list of datasources.
    invalid_origin(origin: list[str]) -> str:
        Check for unavailable origins in a list of origins.
    invalid_scene(scene: list[str]) -> str:
        Check for unavailable scenes in a list of scenes.
    invalid_version(version: list[str]) -> str:
        Check for unsupported versions in a list of versions.
    next_time(current_time: datetime) -> datetime
        Get the next time interval. GridSat-GOES dataset organises the
        data by year.
    normalise_times(datetime_ini: datetime, datetime_fin: datetime)
        -> tuple[datetime, datetime]
        Normalise the initial and final datetimes.
    truncate_to_month(time: datetime) -> datetime
        Truncate the datetime to the current month.

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
        f"G{id:02d}": f"goes{id:02d}" for id in range(8, 16)
    }

    # Available scenes from the GridSat-GOES/CONUS imagery dataset
    # products:
    #
    # NOTE: In its strictest sense, “Contiguous United States” refers
    # to the lower 48 states in North America (including the District of
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
    BASE_URL: dict[str, str] = {
        "NOAA": "https://www.ncei.noaa.gov/data/gridsat-goes/access/",
    }

    # Supported datasources of the GridSat-GOES/CONUS imagery dataset
    # products:
    SUPPORTED_DATASOURCES: set[str] = set(BASE_URL.keys())

    # Available versions of the GridSat-GOES/CONUS imagery dataset
    # products:
    SUPPORTED_VERSIONS: set[str] = {"v01"}

    def __init__(
        self,
        scene: str,
        origin: str | list[str],
        version: str | list[str] = GOES_PRODUCT_LATEST_VERSION,
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
        origin : str | list[str]
            The origin of the GridSat-GOES/CONUS imagery dataset
            product, namely a satellite identifier, e.g. "goes08".
            The origin may be a single origin or a list of origins.
        version : str | list[str]
            The version of the GridSat-GOES/CONUS imagery dataset
            product; e.g., "v01". The version may be a single version
            or a list of versions. Only the latest version is available
            in the public repository. The default is the latest version
            ("v01").

        Raises
        ------
        ValueError
            If the provided origin, scene, or version is invalid.
        Parameters
        ----------
        datasource : str, optional

        """
        if unavailable_scene := self.invalid_scene([scene]):
            available_scenes: list[str] = sorted(self.AVAILABLE_SCENES.keys())
            raise ValueError(
                f"Invalid scene: '{unavailable_scene}'. "
                f"Available scene IDs: {available_scenes}"
            )

        if isinstance(origin, str):
            origin = [origin]

        if unavailable_origin := self.invalid_origin(origin):
            available_origins: list[str] = sorted(
                self.AVAILABLE_ORIGINS.keys()
            )
            raise ValueError(
                f"Invalid origin: '{unavailable_origin}'. "
                f"Available origin IDs: {available_origins}"
            )

        if isinstance(version, str):
            version = [version]

        if unsupported_version := self.invalid_version(version):
            supported_versions: list[str] = sorted(self.SUPPORTED_VERSIONS)
            raise ValueError(
                f"Unsupported version: '{unsupported_version}'. "
                f"Supported versions: {supported_versions}"
            )

        product_name: str = self.SCENE_TO_NAME[scene]
        data_origin: list[str] = [
            self.AVAILABLE_ORIGINS[orig] for orig in origin
        ]

        GOES_PATH_PREFIX: str = f"{product_name.lower()}/"

        super(GridSatProductLocatorGC, self).__init__(
            name=product_name,
            origin=data_origin,
            version=version,
            file_date_format=GOES_FILE_DATE_FORMAT,
            file_date_pattern=GOES_FILE_DATE_PATTERN,
            file_prefix=GOES_FILE_PREFIX,
            path_date_format=GOES_PATH_DATE_FORMAT,
            path_prefix=GOES_PATH_PREFIX,
        )

    def get_base_url(self, datasource: str) -> str:
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
        str:
            The base URL for the GridSat-GOES/CONUS imagery dataset's
            products based on the requested datasource identifier.

        Raises
        ------
        ValueError
            If the provided datasource is not supported or unavailable.
        """
        if unsupported_datasource := self.invalid_datasource([datasource]):
            available_datasource: list[str] = sorted(
                self.SUPPORTED_DATASOURCES
            )
            raise ValueError(
                f"Unsupported datasource: {unsupported_datasource}. "
                f"Available datasources: {available_datasource}"
            )

        return self.BASE_URL[datasource]

    def invalid_datasource(self, datasource: list[str]) -> str:
        """
        Check for unsupported or invalid datasources.

        Verifies and returns the first unsupported datasource from a
        list of datasources.

        Parameters
        ----------
        datasource : list[str]
            The list of datasources to check for unsupported
            datasources.

        Returns
        -------
        str
            The first unsupported datasource found in the list of
            datasources. An empty string is returned if all datasources
            are supported.
        """
        return next(
            (ds for ds in datasource if ds not in self.SUPPORTED_DATASOURCES),
            "",
        )

    def invalid_origin(self, origin: list[str]) -> str:
        """
        Check for unavailable or invalid origins.

        Verifies and returns the first unavailable origin from a list of
        origins.

        Parameters
        ----------
        origin : list[str]
            The list of origins to check for unavailable origins.

        Returns
        -------
        str
            The first unavailable origin found in the list of origins.
            An empty string is returned if all origins are available.
        """
        return next(
            (orig for orig in origin if orig not in self.AVAILABLE_ORIGINS),
            "",
        )

    def invalid_scene(self, scene: list[str]) -> str:
        """
        Check for unavailable or invalid scenes.

        Verifies and returns the first unavailable scene from a list of
        scenes.

        Parameters
        ----------
        scene : list[str]
            The list of scenes to check for unavailable scenes.

        Returns
        -------
        str
            The first unavailable scene found in the list of scenes.
            An empty string is returned if all scenes are available.
        """
        return next(
            (sce for sce in scene if sce not in self.AVAILABLE_SCENES),
            "",
        )

    def invalid_version(self, version: list[str]) -> str:
        """
        Check for unsupported or invalid versions.

        Verifies and returns the first unsupported version from a list
        of versions.

        Parameters
        ----------
        version : list[str]
            The list of versions to check for unsupported versions.

        Returns
        -------
        str
            The first unsupported version found in the list of versions.
            An empty string is returned if all versions are supported.
        """
        return next(
            (ver for ver in version if ver not in self.SUPPORTED_VERSIONS),
            "",
        )

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
        next_month = current_time.month + 1
        next_year = current_time.year
        if next_month > 12:
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
        start_time = self.truncate_to_month(datetime_ini)
        end_time = self.truncate_to_month(datetime_fin)

        return start_time, end_time

    def truncate_to_month(self, time: datetime) -> datetime:
        """
        Truncate the datetime to the current month.

        The datetime is truncated to the start of the month.

        Parameters
        ----------
        time : datetime
            The datetime to round.

        Returns
        -------
        datetime
            The truncated datetime.
        """
        return time.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
