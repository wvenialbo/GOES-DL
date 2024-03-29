import unittest
from datetime import datetime, timezone

from GOES_DL.dataset.gridsat import GridSatProductGOES
from GOES_DL.dataset.gridsat.constants import (
    GOES_PRODUCT_DATE_FORMAT,
    GOES_PRODUCT_DATE_PATTERN,
    GOES_PRODUCT_LATEST_VERSION,
    GRIDSAT_FILE_SUFFIX,
    GRIDSAT_PREFIX,
)


class TestGridSatProductGOES(unittest.TestCase):
    # This set of tests covers the initialization of an object of the
    # GridSatProductGOES class, including the handling of invalid
    # parameters. It also tests the get_prefix, get_suffix,
    # get_filename_pattern, get_datetime, timestamp_to_datetime and
    # match methods.

    FILENAME_1 = "GridSat-GOES.goes12.1994.09.01.0010.v01.nc"
    FILENAME_2 = "GridSat-GOES.goes12.2017.12.31.2330.v01.nc"
    FILENAME_3 = "GridSat-CONUS.goes12.1994.09.01.0010.v01.nc"
    FILENAME_4 = "GridSat-GOES.goes13.2017.12.31.2330.v01.nc"
    FILENAME_5 = "GridSat-GOES.goes12.2017.12.31.2330.v02.nc"
    FILENAME_6 = "GridSat-CONUS.goes08.1994.09.01.0010.v01.nc"
    FILENAME_7 = "GridSat-CONUS.goes13.1994.09.01.0010.v01.nc"

    DATETIME_1: datetime = datetime(1994, 9, 1, 0, 10, tzinfo=timezone.utc)
    DATETIME_2: datetime = datetime(2017, 12, 31, 23, 30, tzinfo=timezone.utc)

    def setUp(self) -> None:
        self.product = GridSatProductGOES("F", "G12")

    def test_name_property(self) -> None:
        self.assertEqual(self.product.name, "GOES")

    def test_origin_property(self) -> None:
        self.assertEqual(self.product.origin, ["goes12"])

    def test_version_property(self) -> None:
        self.assertEqual(self.product.version, [GOES_PRODUCT_LATEST_VERSION])

    def test_file_prefix_property(self) -> None:
        self.assertEqual(self.product.file_prefix, GRIDSAT_PREFIX)

    def test_file_suffix_property(self) -> None:
        self.assertEqual(self.product.file_suffix, GRIDSAT_FILE_SUFFIX)

    def test_date_format_property(self) -> None:
        self.assertEqual(self.product.date_format, GOES_PRODUCT_DATE_FORMAT)

    def test_date_pattern_property(self) -> None:
        self.assertEqual(self.product.date_pattern, GOES_PRODUCT_DATE_PATTERN)

    def test_alternative_scene_init(self) -> None:
        product = GridSatProductGOES("C", ["G08", "G13"])
        self.assertEqual(product.name, "CONUS")
        self.assertEqual(product.origin, ["goes08", "goes13"])
        self.assertEqual(
            product.get_prefix(), "GridSat-CONUS.(?:goes08|goes13)."
        )
        self.assertTrue(product.match(self.FILENAME_6))
        self.assertTrue(product.match(self.FILENAME_7))

    def test_invalid_scene(self) -> None:
        with self.assertRaises(ValueError):
            GridSatProductGOES("Z", "G12")

    def test_invalid_origin(self) -> None:
        with self.assertRaises(ValueError):
            GridSatProductGOES("F", "G20")

    def test_invalid_version(self) -> None:
        with self.assertRaises(ValueError):
            GridSatProductGOES("F", "G12", "v02")

    def test_get_prefix(self) -> None:
        expected_prefix = "GridSat-GOES.(?:goes12)."
        self.assertEqual(self.product.get_prefix(), expected_prefix)

    def test_get_suffix(self) -> None:
        expected_suffix = ".(?:v01).nc"
        self.assertEqual(self.product.get_suffix(), expected_suffix)

    def test_get_filename_pattern(self) -> None:
        expected_pattern = (
            r"GridSat-GOES."
            r"(?:goes12).(\d{4}\.\d{2}\.\d{2}\.\d{4})"
            r".(?:v01).nc"
        )
        self.assertEqual(self.product.get_filename_pattern(), expected_pattern)

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

    def test_timestamp_to_datetime(self) -> None:
        timestamp = "1980.01.01.00"
        expected_datetime = datetime(1980, 1, 1, 0, tzinfo=timezone.utc)
        self.assertEqual(
            self.product.timestamp_to_datetime(timestamp), expected_datetime
        )

    def test_match(self) -> None:
        self.assertTrue(self.product.match(self.FILENAME_1))
        self.assertTrue(self.product.match(self.FILENAME_2))

    def test_match_invalid_filename(self) -> None:
        self.assertFalse(self.product.match(self.FILENAME_3))
        self.assertFalse(self.product.match(self.FILENAME_4))
        self.assertFalse(self.product.match(self.FILENAME_5))


if __name__ == "__main__":
    unittest.main()
