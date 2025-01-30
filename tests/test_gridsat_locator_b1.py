import unittest
from datetime import datetime, timedelta, timezone

from goesdl.dataset.gridsat import GridSatProductLocatorB1


class TestPassed(Exception):
    """
    Exception raised when a test has passed.
    """


class TestGridSatProductLocatorB1(unittest.TestCase):
    # This set of tests covers the initialisation of an object of
    # the `GridSatProductLocatorB1` class, including the handling of
    # invalid parameters. It also tests the `ProductLocator` interface
    # implemented by the `GridSatProductLocatorB1` and parent classes.

    def setUp(self) -> None:
        # Initialise the locator with all supported versions.
        self.locator: GridSatProductLocatorB1 = GridSatProductLocatorB1(
            versions=self._supported_versions()
        )
        self.longMessage = True

    def setUpLocator(self, version: str = "") -> None:
        version = version or self._supported_versions()[0]
        self.locator: GridSatProductLocatorB1 = GridSatProductLocatorB1(
            versions=version
        )

    # ------------------------------------------------------------------
    # A minimal subset of tests are designed to reach 100% code coverage
    # of the `GridSatProductLocatorB1` class hierarchy. The remaining
    # complementary tests help to reach 100% test coverage.
    #
    # Note: For completeness, `match()` is tested against valid filename
    # format with an unknown version, and against a valid filename with
    # an invalid date.
    #
    # Although date conversion is performed under the hood by the
    # framework and `get_datetime()` does not perform any checking for
    # invalid dates, it is tested here against a valid filename with an
    # invalid date to ensure that the method is consistent. It is also
    # tested against a `datetime` object set in a non-UTC timezone.

    def test_init_default_version(self) -> None:
        # Initialise the locator with the default version.
        with self.assertRaises(TestPassed):
            GridSatProductLocatorB1()
            raise TestPassed()

    def test_init_supported_versions(self) -> None:
        for version in self._supported_versions():
            with self.subTest(version=version):
                with self.assertRaises(TestPassed):
                    GridSatProductLocatorB1(versions=version)
                    raise TestPassed()

    def test_init_unsupported_versions(self) -> None:
        for version in self._unsupported_versions():
            with self.subTest(version=version):
                with self.assertRaises(ValueError):
                    GridSatProductLocatorB1(versions=version)

    def test_get_base_url_supported_datasources(self) -> None:
        SUPPORTED_URLS: dict[str, str] = self._supported_urls()
        for datasource_id, expected_url in SUPPORTED_URLS.items():
            returned_url: str = self.locator.get_base_url(
                datasource=datasource_id
            )
            with self.subTest(datasource=datasource_id):
                self.assertEqual(returned_url, expected_url)

    def test_get_base_url_unsupported_datasources(self) -> None:
        for datasource_id in self._unsupported_datasources():
            with self.subTest(datasource=datasource_id):
                with self.assertRaises(ValueError):
                    self.locator.get_base_url(datasource=datasource_id)

    def test_get_datetime_valid_date_utc(self) -> None:
        # Expected `datetime` object set in UTC timezone.
        TZ_UTC: timezone = timezone.utc
        self._test_get_datetime_valid_date(14, TZ_UTC)

    def test_get_datetime_valid_date_non_utc(self) -> None:
        # Expected `datetime` object set in different non-UTC timezone.
        TZ_PYT: timezone = timezone(timedelta(hours=-4.0))
        self._test_get_datetime_valid_date(10, TZ_PYT)

    def test_get_datetime_bad_date_format(self) -> None:
        for invalid_filename in self._incomplete_dates():
            with self.subTest(filename=invalid_filename):
                with self.assertRaises(ValueError):
                    self.locator.get_datetime(invalid_filename)

    def test_get_datetime_incomplete_date(self) -> None:
        for invalid_filename in self._incomplete_dates():
            with self.subTest(filename=invalid_filename):
                with self.assertRaises(ValueError):
                    self.locator.get_datetime(invalid_filename)

    def test_get_datetime_invalid_date(self) -> None:
        # Valid filename with invalid date, e.g. April 31.
        VALID_FILENAME_INVALID_DATE: str = self._filename(month=4, day=31)
        with self.assertRaises(ValueError):
            self.locator.get_datetime(VALID_FILENAME_INVALID_DATE)

    def test_match_valid_filename(self) -> None:
        VALID_FILENAME: str = self._filename()
        self.assertTrue(self.locator.match(VALID_FILENAME))

    def test_match_misspelled_prefix(self) -> None:
        INVALID_FILENAME: str = self._filename(prefix="GRIDCAT")
        self.assertFalse(self.locator.match(INVALID_FILENAME))

    def test_match_misspelled_name(self) -> None:
        INVALID_FILENAME: str = self._filename(name="B2")
        self.assertFalse(self.locator.match(INVALID_FILENAME))

    def test_match_bad_date_format(self) -> None:
        for invalid_filename in self._bad_date_format():
            with self.subTest(filename=invalid_filename):
                self.assertFalse(self.locator.match(invalid_filename))

    def test_match_incomplete_date(self) -> None:
        for invalid_filename in self._incomplete_dates():
            with self.subTest(filename=invalid_filename):
                self.assertFalse(self.locator.match(invalid_filename))

    def test_match_invalid_date(self) -> None:
        # Valid filename format with invalid dates are not caught
        # by `match()` because the date format is correct and do not
        # violates the filename pattern, although it should be caught
        # by the `get_datetime()` method.
        #
        # See `test_get_datetime_invalid_date()`.
        VALID_FILENAME_INVALID_DATE: str = self._filename(month=4, day=31)
        self.assertTrue(self.locator.match(VALID_FILENAME_INVALID_DATE))

    def test_match_supported_versions(self) -> None:
        for version in self._supported_versions():
            self.setUpLocator(version=version)
            filename: str = self._filename(version=version)
            with self.subTest(version=version):
                self.assertTrue(self.locator.match(filename))

    def test_match_unsupported_versions(self) -> None:
        self.setUpLocator(version=self._supported_versions()[0])
        for version in self._unsupported_versions():
            filename: str = self._filename(version=version)
            with self.subTest(version=version):
                self.assertFalse(self.locator.match(filename))

    def test_match_supported_multi_versions(self) -> None:
        for version in self._supported_versions():
            filename: str = self._filename(version=version)
            with self.subTest(version=version):
                self.assertTrue(self.locator.match(filename))

    def test_match_unsupported_multi_versions(self) -> None:
        for version in self._unsupported_versions():
            filename: str = self._filename(version=version)
            with self.subTest(version=version):
                self.assertFalse(self.locator.match(filename))

    def test_match_wrong_suffix(self) -> None:
        INVALID_FILENAME: str = self._filename(suffix=".txt")
        self.assertFalse(self.locator.match(INVALID_FILENAME))

    def test_match_bad_name_separator(self) -> None:
        INVALID_FILENAME: str = self._filename().replace("-B1", "_B1")
        self.assertFalse(self.locator.match(INVALID_FILENAME))

    def test_match_bad_date_separator(self) -> None:
        FILENAME: str = self._filename(year=1999, month=12, day=31, hour=23)
        invalid_filename: str = FILENAME.replace(".1999", "_1999")
        self.assertFalse(
            self.locator.match(invalid_filename), msg="Year separator"
        )
        invalid_filename = FILENAME.replace(".12", "_12")
        self.assertFalse(
            self.locator.match(invalid_filename), msg="Month separator"
        )
        invalid_filename = FILENAME.replace(".31", "_31")
        self.assertFalse(
            self.locator.match(invalid_filename), msg="Day separator"
        )
        invalid_filename = FILENAME.replace(".23", "_23")
        self.assertFalse(
            self.locator.match(invalid_filename), msg="Hour separator"
        )

    def test_match_bad_version_separator(self) -> None:
        INVALID_FILENAME: str = self._filename().replace(".v02r01", "_v02r01")
        self.assertFalse(self.locator.match(INVALID_FILENAME))

    def test_match_bad_suffix_separator(self) -> None:
        INVALID_FILENAME: str = self._filename(suffix="_nc")
        self.assertFalse(self.locator.match(INVALID_FILENAME))

    def test_match_bad_version_prefix(self) -> None:
        FILENAME: str = self._filename()
        invalid_filename: str = FILENAME.replace(".v02r01", ".b02r01")
        self.assertFalse(self.locator.match(invalid_filename))
        invalid_filename: str = FILENAME.replace(".v02r01", ".v02s01")
        self.assertFalse(self.locator.match(invalid_filename))

    def test_get_paths(self) -> None:
        TIME_1: datetime = datetime(1970, 8, 23, 0)
        TIME_2: datetime = datetime(2020, 8, 23, 14)
        RETURNED_PATHS: list[str] = self.locator.get_paths(TIME_1, TIME_2)
        EXPECTED_PATHS: list[str] = [
            self._path(year) for year in range(1970, 2021)
        ]
        self.assertEqual(RETURNED_PATHS, EXPECTED_PATHS)

    # ------------------------------------------------------------------

    def _test_get_datetime_valid_date(self, hour: int, tz: timezone) -> None:
        VALID_FILENAME: str = self._filename()
        EXPECTED_DATETIME: datetime = datetime(2020, 8, 23, hour, tzinfo=tz)
        RETURNED_DATETIME: datetime = self.locator.get_datetime(VALID_FILENAME)
        self.assertEqual(RETURNED_DATETIME, EXPECTED_DATETIME)

    # ------------------------------------------------------------------

    @staticmethod
    def _filename(
        prefix: str = "GRIDSAT",
        name: str = "B1",
        year: int = 2020,
        month: int = 8,
        day: int = 23,
        hour: int = 14,
        version: str = "v02r01",
        suffix: str = ".nc",
    ) -> str:
        # By default returns a valid filename for the GridSat-B1 imagery
        # dataset products.
        return (
            f"{prefix}-{name}."
            f"{year:04d}.{month:02d}.{day:02d}.{hour:02d}."
            f"{version}{suffix}"
        )

    @classmethod
    def _bad_date_format(cls) -> list[str]:
        BAD_YEAR: str = cls._filename(year=99999)
        BAD_MONTH: str = cls._filename(month=999)
        BAD_DAY: str = cls._filename(day=999)
        BAD_HOUR: str = cls._filename(hour=999)
        return [BAD_YEAR, BAD_MONTH, BAD_DAY, BAD_HOUR]

    @classmethod
    def _incomplete_dates(cls) -> list[str]:
        NO_YEAR: str = cls._filename(year=9999).replace(".9999", "")
        NO_MONTH: str = cls._filename(month=99).replace(".99", "")
        NO_DAY: str = cls._filename(day=99).replace(".99", "")
        NO_HOUR: str = cls._filename(hour=99).replace(".99", "")
        return [NO_YEAR, NO_MONTH, NO_DAY, NO_HOUR]

    @staticmethod
    def _path(year: int) -> str:
        return f"{year:04d}/"

    # ------------------------------------------------------------------

    @staticmethod
    def _available_datasources() -> dict[str, str]:
        return {
            "AWS": "s3://noaa-cdr-gridsat-b1-pds/data/",
            "Azure": "https://noaa-cdr-gridsat-b1.blob.core.windows.net/data/",
            "GCP": "gs://noaa-cdr-gridsat-b1/data/",
            "NOAA": "https://www.ncei.noaa.gov/data/geostationary-ir-"
            "channel-brightness-temperature-gridsat-b1/access/",
        }

    @staticmethod
    def _supported_datasources() -> list[str]:
        return ["AWS"]

    @classmethod
    def _supported_urls(cls) -> dict[str, str]:
        AVAILABLE_DATASOURCES: dict[str, str] = cls._available_datasources()
        SUPPORTED_DATASOURCES: list[str] = cls._supported_datasources()
        return {
            datasource_id: url
            for datasource_id, url in AVAILABLE_DATASOURCES.items()
            if datasource_id in SUPPORTED_DATASOURCES
        }

    @classmethod
    def _unsupported_datasources(cls) -> list[str]:
        AVAILABLE_DATASOURCES: dict[str, str] = cls._available_datasources()
        SUPPORTED_DATASOURCES: list[str] = cls._supported_datasources()
        return [
            datasource_id
            for datasource_id in AVAILABLE_DATASOURCES.keys()
            if datasource_id not in SUPPORTED_DATASOURCES
        ]

    # ------------------------------------------------------------------

    @staticmethod
    def _supported_versions() -> list[str]:
        return ["v02r01"]

    @classmethod
    def _unsupported_versions(cls) -> list[str]:
        AVAILABLE_VERSIONS: set[str] = {
            f"v{v:02}r{r:02}" for v in range(1, 10) for r in range(1, 6)
        }
        SUPPORTED_VERSIONS: list[str] = cls._supported_versions()
        return [
            version
            for version in AVAILABLE_VERSIONS
            if version not in SUPPORTED_VERSIONS
        ]
