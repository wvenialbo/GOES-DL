import unittest

from GOES_DL.product import GOESProduct


class GOESProductTest(GOESProduct):
    def get_baseurl(self, timestamp: str) -> str:
        return f"https://path/to/{timestamp}"

    def get_filename(self, timestamp: str) -> str:
        return f"{self.product_id}_{self.origin_id}_{timestamp}.nc"


class TestGOESProduct(unittest.TestCase):
    CLASS_NAME = GOESProductTest.__name__

    def setUp(self) -> None:
        self.valid_origin_id = "G16"  # Unchecked by GOESProduct
        self.valid_product_id = "MCMIP"  # Unchecked by GOESProduct
        self.product = GOESProductTest(
            self.valid_product_id, self.valid_origin_id
        )

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
            f"product_id='{self.valid_product_id}'"
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
        TIMESTAMP = "2024-01-01T00:00:00Z"
        EXPECTED_BASEURL = f"https://path/to/{TIMESTAMP}"
        self.assertEqual(self.product.get_baseurl(TIMESTAMP), EXPECTED_BASEURL)

    def test_get_filename(self) -> None:
        TIMESTAMP = "2024-01-01T00:00:00Z"
        EXPECTED_FILENAME = (
            f"{self.valid_product_id}_"
            f"{self.valid_origin_id}_"
            f"{TIMESTAMP}.nc"
        )
        self.assertEqual(
            self.product.get_filename(TIMESTAMP), EXPECTED_FILENAME
        )


if __name__ == "__main__":
    unittest.main()
