from typing import Any

from GOES_DL.dataset.goes import GOESProductLocatorABIPP as ProductLocatorGOES
from GOES_DL.dataset.gridsat import GridSatProductLocatorB1 as ProductLocatorB1
from GOES_DL.datasource import DatasourceAWS as Datasource
from GOES_DL.downloader import Downloader

DATE_FORMAT = "%Y-%m-%dT%H:%M%z"


def test(dl: Downloader, start_time: str, end_time: str = "") -> list[Any]:
    if end_time:
        print(f"Downloading data from {start_time} to {end_time}")
    else:
        print(f"Downloading data from {start_time}")

    files: list[Any] = dl.get_files(start_time, end_time)

    return files


def test_gridsat() -> None:
    pd = ProductLocatorB1()
    ds = Datasource(pd.get_base_url("AWS"))
    dl = Downloader(datasource=ds, product_locator=pd, date_format=DATE_FORMAT)

    test(dl, "1980-01-01T00:00+0000")
    test(dl, "1980-01-01T00:00+0000", "1980-01-01T06:00+0000")
    test(dl, "1980-08-23T00:00+0000")
    test(dl, "1980-08-23T00:00+0000", "1980-08-23T06:00+0000")
    test(dl, "1980-08-23T00:00+0000", "1980-08-24T00:00+0000")
    test(dl, "2024-08-23T00:00+0000")


def test_goes() -> None:
    pd = ProductLocatorGOES("CMIP", "F", "C13", "G16")
    ds = Datasource(pd.get_base_url("AWS"))
    dl = Downloader(datasource=ds, product_locator=pd, date_format=DATE_FORMAT)

    test(dl, "2024-08-23T00:00+0000")


def main() -> None:
    test_gridsat()
    test_goes()


if __name__ == "__main__":
    main()
