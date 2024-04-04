import unittest
from datetime import datetime, timezone

from GOES_DL.dataset import Product
from GOES_DL.dataset.gridsat import GridSatProductB1
from GOES_DL.dataset.gridsat.constants import (
    B1_GRIDSAT_PREFIX,
    B1_PRODUCT_DATE_FORMAT,
    B1_PRODUCT_DATE_PATTERN,
    B1_PRODUCT_LATEST_VERSION,
    B1_PRODUCT_NAME,
    B1_PRODUCT_ORIGIN,
)


class TestGridSatProductB1(unittest.TestCase):
    # This set of tests covers the initialization of an object of the
    # GridSatProductB1 class, including the handling of invalid
    # parameters. It also tests the get_prefix, get_suffix,
    # get_filename_pattern, get_datetime, timestamp_to_datetime and
    # match methods.

    # Valid filename
    FILENAME_1: str = "GRIDSAT-B1.2020.08.23.14.v02r01.nc"

    # Filename with invalid product name
    FILENAME_2: str = "GRIDSAT-GOES.1980.01.01.00.v02r01.nc"

    # Filename with invalid timestamp format
    FILENAME_3: str = "GRIDSAT-B1.2023.09.30.2100.v02r01.nc"

    # Filename with unsupported version
    FILENAME_4: str = "GRIDSAT-B1.1980.01.01.00.v01r01.nc"

    DATETIME_1: datetime = datetime(2020, 8, 23, 14, tzinfo=timezone.utc)

    VALID_VERSION = B1_PRODUCT_LATEST_VERSION

    def setUp(self) -> None:
        self.product: GridSatProductB1 = GridSatProductB1()

    def test_init_is_product(self) -> None:
        self.assertIsInstance(self.product, Product)

    def test_init_is_product_b1(self) -> None:
        self.assertIsInstance(self.product, GridSatProductB1)

    def test_init_invalid_version(self) -> None:
        with self.assertRaises(ValueError):
            GridSatProductB1(version="v01r01")

    def test_init_available_versions(self) -> None:
        for version in [self.VALID_VERSION]:
            product: GridSatProductB1 = GridSatProductB1(version=version)
            self.assertEqual(product.version, [version])

    def test_name_property(self) -> None:
        self.assertEqual(self.product.name, B1_PRODUCT_NAME)

    def test_origin_property(self) -> None:
        self.assertEqual(self.product.origin, B1_PRODUCT_ORIGIN)

    def test_version_property(self) -> None:
        self.assertEqual(self.product.version, [self.VALID_VERSION])

    def test_file_prefix_property(self) -> None:
        self.assertEqual(self.product.file_prefix, B1_GRIDSAT_PREFIX)

    def test_date_format_property(self) -> None:
        self.assertEqual(self.product.date_format, B1_PRODUCT_DATE_FORMAT)

    def test_date_pattern_property(self) -> None:
        self.assertEqual(self.product.date_pattern, B1_PRODUCT_DATE_PATTERN)

    def test_invalid_version(self) -> None:
        expected_value: str = "v01r01"
        unsupported_version: str = self.product.invalid_version(
            [expected_value]
        )
        self.assertEqual(unsupported_version, expected_value)

    def test_available_versions(self) -> None:
        valid_version: str = self.VALID_VERSION
        expected_value: str = ""
        returned_value: str = self.product.invalid_version([valid_version])
        self.assertEqual(returned_value, expected_value)

    def test_get_prefix(self) -> None:
        expected_prefix: str = "GRIDSAT-B1."
        self.assertEqual(self.product.get_prefix(), expected_prefix)

    def test_get_suffix(self) -> None:
        expected_suffix: str = f".(?:{self.VALID_VERSION}).nc"
        self.assertEqual(self.product.get_suffix(), expected_suffix)

    def test_get_filename_pattern(self) -> None:
        expected_pattern: str = (
            r"GRIDSAT-B1."
            r"(\d{4}\.\d{2}\.\d{2}\.\d{2})"
            rf".(?:{self.VALID_VERSION}).nc"
        )
        self.assertEqual(self.product.get_filename_pattern(), expected_pattern)

    def test_get_datetime(self) -> None:
        self.assertEqual(
            self.product.get_datetime(self.FILENAME_1), self.DATETIME_1
        )

    def test_get_datetime_invalid_filename(self) -> None:
        with self.assertRaises(ValueError):
            self.product.get_datetime(self.FILENAME_3)

    def test_timestamp_to_datetime(self) -> None:
        timestamp: str = "1980.01.01.00"
        expected_datetime: datetime = datetime(
            1980, 1, 1, 0, tzinfo=timezone.utc
        )
        self.assertEqual(
            self.product.timestamp_to_datetime(timestamp), expected_datetime
        )

    def test_match(self) -> None:
        self.assertTrue(self.product.match(self.FILENAME_1))

    def test_match_invalid_name_filename(self) -> None:
        self.assertFalse(self.product.match(self.FILENAME_2))

    def test_match_invalid_timestamp_filename(self) -> None:
        self.assertFalse(self.product.match(self.FILENAME_3))

    def test_match_invalid_version_filename(self) -> None:
        self.assertFalse(self.product.match(self.FILENAME_4))
