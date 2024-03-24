import unittest

from GOES_DL.product import GOES2GImagerProduct


class TestGOES2GImagerProduct(unittest.TestCase):
    CLASS_NAME = GOES2GImagerProduct.__name__

    def setUp(self) -> None:
        self.valid_origin_id = "G08"
        self.valid_scene_id = "F"
        self.valid_version = "1"
        self.valid_product_id = GOES2GImagerProduct.AVAILABLE_PRODUCT[0]
        self.available_origin = GOES2GImagerProduct.AVAILABLE_ORIGIN
        self.product = GOES2GImagerProduct(
            self.valid_origin_id, self.valid_scene_id, self.valid_version
        )

    def test_init_valid_parameters(self) -> None:
        self.assertEqual(self.product.product_id, self.valid_product_id)
        self.assertEqual(self.product.origin_id, self.valid_origin_id)
        self.assertEqual(self.product.scene_id, self.valid_scene_id)
        self.assertEqual(self.product.version, self.valid_version)

    def test_init_invalid_origin(self) -> None:
        invalid_origin_id = "G20"
        with self.assertRaises(ValueError):
            GOES2GImagerProduct(
                invalid_origin_id, self.valid_scene_id, self.valid_version
            )

    def test_init_invalid_scene(self) -> None:
        invalid_scene_id = "Z"
        with self.assertRaises(ValueError):
            GOES2GImagerProduct(
                self.valid_origin_id, invalid_scene_id, self.valid_version
            )

    def test_init_invalid_version(self) -> None:
        invalid_scene_id = "2"
        with self.assertRaises(ValueError):
            GOES2GImagerProduct(
                self.valid_origin_id, self.valid_scene_id, invalid_scene_id
            )

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
            GOES2GImagerProduct(valid_origin_id)

    def test_unavailable_origin(self) -> None:
        for id in range(16, 20):
            invalid_origin_id = f"G{id:02d}"
            self.assertNotIn(invalid_origin_id, self.available_origin)
            with self.assertRaises(ValueError):
                GOES2GImagerProduct(invalid_origin_id)

    def test_available_scene(self) -> None:
        for valid_scene_id in ["F", "C"]:
            self.assertIn(valid_scene_id, GOES2GImagerProduct.AVAILABLE_SCENE)
            GOES2GImagerProduct(self.valid_origin_id, valid_scene_id)

    def test_unavailable_scene(self) -> None:
        for invalid_scene_id in {"M1", "M2"}:
            self.assertNotIn(
                invalid_scene_id, GOES2GImagerProduct.AVAILABLE_SCENE
            )
            with self.assertRaises(ValueError):
                GOES2GImagerProduct(self.valid_origin_id, invalid_scene_id)

    def test_available_version(self) -> None:
        for valid_vernum in range(1, 2):
            valid_version = f"{valid_vernum}"
            self.assertIn(
                f"{valid_version}", GOES2GImagerProduct.AVAILABLE_VERSION
            )
            GOES2GImagerProduct(
                self.valid_origin_id, self.valid_scene_id, valid_version
            )

    def test_unavailable_version(self) -> None:
        for invalid_vernum in range(2, 6):
            invalid_version = f"{invalid_vernum}"
            self.assertNotIn(
                invalid_version, GOES2GImagerProduct.AVAILABLE_VERSION
            )
            with self.assertRaises(ValueError):
                GOES2GImagerProduct(
                    self.valid_origin_id, self.valid_scene_id, invalid_version
                )

    def test_get_baseurl(self) -> None:
        TIMESTAMP = "20220101102030"
        EXPECTED_BASEURL = (
            "https://www.ncei.noaa.gov/data/gridsat-goes/access/goes/2022/01"
        )
        self.assertEqual(self.product.get_baseurl(TIMESTAMP), EXPECTED_BASEURL)

    def test_get_file_name(self) -> None:
        TIMESTAMP = "20220101102030"
        EXPECTED_FILE_NAME = "GridSat-GOES.goes08.2022.01.01.1020.v01.nc"
        actual_file_name = self.product.get_filename(TIMESTAMP)
        self.assertEqual(EXPECTED_FILE_NAME, actual_file_name)

    def test_get_baseurl_with_different_scene_and_timestamp(self) -> None:
        TIMESTAMP = "20201231201045"
        SCENE_ID = "C"
        EXPECTED_BASEURL = (
            "https://www.ncei.noaa.gov/data/gridsat-goes/access/conus/2020/12"
        )
        product = GOES2GImagerProduct(
            self.valid_origin_id, SCENE_ID, self.valid_version
        )
        self.assertEqual(product.get_baseurl(TIMESTAMP), EXPECTED_BASEURL)

    def test_get_file_name_with_different_scene_origin_and_timestamp(
        self,
    ) -> None:
        TIMESTAMP = "20201231201045"
        EXPECTED_FILE_NAME = "GridSat-CONUS.goes13.2020.12.31.2010.v01.nc"
        valid_origin_id = "G13"
        valid_scene_id = "C"
        self.product = GOES2GImagerProduct(
            valid_origin_id, valid_scene_id, self.valid_version
        )
        actual_file_name = self.product.get_filename(TIMESTAMP)
        self.assertEqual(EXPECTED_FILE_NAME, actual_file_name)

    def test_format(self) -> None:
        self.assertEqual(
            format(self.product, "product"), self.valid_product_id
        )
        self.assertEqual(format(self.product, "origin"), self.valid_origin_id)
        self.assertEqual(format(self.product, ""), str(self.product))
        with self.assertRaises(ValueError):
            format(self.product, "invalid")

    def test_repr(self) -> None:
        MODULE_NAME = GOES2GImagerProduct.__module__
        EXPECTED_REPR = (
            f"<{MODULE_NAME}.{self.CLASS_NAME}("
            f"product_id='{self.valid_product_id}',"
            f"origin_id='{self.valid_origin_id}',"
            f"scene_id='{self.valid_scene_id}',"
            f"version='{self.valid_version}'"
            ") at 0x"
        )
        repr_result = repr(self.product)
        self.assertTrue(repr_result.startswith(EXPECTED_REPR))
        self.assertTrue(repr_result.endswith(">"))

    def test_str(self) -> None:
        EXPECTED_STR = (
            f"{self.CLASS_NAME}:\n"
            f"  Product ID : '{self.valid_product_id}'\n"
            f"  Origin ID  : '{self.valid_origin_id}'\n"
            f"  Scene ID   : '{self.valid_scene_id}'\n"
            f"  Version    : 'v{int(self.valid_version):02d}'"
        )
        str_result = str(self.product)
        expected_result = EXPECTED_STR
        self.assertEqual(str_result, expected_result)


if __name__ == "__main__":
    unittest.main()
