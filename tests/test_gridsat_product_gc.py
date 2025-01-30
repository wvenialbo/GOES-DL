import unittest
from datetime import datetime, timedelta, timezone

from goesdl.dataset.gridsat import GridSatProductLocatorGC


class TestPassed(Exception):
    """
    Exception raised when a test has passed.
    """


class TestGridSatProductLocatorGC(unittest.TestCase):
    # This set of tests covers the initialisation of an object of
    # the `GridSatProductLocatorGC` class, including the handling of
    # invalid parameters. It also tests the `ProductLocator` interface
    # implemented by the `GridSatProductLocatorGC` and parent classes.

    def setUp(self) -> None:
        # Initialise the locator with a valid scene, and all supported
        # origins and versions.
        self.locator: GridSatProductLocatorGC = GridSatProductLocatorGC(
            scene=self._supported_scenes()[0],
            origins=self._supported_origins(),
            versions=self._supported_versions(),
        )
        self.longMessage = True

    def setUpLocator(
        self, scene: str = "", origin: str = "", version: str = ""
    ) -> None:
        self.locator: GridSatProductLocatorGC = GridSatProductLocatorGC(
            scene=scene or self._supported_scenes()[0],
            origins=origin or self._supported_origins(),
            versions=version or self._supported_versions(),
        )

    # ------------------------------------------------------------------
    # A minimal subset of tests are designed to reach 100% code coverage
    # of the `GridSatProductLocatorGC` class hierarchy. The remaining
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

    def test_init_supported_scenes(self) -> None:
        for scene in self._supported_scenes():
            with self.subTest(scene=scene):
                with self.assertRaises(TestPassed):
                    GridSatProductLocatorGC(
                        scene=scene,
                        origins=self._supported_origins(),
                        versions=self._supported_versions(),
                    )
                    raise TestPassed()

    def test_init_unsupported_scenes(self) -> None:
        for scene in self._unsupported_scenes():
            with self.subTest(scene=scene):
                with self.assertRaises(ValueError):
                    GridSatProductLocatorGC(
                        scene=scene,
                        origins=self._supported_origins(),
                        versions=self._supported_versions(),
                    )

    def test_init_supported_origins(self) -> None:
        for origin in self._supported_origins():
            with self.subTest(origin=origin):
                with self.assertRaises(TestPassed):
                    GridSatProductLocatorGC(
                        scene=self._supported_scenes()[0],
                        origins=origin,
                        versions=self._supported_versions(),
                    )
                    raise TestPassed()

    def test_init_unsupported_origins(self) -> None:
        for origin in self._unsupported_origins():
            with self.subTest(origin=origin):
                with self.assertRaises(ValueError):
                    GridSatProductLocatorGC(
                        scene=self._supported_scenes()[0],
                        origins=origin,
                        versions=self._supported_versions(),
                    )

    def test_init_default_version(self) -> None:
        # Initialise the locator with the default version.
        with self.assertRaises(TestPassed):
            GridSatProductLocatorGC(
                scene=self._supported_scenes()[0],
                origins=self._supported_origins()[0],
            )
            raise TestPassed()

    def test_init_supported_versions(self) -> None:
        for version in self._supported_versions():
            with self.subTest(version=version):
                with self.assertRaises(TestPassed):
                    GridSatProductLocatorGC(
                        scene=self._supported_scenes()[0],
                        origins=self._supported_origins()[0],
                        versions=version,
                    )
                    raise TestPassed()

    def test_init_unsupported_versions(self) -> None:
        for version in self._unsupported_versions():
            with self.subTest(version=version):
                with self.assertRaises(ValueError):
                    GridSatProductLocatorGC(
                        scene=self._supported_scenes()[0],
                        origins=self._supported_origins()[0],
                        versions=version,
                    )

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
        self._test_get_datetime_valid_date(12, TZ_UTC)

    def test_get_datetime_valid_date_non_utc(self) -> None:
        # Expected `datetime` object set in different non-UTC timezone.
        TZ_PYT: timezone = timezone(timedelta(hours=-4.0))
        self._test_get_datetime_valid_date(8, TZ_PYT)

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
        # Valid filename with invalid date, e.g. September 31.
        VALID_FILENAME_INVALID_DATE: str = self._filename(month=9, day=31)
        with self.assertRaises(ValueError):
            self.locator.get_datetime(VALID_FILENAME_INVALID_DATE)

    def test_match_valid_filename(self) -> None:
        VALID_FILENAME: str = self._filename()
        self.assertTrue(self.locator.match(VALID_FILENAME))

    def test_match_misspelled_prefix(self) -> None:
        INVALID_FILENAME: str = self._filename(prefix="GridCat")
        self.assertFalse(self.locator.match(INVALID_FILENAME))

    def test_match_supported_scenes(self) -> None:
        for scene in self._supported_scenes():
            self.setUpLocator(scene=scene)
            filename: str = self._filename(scene=scene)
            with self.subTest(scene=scene):
                self.assertTrue(self.locator.match(filename))

    def test_match_unsupported_scenes(self) -> None:
        self.setUpLocator(scene=self._supported_scenes()[0])
        for scene in self._unsupported_scenes():
            filename: str = self._filename(scene=scene)
            with self.subTest(scene=scene):
                self.assertFalse(self.locator.match(filename))

    def test_match_supported_origins(self) -> None:
        for origin in self._supported_origins():
            self.setUpLocator(origin=origin)
            filename: str = self._filename(origin=origin)
            with self.subTest(origin=origin):
                self.assertTrue(self.locator.match(filename))

    def test_match_unsupported_origins(self) -> None:
        self.setUpLocator(origin=self._supported_origins()[0])
        for origin in self._unsupported_origins():
            filename: str = self._filename(origin=origin)
            with self.subTest(origin=origin):
                self.assertFalse(self.locator.match(filename))

    def test_match_supported_multi_origins(self) -> None:
        for origin in self._supported_origins():
            filename: str = self._filename(origin=origin)
            with self.subTest(origin=origin):
                self.assertTrue(self.locator.match(filename))

    def test_match_unsupported_multi_origins(self) -> None:
        for origin in self._unsupported_origins():
            filename: str = self._filename(origin=origin)
            with self.subTest(origin=origin):
                self.assertFalse(self.locator.match(filename))

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
        VALID_FILENAME_INVALID_DATE: str = self._filename(month=9, day=31)
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

    def test_match_bad_scene_separator(self) -> None:
        INVALID_FILENAME: str = self._filename().replace("-GOES", "_GOES")
        self.assertFalse(self.locator.match(INVALID_FILENAME))

    def test_match_bad_origin_separator(self) -> None:
        INVALID_FILENAME: str = self._filename().replace(".goes12", "_goes12")
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
        INVALID_FILENAME: str = self._filename().replace(".v01", "_v01")
        self.assertFalse(self.locator.match(INVALID_FILENAME))

    def test_match_bad_suffix_separator(self) -> None:
        INVALID_FILENAME: str = self._filename(suffix="_nc")
        self.assertFalse(self.locator.match(INVALID_FILENAME))

    def test_match_bad_version_prefix(self) -> None:
        INVALID_FILENAME: str = self._filename().replace(".v01", ".b01")
        self.assertFalse(self.locator.match(INVALID_FILENAME))

    def test_get_paths(self) -> None:
        TIME_1: datetime = datetime(1982, 1, 10, 11)
        TIME_2: datetime = datetime(1985, 12, 13, 14)
        for scene in self._supported_scenes():
            self.setUpLocator(scene=scene)
            returned_paths: list[str] = self.locator.get_paths(TIME_1, TIME_2)
            expected_paths: list[str] = [
                self._path(scene, year, month)
                for year in range(1982, 1986)
                for month in range(1, 13)
            ]
            with self.subTest(scene=scene):
                self.assertEqual(returned_paths, expected_paths)

    # ------------------------------------------------------------------

    def _test_get_datetime_valid_date(self, hour: int, tz: timezone) -> None:
        VALID_FILENAME: str = self._filename()
        expected_datetime: datetime = datetime(
            1994, 8, 23, hour, 13, tzinfo=tz
        )
        returned_datetime: datetime = self.locator.get_datetime(VALID_FILENAME)
        self.assertEqual(returned_datetime, expected_datetime)

    # ------------------------------------------------------------------

    @staticmethod
    def _filename(
        prefix: str = "GridSat",
        scene: str = "GOES",
        origin: str = "goes12",
        year: int = 1994,
        month: int = 8,
        day: int = 23,
        hour: int = 12,
        minute: int = 13,
        version: str = "v01",
        suffix: str = ".nc",
    ) -> str:
        # By default returns a valid filename for the GridSat-GOES/CONUS
        # imagery dataset products.
        SCENE_MAPPING: dict[str, str] = {
            "F": "GOES",
            "C": "CONUS",
            "M1": "MESOSCALE1",
            "M2": "MESOSCALE2",
        }
        if scene in SCENE_MAPPING:
            scene = SCENE_MAPPING[scene]
        ORIGIN_MAPPING: dict[str, str] = {
            f"G{id:02d}": f"goes{id:02d}" for id in range(8, 16)
        }
        if origin in ORIGIN_MAPPING:
            origin = ORIGIN_MAPPING[origin]
        return (
            f"{prefix}-{scene}.{origin}."
            f"{year:04d}.{month:02d}.{day:02d}.{hour:02d}{minute:02d}."
            f"{version}{suffix}"
        )

    @classmethod
    def _bad_date_format(cls) -> list[str]:
        BAD_YEAR: str = cls._filename(year=99999)
        BAD_MONTH: str = cls._filename(month=999)
        BAD_DAY: str = cls._filename(day=999)
        BAD_HOUR: str = cls._filename(hour=999)
        BAD_MINUTE: str = cls._filename(minute=999)
        return [BAD_YEAR, BAD_MONTH, BAD_DAY, BAD_HOUR, BAD_MINUTE]

    @classmethod
    def _incomplete_dates(cls) -> list[str]:
        NO_YEAR: str = cls._filename(year=9999).replace(".9999", "")
        NO_MONTH: str = cls._filename(month=99).replace(".99", "")
        NO_DAY: str = cls._filename(day=99).replace(".99", "")
        NO_HOUR: str = cls._filename(hour=99).replace(".99", "")
        NO_MINUTE: str = cls._filename(minute=99).replace("99", "")
        return [NO_YEAR, NO_MONTH, NO_DAY, NO_HOUR, NO_MINUTE]

    @staticmethod
    def _path(scene: str, year: int, month: int) -> str:
        SCENE_MAPPING: dict[str, str] = {"F": "goes", "C": "conus"}
        return f"{SCENE_MAPPING[scene]}/{year:04d}/{month:02d}/"

    # ------------------------------------------------------------------

    @staticmethod
    def _available_datasources() -> dict[str, str]:
        return {
            "AWS": "s3://noaa-cdr-gridsat-goes-pds/data/",
            "Azure": "https://noaa-cdr-gridsat-goes.blob.core.windows.net/"
            "data/",
            "GCP": "gs://noaa-cdr-gridsat-goes/data/",
            "NOAA": "https://www.ncei.noaa.gov/data/gridsat-goes/access/",
        }

    @classmethod
    def _supported_urls(cls) -> dict[str, str]:
        AVAILABLE_DATASOURCES: dict[str, str] = cls._available_datasources()
        SUPPORTED_DATASOURCES: list[str] = cls._supported_datasources()
        return {
            datasource_id: url
            for datasource_id, url in AVAILABLE_DATASOURCES.items()
            if datasource_id in SUPPORTED_DATASOURCES
        }

    @staticmethod
    def _supported_datasources() -> list[str]:
        return ["NOAA"]

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
    def _supported_scenes() -> list[str]:
        return ["F", "C"]

    @staticmethod
    def _unsupported_scenes() -> list[str]:
        return ["M1", "M2"]

    # ------------------------------------------------------------------

    @staticmethod
    def _get_origins(a: int, b: int) -> list[str]:
        return [f"G{n:02d}" for n in range(a, b + 1)]

    @classmethod
    def _supported_origins(cls) -> list[str]:
        return cls._get_origins(8, 15)

    @classmethod
    def _unsupported_origins(cls) -> list[str]:
        AVAILABLE_ORIGINS: list[str] = cls._get_origins(1, 18)
        SUPPORTED_ORIGINS: list[str] = cls._supported_origins()
        return [
            origin
            for origin in AVAILABLE_ORIGINS
            if origin not in SUPPORTED_ORIGINS
        ]

    # ------------------------------------------------------------------

    @staticmethod
    def _supported_versions() -> list[str]:
        return ["v01"]

    @classmethod
    def _unsupported_versions(cls) -> list[str]:
        AVAILABLE_VERSIONS: set[str] = {f"v{v:02}" for v in range(1, 10)}
        SUPPORTED_VERSIONS: list[str] = cls._supported_versions()
        return [
            version
            for version in AVAILABLE_VERSIONS
            if version not in SUPPORTED_VERSIONS
        ]
