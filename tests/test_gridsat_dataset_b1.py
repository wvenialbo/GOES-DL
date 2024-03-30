import unittest
from datetime import datetime

from GOES_DL.dataset import Dataset, Product
from GOES_DL.dataset.gridsat.constants import (
    B1_DATASET_DATE_FORMAT,
    B1_DATASET_PATH_PREFIX,
)
from GOES_DL.dataset.gridsat.dataset_b1 import GridSatDatasetB1
from GOES_DL.dataset.gridsat.product_b1 import GridSatProductB1
from GOES_DL.datasource import Datasource, DatasourceAWS


class TestGridSatDatasetB1(unittest.TestCase):
    AVAILABLE_DATASOURCE = GridSatDatasetB1.AVAILABLE_DATASOURCE

    def setUp(self) -> None:
        self.product: GridSatProductB1 = GridSatProductB1()
        self.dataset: GridSatDatasetB1 = GridSatDatasetB1(self.product)

    def test_init_is_dataset(self) -> None:
        self.assertIsInstance(self.dataset, Dataset)

    def test_init_is_product(self) -> None:
        self.assertIsInstance(self.product, Product)

    def test_init_invalid_datasource(self) -> None:
        with self.assertRaises(ValueError):
            GridSatDatasetB1(self.product, datasource="Google")

    def test_init_supported_datasources(self) -> None:
        for key, value in self.AVAILABLE_DATASOURCE.items():
            dataset = GridSatDatasetB1(self.product, datasource=key)
            self.assertIsInstance(dataset.datasource, value)

    def test_datasource_property(self) -> None:
        self.assertIsInstance(self.dataset.datasource, DatasourceAWS)

    def test_datasource_property_is_datasource(self) -> None:
        self.assertIsInstance(self.dataset.datasource, Datasource)

    def test_product_property(self) -> None:
        self.assertIsInstance(self.dataset.product, GridSatProductB1)

    def test_product_property_is_product(self) -> None:
        self.assertIsInstance(self.dataset.product, Product)

    def test_date_format_property(self) -> None:
        self.assertEqual(self.dataset.date_format, B1_DATASET_DATE_FORMAT)

    def test_path_prefix_property(self) -> None:
        self.assertEqual(self.dataset.path_prefix, B1_DATASET_PATH_PREFIX)

    def test_get_datasource(self) -> None:
        self.assertEqual(
            self.dataset.get_datasource(), self.dataset.datasource
        )

    def test_get_product(self) -> None:
        self.assertEqual(self.dataset.get_product(), self.product)

    def test_get_paths(self) -> None:
        time_1: datetime = datetime(1970, 8, 23, 0)
        time_2: datetime = datetime(2020, 8, 23, 14)
        expected_paths = [f"{year}/" for year in range(1970, 2021)]
        returned_paths = self.dataset.get_paths(time_1, time_2)
        self.assertEqual(returned_paths, expected_paths)

    def test_invalid_datasource(self) -> None:
        unsupported_datasource = self.dataset.invalid_datasource(["Google"])
        self.assertEqual(unsupported_datasource, "Google")

    def test_available_datasource(self) -> None:
        supported_datasource = self.dataset.invalid_datasource(
            list(self.AVAILABLE_DATASOURCE.keys())
        )
        self.assertEqual(supported_datasource, "")

    def test_next_time(self) -> None:
        current_time = datetime(2022, 1, 1)
        next_time = self.dataset.next_time(current_time)
        self.assertEqual(next_time, datetime(2023, 1, 1))

    def test_normalize_times(self) -> None:
        time_1: datetime = datetime(1970, 8, 23, 0)
        time_2: datetime = datetime(2020, 8, 23, 14)
        t_time_1, t_time_2 = self.dataset.normalize_times(time_1, time_2)
        self.assertTrue(
            t_time_1 == datetime(1970, 1, 1, 0)
            and t_time_2 == datetime(2020, 1, 1, 0)
        )

    def test_truncate_to_year(self) -> None:
        current_time: datetime = datetime(2020, 8, 23, 14)
        truncated_time = self.dataset.truncate_to_year(current_time)
        self.assertEqual(truncated_time, datetime(2020, 1, 1, 0))


if __name__ == "__main__":
    unittest.main()
