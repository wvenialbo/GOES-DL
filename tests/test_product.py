import unittest
from datetime import datetime

from GOES_DL.product import GOESProduct


class GOESProductTest(GOESProduct):
    def get_baseurl(self, timestamp: str) -> str:
        date_obj: datetime = datetime.strptime(timestamp, self._date_format)
        date: str = date_obj.strftime("%Y/%m")
        return f"https://path/to/{date}/"

    def get_filename(
        self, time_start: str, time_end: str = "", time_create: str = ""
    ) -> str:
        if time_create:
            raise ValueError("time_create parameter is not supported")
        if time_end:
            raise ValueError("time_end parameter is not supported")
        date_obj: datetime = datetime.strptime(time_start, self._date_format)
        date: str = date_obj.strftime("%Y.%m.%d.%H%M")
        return f"{self.get_file_id()}.{date}.nc"

    def get_file_id(self) -> str:
        return f"{self.origin_id}.{self.product_id}"


class TestGOESProduct(unittest.TestCase):
    CLASS_NAME = GOESProductTest.__name__

    def setUp(self) -> None:
        self.valid_origin_id = "G16"  # Unchecked by GOESProduct
        self.valid_product_id = "MCMIP"  # Unchecked by GOESProduct
        self.valid_date_format = "%Y%m%d-%H%M%S"
        self.product = GOESProductTest(
            self.valid_product_id, self.valid_origin_id, self.valid_date_format
        )

    def test_default_date_format(self) -> None:
        self.product = GOESProductTest(
            self.valid_product_id, self.valid_origin_id
        )
        self.assertEqual(self.product.date_format, "%Y-%m-%dT%H:%M:%S%z")

    def test_date_format_property(self) -> None:
        self.assertEqual(self.product.date_format, self.valid_date_format)

    def test_origin_id_property(self) -> None:
        self.assertEqual(self.product.origin_id, self.valid_origin_id)

    def test_product_id_property(self) -> None:
        self.assertEqual(self.product.product_id, self.valid_product_id)

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

    def test_repr(self) -> None:
        MODULE_NAME = GOESProductTest.__module__
        EXPECTED_RESULT = (
            f"<{MODULE_NAME}.{self.CLASS_NAME}("
            f"origin_id='{self.valid_origin_id}',"
            f"product_id='{self.valid_product_id}',"
            f"date_format='{self.valid_date_format}'"
            f") at {id(self.product):#x}>"
        )
        repr_result = repr(self.product)
        self.assertEqual(repr_result, EXPECTED_RESULT)

    def test_str(self) -> None:
        EXPECTED_RESULT = (
            f"{self.CLASS_NAME}:\n"
            f"  Origin ID  : '{self.valid_origin_id}'\n"
            f"  Product ID : '{self.valid_product_id}'"
        )
        str_result = str(self.product)
        self.assertEqual(str_result, EXPECTED_RESULT)

    def test_get_baseurl(self) -> None:
        TIMESTAMP = "20240307-203000"
        EXPECTED_BASEURL = "https://path/to/2024/03/"
        self.assertEqual(self.product.get_baseurl(TIMESTAMP), EXPECTED_BASEURL)

    def test_get_baseurl_invalid_timestamp(self) -> None:
        TIMESTAMP = "20240307.203000"
        with self.assertRaises(ValueError):
            self.product.get_baseurl(TIMESTAMP)

    def test_get_filename(self) -> None:
        TIMESTAMP = "20240307-203000"
        EXPECTED_FILENAME = (
            f"{self.valid_origin_id}.{self.valid_product_id}."
            "2024.03.07.2030.nc"
        )
        self.assertEqual(
            self.product.get_filename(TIMESTAMP), EXPECTED_FILENAME
        )

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
        EXPECTED_FILE_ID = f"{self.valid_origin_id}.{self.valid_product_id}"
        self.assertEqual(self.product.get_file_id(), EXPECTED_FILE_ID)


if __name__ == "__main__":
    unittest.main()
