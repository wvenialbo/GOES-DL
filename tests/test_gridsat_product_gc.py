import unittest
from datetime import datetime, timezone

from ..GOES_DL.dataset import ProductBase
from ..GOES_DL.dataset.gridsat import GridSatProductGC
from ..GOES_DL.dataset.gridsat.constants import (
    GOES_GRIDSAT_PREFIX,
    GOES_PRODUCT_DATE_FORMAT,
    GOES_PRODUCT_DATE_PATTERN,
    GOES_PRODUCT_LATEST_VERSION,
    GRIDSAT_FILE_SUFFIX,
)


class TestGridSatProductGC(unittest.TestCase):
    # This set of tests covers the initialization of an object of the
    # GridSatProductGOES class, including the handling of invalid
    # parameters. It also tests the get_prefix, get_suffix,
    # get_filename_pattern, get_datetime, timestamp_to_datetime and
    # match methods.

    # Valid filenames
    FILENAME_1 = "GridSat-GOES.goes12.1994.08.23.1213.v01.nc"
    FILENAME_2 = "GridSat-GOES.goes13.1994.08.23.1213.v01.nc"

    # Filename with invalid product name
    FILENAME_3 = "GridSat-CONUS.goes12.1994.08.23.1213.v01.nc"

    # Filename with invalid timestamp format
    FILENAME_4 = "GridSat-GOES.goes12.1994.08.23.12.v01.nc"

    # Filename with unsupported version
    FILENAME_5 = "GridSat-GOES.goes12.1994.08.23.1213.v02.nc"

    DATETIME_1: datetime = datetime(1994, 8, 23, 12, 13, tzinfo=timezone.utc)

    VALID_SCENE = "F"
    VALID_NAME = "GOES"
    VALID_ORIGID = "G12"
    VALID_ORIGIN = "goes12"
    VALID_VERSION = "v01"

    MULTI_ORIGIN = ["G12", "G13"]
    MULTI_NAME = ["goes12", "goes13"]

    def setUp(self) -> None:
        self.product: GridSatProductGC = GridSatProductGC(
            self.VALID_SCENE, self.VALID_ORIGID
        )

    def test_init_is_product(self) -> None:
        self.assertIsInstance(self.product, ProductBase)

    def test_init_is_product_goes(self) -> None:
        self.assertIsInstance(self.product, GridSatProductGC)

    def test_init_invalid_scene(self) -> None:
        with self.assertRaises(ValueError):
            GridSatProductGC("Z", self.VALID_ORIGID)

    def test_init_invalid_origin(self) -> None:
        with self.assertRaises(ValueError):
            GridSatProductGC(self.VALID_SCENE, "G20")

    def test_init_invalid_version(self) -> None:
        with self.assertRaises(ValueError):
            GridSatProductGC(self.VALID_SCENE, self.VALID_ORIGID, "v02")

    def test_init_available_scenes(self) -> None:
        for name, scene in zip(["CONUS", "GOES"], ["C", "F"]):
            product: GridSatProductGC = GridSatProductGC(
                scene, self.VALID_ORIGID
            )
            self.assertEqual(product.name, name)

    def test_init_available_origins(self) -> None:
        orig_ids: list[str] = [f"G{i:02d}" for i in range(8, 16)]
        orig_names: list[str] = [f"goes{i:02d}" for i in range(8, 16)]
        for name, orig in zip(orig_names, orig_ids):
            product: GridSatProductGC = GridSatProductGC(
                self.VALID_SCENE, orig
            )
            self.assertEqual(product.origin, [name])

    def test_init_available_versions(self) -> None:
        for version in [self.VALID_VERSION]:
            product: GridSatProductGC = GridSatProductGC(
                self.VALID_SCENE, self.VALID_ORIGID, version
            )
            self.assertEqual(product.version, [version])

    def test_name_property(self) -> None:
        self.assertEqual(self.product.name, self.VALID_NAME)

    def test_origin_property(self) -> None:
        self.assertEqual(self.product.origin, [self.VALID_ORIGIN])

    def test_multiple_origins_property(self) -> None:
        product: GridSatProductGC = GridSatProductGC(
            self.VALID_SCENE, self.MULTI_ORIGIN
        )
        self.assertEqual(product.origin, self.MULTI_NAME)

    def test_version_property(self) -> None:
        self.assertEqual(self.product.version, [GOES_PRODUCT_LATEST_VERSION])

    def test_file_prefix_property(self) -> None:
        self.assertEqual(self.product.file_prefix, GOES_GRIDSAT_PREFIX)

    def test_file_suffix_property(self) -> None:
        self.assertEqual(self.product.file_suffix, GRIDSAT_FILE_SUFFIX)

    def test_date_format_property(self) -> None:
        self.assertEqual(self.product.date_format, GOES_PRODUCT_DATE_FORMAT)

    def test_date_pattern_property(self) -> None:
        self.assertEqual(self.product.date_pattern, GOES_PRODUCT_DATE_PATTERN)

    def test_invalid_scene(self) -> None:
        expected_value: str = "Z"
        unavailable_scene: str = self.product.invalid_scene([expected_value])
        self.assertEqual(unavailable_scene, expected_value)

    def test_invalid_origin(self) -> None:
        expected_value: str = "G20"
        unavailable_product: str = self.product.invalid_origin(
            [expected_value]
        )
        self.assertEqual(unavailable_product, expected_value)

    def test_invalid_version(self) -> None:
        expected_value: str = "v02"
        unsupported_version: str = self.product.invalid_version(
            [expected_value]
        )
        self.assertEqual(unsupported_version, expected_value)

    def test_available_scenes(self) -> None:
        available_scenes: list[str] = ["C", "F"]
        expected_value: str = ""
        returned_value: str = self.product.invalid_scene(available_scenes)
        self.assertEqual(returned_value, expected_value)

    def test_available_origins(self) -> None:
        available_origins: list[str] = [f"G{i:02d}" for i in range(8, 16)]
        expected_value: str = ""
        returned_value: str = self.product.invalid_origin(available_origins)
        self.assertEqual(returned_value, expected_value)

    def test_available_versions(self) -> None:
        available_versions: list[str] = ["v01"]
        expected_value: str = ""
        returned_value: str = self.product.invalid_version(available_versions)
        self.assertEqual(returned_value, expected_value)

    def test_get_prefix(self) -> None:
        expected_prefix: str = (
            f"GridSat-{self.VALID_NAME}.(?:{self.VALID_ORIGIN})."
        )
        self.assertEqual(self.product.get_prefix(), expected_prefix)

    def test_get_prefix_multiple_origins(self) -> None:
        origins: str = "|".join(self.MULTI_NAME)
        expected_prefix: str = f"GridSat-{self.VALID_NAME}.(?:{origins})."
        product: GridSatProductGC = GridSatProductGC(
            self.VALID_SCENE, self.MULTI_ORIGIN
        )
        self.assertEqual(product.get_prefix(), expected_prefix)

    def test_get_suffix(self) -> None:
        expected_suffix: str = f".(?:{self.VALID_VERSION}).nc"
        self.assertEqual(self.product.get_suffix(), expected_suffix)

    def test_get_filename_pattern(self) -> None:
        expected_pattern: str = (
            rf"GridSat-{self.VALID_NAME}."
            rf"(?:{self.VALID_ORIGIN})."
            r"(\d{4}\.\d{2}\.\d{2}\.\d{4})"
            rf".(?:{self.VALID_VERSION}).nc"
        )
        self.assertEqual(self.product.get_filename_pattern(), expected_pattern)

    def test_get_datetime(self) -> None:
        self.assertEqual(
            self.product.get_datetime(self.FILENAME_1), self.DATETIME_1
        )

    def test_get_datetime_invalid_filename(self) -> None:
        with self.assertRaises(ValueError):
            self.product.get_datetime(self.FILENAME_4)

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
        self.assertFalse(self.product.match(self.FILENAME_3))

    def test_match_invalid_timestamp_filename(self) -> None:
        self.assertFalse(self.product.match(self.FILENAME_4))

    def test_match_invalid_version_filename(self) -> None:
        self.assertFalse(self.product.match(self.FILENAME_5))

    def test_match_multiple_origins(self) -> None:
        product: GridSatProductGC = GridSatProductGC(
            self.VALID_SCENE, self.MULTI_ORIGIN
        )
        self.assertTrue(
            product.match(self.FILENAME_1) and product.match(self.FILENAME_2)
        )


if __name__ == "__main__":
    unittest.main()
