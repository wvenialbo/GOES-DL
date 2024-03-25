import unittest

from GOES_DL.product import GOESRSLightningProduct


class TestGOESRSLightningProduct(unittest.TestCase):
    CLASS_NAME = GOESRSLightningProduct.__name__

    def setUp(self) -> None:
        self.available_origin = {
            "G16",
            "G17",
            "G18",
        }
        self.valid_date_format = "%Y%m%d-%H%M%S"
        self.valid_instrument_id = "GLM"  # GOESRSLightningProduct internal
        self.valid_level_id = "L2"  # GOESRSLightningProduct internal
        self.valid_origin_id = "G16"
        self.valid_product_id = "LCFA"  # GOESRSLightningProduct internal
        self.product = GOESRSLightningProduct(
            self.valid_origin_id, self.valid_date_format
        )

    def test_init_invalid_origin_parameter(self) -> None:
        with self.assertRaises(ValueError):
            GOESRSLightningProduct("G08")

    def test_init_invalid_date_format_parameter(self) -> None:
        with self.assertRaises(ValueError):
            product = GOESRSLightningProduct(self.valid_origin_id, "%Y-%k")
            product.get_filename("2024-03")

    def test_default_date_format(self) -> None:
        self.product = GOESRSLightningProduct(self.valid_origin_id)
        self.assertEqual(self.product.date_format, "%Y-%m-%dT%H:%M:%S%z")

    def test_date_format_property(self) -> None:
        self.assertEqual(self.product.date_format, self.valid_date_format)

    def test_instrument_id_property(self) -> None:
        self.assertEqual(self.product.instrument_id, self.valid_instrument_id)

    def test_level_id_property(self) -> None:
        self.assertEqual(self.product.level_id, self.valid_level_id)

    def test_origin_id_property(self) -> None:
        self.assertEqual(self.product.origin_id, self.valid_origin_id)

    def test_product_id_property(self) -> None:
        self.assertEqual(self.product.product_id, self.valid_product_id)

    def test_format_instrument(self) -> None:
        self.assertEqual(
            format(self.product, "instrument"), self.valid_instrument_id
        )

    def test_format_level(self) -> None:
        self.assertEqual(format(self.product, "level"), self.valid_level_id)

    def test_format_origin(self) -> None:
        self.assertEqual(format(self.product, "origin"), self.valid_origin_id)

    def test_format_product(self) -> None:
        self.assertEqual(
            format(self.product, "product"), self.valid_product_id
        )

    def test_format(self) -> None:
        self.assertEqual(format(self.product, ""), str(self.product))

    def test_invalid_format_spec(self) -> None:
        with self.assertRaises(ValueError):
            format(self.product, "invalid")

    def test_available_origin(self) -> None:
        for id in range(16, 19):
            valid_origin_id = f"G{id:02d}"
            self.assertIn(valid_origin_id, self.available_origin)
            GOESRSLightningProduct(origin_id=valid_origin_id)

    def test_unavailable_origin(self) -> None:
        for id in range(8, 16):
            invalid_origin_id = f"G{id:02d}"
            self.assertNotIn(invalid_origin_id, self.available_origin)
            with self.assertRaises(ValueError):
                GOESRSLightningProduct(origin_id=invalid_origin_id)

    def test_repr(self) -> None:
        MODULE_NAME = GOESRSLightningProduct.__module__
        EXPECTED_RESULT = (
            f"<{MODULE_NAME}.{self.CLASS_NAME}("
            f"level_id='{self.valid_level_id}',"
            f"product_id='{self.valid_product_id}',"
            f"instrument_id='{self.valid_instrument_id}',"
            f"origin_id='{self.valid_origin_id}',"
            f"date_format='{self.valid_date_format}'"
            f") at {id(self.product):#x}>"
        )
        repr_result = repr(self.product)
        self.assertEqual(repr_result, EXPECTED_RESULT)

    def test_str(self) -> None:
        EXPECTED_RESULT = (
            f"{self.CLASS_NAME}:\n"
            f"  Origin ID  : '{self.valid_origin_id}'\n"
            f"  Instrument : '{self.valid_instrument_id}'\n"
            f"  Product ID : '{self.valid_product_id}'\n"
            f"  Level      : '{self.valid_level_id}'"
        )
        str_result = str(self.product)
        self.assertEqual(str_result, EXPECTED_RESULT)

    def test_get_baseurl(self) -> None:
        TIMESTAMP = "20240307-203000"
        EXPECTED_BASEURL = (
            "https://noaa-goes16.s3.amazonaws.com/GLM-L2-LCFA/2024/067/20/"
        )
        self.assertEqual(self.product.get_baseurl(TIMESTAMP), EXPECTED_BASEURL)

    def test_get_baseurl_invalid_timestamp(self) -> None:
        TIMESTAMP = "20240307.203000"
        with self.assertRaises(ValueError):
            self.product.get_baseurl(TIMESTAMP)

    def test_get_file_name(self) -> None:
        TIMESTAMP = "20240307-203000"
        EXPECTED_FILE_NAME = (
            "OR_GLM-L2-LCFA_G16_s20240672030000_"
            "e20240672030000_c20240672030000.nc"
        )
        actual_file_name = self.product.get_filename(
            TIMESTAMP, TIMESTAMP, TIMESTAMP
        )
        self.assertEqual(EXPECTED_FILE_NAME, actual_file_name)

    def test_get_filename_without_time_end_and_time_create(self) -> None:
        TIMESTAMP = "20240307-203000"
        with self.assertRaises(ValueError):
            self.product.get_filename(TIMESTAMP, time_end=TIMESTAMP)
        with self.assertRaises(ValueError):
            self.product.get_filename(TIMESTAMP, time_create=TIMESTAMP)
        with self.assertRaises(ValueError):
            self.product.get_filename(TIMESTAMP)

    def test_get_filename_invalid_timestamp(self) -> None:
        TIMESTAMP = "20240307.203000"
        with self.assertRaises(ValueError):
            self.product.get_filename(TIMESTAMP)

    def test_get_file_id(self) -> None:
        EXPECTED_FILE_ID = "GLM-L2-LCFA_G16"
        actual_file_id = self.product.get_file_id()
        self.assertEqual(EXPECTED_FILE_ID, actual_file_id)


if __name__ == "__main__":
    unittest.main()
