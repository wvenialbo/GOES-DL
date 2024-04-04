import unittest
from datetime import datetime

from GOES_DL.dataset import Product, ProductLocator
from GOES_DL.dataset.gridsat import GridSatProductGC, GridSatProductLocatorGC
from GOES_DL.datasource import Datasource, DatasourceHTTP


class TestGridSatProductLocatorGC(unittest.TestCase):
    AVAILABLE_DATASOURCE: list[str] = ["NOAA"]
    UNSUPPORTED_DATASOURCE: list[str] = ["Google", "AWS", "Azure"]
    DATASOURCE_CLASS: list[type[Datasource]] = [DatasourceHTTP]
    DATASOURCE_URL: list[str] = [
        "https://www.ncei.noaa.gov/data/gridsat-goes/access/"
    ]

    VALID_ORIGIN: str = "G12"
    PRODUCT_SCENE: list[str] = ["F", "C"]
    PATH_PREFIX: list[str] = ["goes/", "conus/"]
    DATE_FORMAT: str = "%Y/%m"

    def setUp(self) -> None:
        self.product: GridSatProductGC = GridSatProductGC(
            self.PRODUCT_SCENE[0], self.VALID_ORIGIN
        )
        self.locator: GridSatProductLocatorGC = GridSatProductLocatorGC(
            self.product
        )
        self.datasource: Datasource = self.locator.datasource

    def test_init_is_locator(self) -> None:
        self.assertIsInstance(self.locator, ProductLocator)

    def test_init_is_locator_goes(self) -> None:
        self.assertIsInstance(self.locator, GridSatProductLocatorGC)

    def test_init_is_product(self) -> None:
        self.assertIsInstance(self.product, Product)

    def test_init_is_product_goes(self) -> None:
        self.assertIsInstance(self.product, GridSatProductGC)

    def test_init_is_datasource(self) -> None:
        self.assertIsInstance(self.datasource, Datasource)

    def test_init_is_datasource_http(self) -> None:
        self.assertIsInstance(self.datasource, DatasourceHTTP)

    def test_init_invalid_datasource(self) -> None:
        for datasource in self.UNSUPPORTED_DATASOURCE:
            with self.assertRaises(ValueError):
                GridSatProductLocatorGC(self.product, datasource=datasource)

    def test_init_supported_datasources(self) -> None:
        available_ds: list[str] = self.AVAILABLE_DATASOURCE
        class_ds: list[type[Datasource]] = self.DATASOURCE_CLASS
        for datasource, expected_class in zip(available_ds, class_ds):
            locator: GridSatProductLocatorGC = GridSatProductLocatorGC(
                self.product, datasource=datasource
            )
            self.assertIsInstance(locator.datasource, expected_class)

    def test_init_supported_datasource_urls(self) -> None:
        available_ds: list[str] = self.AVAILABLE_DATASOURCE
        url_ds: list[str] = self.DATASOURCE_URL
        for datasource, expected_url in zip(available_ds, url_ds):
            locator: GridSatProductLocatorGC = GridSatProductLocatorGC(
                self.product, datasource=datasource
            )
            self.assertEqual(locator.datasource.base_url, expected_url)

    def test_init_available_scenes(self) -> None:
        available_scene: list[str] = self.PRODUCT_SCENE
        expected_prefixes: list[str] = self.PATH_PREFIX
        for scene, expected_prefix in zip(available_scene, expected_prefixes):
            product: GridSatProductGC = GridSatProductGC(
                scene, self.VALID_ORIGIN
            )
            locator: GridSatProductLocatorGC = GridSatProductLocatorGC(product)
            self.assertEqual(locator.path_prefix, expected_prefix)

    def test_datasource_property(self) -> None:
        self.assertIsInstance(self.locator.datasource, DatasourceHTTP)

    def test_datasource_property_is_datasource(self) -> None:
        self.assertIsInstance(self.locator.datasource, Datasource)

    def test_product_property(self) -> None:
        self.assertIsInstance(self.locator.product, GridSatProductGC)

    def test_product_property_is_product(self) -> None:
        self.assertIsInstance(self.locator.product, Product)

    def test_date_format_property(self) -> None:
        self.assertEqual(self.locator.date_format, self.DATE_FORMAT)

    def test_path_prefix_property(self) -> None:
        self.assertEqual(self.locator.path_prefix, self.PATH_PREFIX[0])

    def test_get_datasource(self) -> None:
        self.assertEqual(self.locator.get_datasource(), self.datasource)

    def test_get_product(self) -> None:
        self.assertEqual(self.locator.get_product(), self.product)

    def test_get_paths(self) -> None:
        time_1: datetime = datetime(1982, 1, 10, 11)
        time_2: datetime = datetime(1985, 12, 13, 14)
        expected_paths: list[str] = [
            f"{self.PATH_PREFIX[0]}{year:04d}/{month:02d}/"
            for year in range(1982, 1986)
            for month in range(1, 13)
        ]
        returned_paths: list[str] = self.locator.get_paths(time_1, time_2)
        self.assertEqual(returned_paths, expected_paths)

    def test_invalid_datasource(self) -> None:
        invalid_ds: list[str] = self.UNSUPPORTED_DATASOURCE
        for expected_ds in invalid_ds:
            unsupported_ds: str = self.locator.invalid_datasource(
                [expected_ds]
            )
            self.assertEqual(unsupported_ds, expected_ds)

    def test_invalid_datasource_array(self) -> None:
        invalid_ds: list[str] = self.UNSUPPORTED_DATASOURCE
        expected_ds: str = invalid_ds[0]
        unsupported_ds: str = self.locator.invalid_datasource(invalid_ds)
        self.assertEqual(unsupported_ds, expected_ds)

    def test_available_datasource(self) -> None:
        available_ds: list[str] = self.AVAILABLE_DATASOURCE
        for datasource in available_ds:
            supported_ds: str = self.locator.invalid_datasource([datasource])
            self.assertEqual(supported_ds, "")

    def test_available_datasource_array(self) -> None:
        available_ds: list[str] = self.AVAILABLE_DATASOURCE
        supported_ds: str = self.locator.invalid_datasource(available_ds)
        self.assertEqual(supported_ds, "")

    def test_next_time(self) -> None:
        current_time = datetime(2022, 1, 1)
        expected_next_time: datetime = datetime(2022, 2, 1)
        returned_next_time: datetime = self.locator.next_time(current_time)
        self.assertEqual(returned_next_time, expected_next_time)

    def test_normalize_time_1(self) -> None:
        time_1: datetime = datetime(1970, 8, 23, 12)
        time_2: datetime = datetime(2020, 8, 23, 13)
        expected_time_1: datetime = datetime(1970, 8, 1, 0)
        returned_time_1: datetime
        returned_time_1, _ = self.locator.normalize_times(time_1, time_2)
        self.assertEqual(returned_time_1, expected_time_1)

    def test_normalize_time_2(self) -> None:
        time_1: datetime = datetime(1970, 8, 23, 14)
        time_2: datetime = datetime(2020, 8, 23, 15)
        expected_time_2: datetime = datetime(2020, 8, 1, 0)
        returned_time_2: datetime
        _, returned_time_2 = self.locator.normalize_times(time_1, time_2)
        self.assertEqual(returned_time_2, expected_time_2)

    def test_truncate_to_month(self) -> None:
        current_time: datetime = datetime(2020, 8, 23, 16)
        expected_truncated_time: datetime = datetime(2020, 8, 1, 0)
        returned_truncated_time: datetime = self.locator.truncate_to_month(
            current_time
        )
        self.assertEqual(returned_truncated_time, expected_truncated_time)
