import unittest

from GOES_DL.product import GOES2GImagerProduct


class TestGOES2GImagerProduct(unittest.TestCase):
    CLASS_NAME = GOES2GImagerProduct.__name__

    def setUp(self) -> None:
        self.valid_origin_id = "G08"
        self.valid_scene_id = "F"
        self.valid_version = "v01"
        self.valid_product_id = "MCMIP"  # GOES2GImagerProduct internal
        self.available_origin = {
            "G08",
            "G09",
            "G10",
            "G11",
            "G12",
            "G13",
            "G14",
            "G15",
        }
        self.valid_date_format = "%Y%m%d-%H%M%S"
        self.product = GOES2GImagerProduct(
            self.valid_scene_id,
            self.valid_origin_id,
            self.valid_version,
            self.valid_date_format,
        )

    def test_init_invalid_origin_parameter(self) -> None:
        invalid_origin_id = "G20"
        with self.assertRaises(ValueError):
            GOES2GImagerProduct(
                self.valid_scene_id, invalid_origin_id, self.valid_version
            )

    def test_init_invalid_scene_parameter(self) -> None:
        invalid_scene_id = "M1"
        with self.assertRaises(ValueError):
            GOES2GImagerProduct(
                invalid_scene_id, self.valid_origin_id, self.valid_version
            )

    def test_init_invalid_version_parameter(self) -> None:
        invalid_scene_id = "v02"
        with self.assertRaises(ValueError):
            GOES2GImagerProduct(
                self.valid_scene_id, self.valid_origin_id, invalid_scene_id
            )

    def test_default_date_format(self) -> None:
        self.product = GOES2GImagerProduct(
            self.valid_scene_id,
            self.valid_origin_id,
            self.valid_version,
        )
        self.assertEqual(self.product.date_format, "%Y-%m-%dT%H:%M:%S%z")

    def test_date_format_property(self) -> None:
        self.assertEqual(self.product.date_format, self.valid_date_format)

    def test_product_id_property(self) -> None:
        self.assertEqual(self.product.product_id, self.valid_product_id)

    def test_origin_id_property(self) -> None:
        self.assertEqual(self.product.origin_id, self.valid_origin_id)

    def test_scene_id_property(self) -> None:
        self.assertEqual(self.product.scene_id, self.valid_scene_id)

    def test_version_property(self) -> None:
        self.assertEqual(self.product.version, self.valid_version)

    def test_available_origin(self) -> None:
        for id in range(8, 16):
            valid_origin_id = f"G{id:02d}"
            self.assertIn(valid_origin_id, self.available_origin)
            GOES2GImagerProduct(origin_id=valid_origin_id)

    def test_unavailable_origin(self) -> None:
        for id in range(16, 20):
            invalid_origin_id = f"G{id:02d}"
            self.assertNotIn(invalid_origin_id, self.available_origin)
            with self.assertRaises(ValueError):
                GOES2GImagerProduct(origin_id=invalid_origin_id)

    def test_available_scene(self) -> None:
        for valid_scene_id in ["F", "C"]:
            self.assertIn(valid_scene_id, GOES2GImagerProduct.AVAILABLE_SCENE)
            GOES2GImagerProduct(valid_scene_id, self.valid_origin_id)

    def test_unavailable_scene(self) -> None:
        for invalid_scene_id in {"M1", "M2"}:
            self.assertNotIn(
                invalid_scene_id, GOES2GImagerProduct.AVAILABLE_SCENE
            )
            with self.assertRaises(ValueError):
                GOES2GImagerProduct(invalid_scene_id, self.valid_origin_id)

    def test_available_version(self) -> None:
        for valid_vernum in range(1, 2):
            valid_version = f"v{valid_vernum:02d}"
            self.assertIn(
                f"{valid_version}", GOES2GImagerProduct.AVAILABLE_VERSION
            )
            GOES2GImagerProduct(
                self.valid_scene_id, self.valid_origin_id, valid_version
            )

    def test_unavailable_version(self) -> None:
        for invalid_vernum in range(2, 6):
            invalid_version = f"v{invalid_vernum:02d}"
            self.assertNotIn(
                invalid_version, GOES2GImagerProduct.AVAILABLE_VERSION
            )
            with self.assertRaises(ValueError):
                GOES2GImagerProduct(
                    self.valid_scene_id, self.valid_origin_id, invalid_version
                )

    def test_format_origin(self) -> None:
        self.assertEqual(format(self.product, "origin"), self.valid_origin_id)

    def test_format_product(self) -> None:
        self.assertEqual(
            format(self.product, "product"), self.valid_product_id
        )

    def test_format_scene(self) -> None:
        self.assertEqual(format(self.product, "scene"), self.valid_scene_id)

    def test_format_version(self) -> None:
        self.assertEqual(format(self.product, "version"), self.valid_version)

    def test_format(self) -> None:
        self.assertEqual(format(self.product, ""), str(self.product))

    def test_invalid_format_spec(self) -> None:
        with self.assertRaises(ValueError):
            format(self.product, "invalid")

    def test_repr(self) -> None:
        MODULE_NAME = GOES2GImagerProduct.__module__
        EXPECTED_RESULT = (
            f"<{MODULE_NAME}.{self.CLASS_NAME}("
            f"origin_id='{self.valid_origin_id}',"
            f"product_id='{self.valid_product_id}',"
            f"scene_id='{self.valid_scene_id}',"
            f"version='{self.valid_version}',"
            f"date_format='{self.valid_date_format}'"
            f") at {id(self.product):#x}>"
        )
        repr_result = repr(self.product)
        self.assertEqual(repr_result, EXPECTED_RESULT)

    def test_str(self) -> None:
        EXPECTED_RESULT = (
            f"{self.CLASS_NAME}:\n"
            f"  Origin ID  : '{self.valid_origin_id}'\n"
            f"  Product ID : '{self.valid_product_id}'\n"
            f"  Scene ID   : '{self.valid_scene_id}'\n"
            f"  Version    : '{self.valid_version}'"
        )
        str_result = str(self.product)
        self.assertEqual(str_result, EXPECTED_RESULT)

    def test_get_baseurl(self) -> None:
        TIMESTAMP = "20240307-203000"
        EXPECTED_BASEURL = (
            "https://www.ncei.noaa.gov/data/gridsat-goes/access/goes/2024/03/"
        )
        self.assertEqual(self.product.get_baseurl(TIMESTAMP), EXPECTED_BASEURL)

    def test_get_baseurl_invalid_timestamp(self) -> None:
        TIMESTAMP = "20240307.203000"
        with self.assertRaises(ValueError):
            self.product.get_baseurl(TIMESTAMP)

    def test_get_file_name(self) -> None:
        TIMESTAMP = "20240307-203000"
        EXPECTED_FILE_NAME = "GridSat-GOES.goes08.2024.03.07.2030.v01.nc"
        actual_file_name = self.product.get_filename(TIMESTAMP)
        self.assertEqual(EXPECTED_FILE_NAME, actual_file_name)

    def test_get_filename_with_time_end_and_time_create(self) -> None:
        TIMESTAMP = "20240307-203000"
        with self.assertRaises(ValueError):
            self.product.get_filename(TIMESTAMP, time_end=TIMESTAMP)
        with self.assertRaises(ValueError):
            self.product.get_filename(TIMESTAMP, time_create=TIMESTAMP)
        with self.assertRaises(ValueError):
            self.product.get_filename(TIMESTAMP, TIMESTAMP, TIMESTAMP)

    def test_get_filename_invalid_timestamp(self) -> None:
        TIMESTAMP = "20240307.203000"
        with self.assertRaises(ValueError):
            self.product.get_filename(TIMESTAMP)

    def test_get_file_id(self) -> None:
        EXPECTED_FILE_ID = "GridSat-GOES.goes08.v01"
        actual_file_id = self.product.get_file_id()
        self.assertEqual(EXPECTED_FILE_ID, actual_file_id)


if __name__ == "__main__":
    unittest.main()
