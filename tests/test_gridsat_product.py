import unittest
from datetime import datetime, timezone

from GOES_DL.dataset.gridsat.product import GridSatProduct


class TestGridSatProduct(unittest.TestCase):
    # This set of tests covers the initialization of an object of the
    # GridSatProduct class. It also tests the get_prefix, get_suffix,
    # get_filename_pattern, get_datetime, timestamp_to_datetime and
    # match methods.

    FILENAME_1: str = "GRIDSAT-B1.meteosat.1980.01.01.00.v02r01.nc"
    FILENAME_2: str = "GRIDSAT-B1.meteosat.2023.09.30.21.v02r01.nc"
    FILENAME_3: str = "GRIDSAT-B1.1980.01.01.00.v02r01.nc"
    FILENAME_4: str = "GRIDSAT-B1.meteosat.2023.09.30.21.v01.nc"
    FILENAME_5: str = "GRIDSAT-B1.meteosat.2023.09.30.2100.v02r01.nc"

    DATETIME_1: datetime = datetime(1980, 1, 1, 0, tzinfo=timezone.utc)
    DATETIME_2: datetime = datetime(2023, 9, 30, 21, tzinfo=timezone.utc)

    NAME: str = "B1"
    ORIGIN: list[str] = ["meteosat"]
    VERSION: list[str] = ["v02r01"]
    FILE_PREFIX: str = "GRIDSAT"
    FILE_SUFFIX: str = ".nc"
    DATE_FORMAT: str = "%Y.%m.%d.%H"
    DATE_PATTERN: str = r"\d{4}\.\d{2}\.\d{2}\.\d{2}"

    def setUp(self) -> None:
        self.product: GridSatProduct = GridSatProduct(
            name=self.NAME,
            origin=self.ORIGIN,
            version=self.VERSION,
            file_prefix=self.FILE_PREFIX,
            date_format=self.DATE_FORMAT,
            date_pattern=self.DATE_PATTERN,
        )

    def test_name_property(self) -> None:
        self.assertEqual(self.product.name, self.NAME)

    def test_origin_property(self) -> None:
        self.assertEqual(self.product.origin, self.ORIGIN)

    def test_version_property(self) -> None:
        self.assertEqual(self.product.version, self.VERSION)

    def test_file_prefix_property(self) -> None:
        self.assertEqual(self.product.file_prefix, self.FILE_PREFIX)

    def test_date_format_property(self) -> None:
        self.assertEqual(self.product.date_format, self.DATE_FORMAT)

    def test_date_pattern_property(self) -> None:
        self.assertEqual(self.product.date_pattern, self.DATE_PATTERN)

    def test_get_prefix(self) -> None:
        expected_prefix = "GRIDSAT-B1.(?:meteosat)."
        self.assertEqual(self.product.get_prefix(), expected_prefix)

    def test_get_suffix(self) -> None:
        expected_suffix = ".(?:v02r01).nc"
        self.assertEqual(self.product.get_suffix(), expected_suffix)

    def test_get_filename_pattern(self) -> None:
        expected_pattern = (
            r"GRIDSAT-B1.(?:meteosat)."
            r"(\d{4}\.\d{2}\.\d{2}\.\d{2})"
            r".(?:v02r01).nc"
        )
        self.assertEqual(self.product.get_filename_pattern(), expected_pattern)

    def test_timestamp_to_datetime(self) -> None:
        timestamp = "1980.01.01.00"
        expected_datetime = datetime(1980, 1, 1, 0, tzinfo=timezone.utc)
        self.assertEqual(
            self.product.timestamp_to_datetime(timestamp), expected_datetime
        )

    def test_get_datetime(self) -> None:
        self.assertEqual(
            self.product.get_datetime(self.FILENAME_1), self.DATETIME_1
        )
        self.assertEqual(
            self.product.get_datetime(self.FILENAME_2), self.DATETIME_2
        )

    def test_get_datetime_invalid_filename(self) -> None:
        with self.assertRaises(ValueError):
            self.product.get_datetime(self.FILENAME_3)
            self.product.get_datetime(self.FILENAME_4)
            self.product.get_datetime(self.FILENAME_5)

    def test_match(self) -> None:
        self.assertTrue(self.product.match(self.FILENAME_1))
        self.assertTrue(self.product.match(self.FILENAME_2))

    def test_match_invalid_filename(self) -> None:
        self.assertFalse(self.product.match(self.FILENAME_3))
        self.assertFalse(self.product.match(self.FILENAME_4))
        self.assertFalse(self.product.match(self.FILENAME_5))
