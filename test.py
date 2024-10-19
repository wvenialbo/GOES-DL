from typing import Any

from .GOES_DL.dataset.goes import GOESProductLocatorABIPP as ProductLocatorGOES
from .GOES_DL.dataset.gridsat import (
    GridSatProductLocatorB1 as ProductLocatorB1,
)
from .GOES_DL.datasource import DatasourceAWS, DatasourceHTTP
from .GOES_DL.downloader import Downloader

DATE_FORMAT = "%Y-%m-%dT%H:%M%z"


def test(dl: Downloader, start: str, end: str = "") -> list[Any]:
    if end:
        print(f"Downloading data from {start} to {end}")
    else:
        print(f"Downloading data from {start}")

    files: list[Any] = dl.get_files(start=start, end=end)

    return files


def test_gridsat_aws() -> None:
    pd = ProductLocatorB1()
    ds = DatasourceAWS(pd)
    dl = Downloader(datasource=ds, locator=pd, date_format=DATE_FORMAT)

    test(dl, "1980-01-01T00:00+0000")
    test(dl, "1980-01-01T00:00+0000", "1980-01-01T06:00+0000")
    test(dl, "1980-08-23T00:00+0000")
    test(dl, "1980-08-23T00:00+0000", "1980-08-23T06:00+0000")
    test(dl, "1980-08-23T00:00+0000", "1980-08-24T00:00+0000")
    test(dl, "2024-08-23T00:00+0000")


def test_gridsat_http() -> None:
    pd = ProductLocatorB1()
    ds = DatasourceHTTP(pd)
    dl = Downloader(datasource=ds, locator=pd, date_format=DATE_FORMAT)

    test(dl, "1980-01-01T00:00+0000")
    test(dl, "1980-01-01T00:00+0000", "1980-01-01T06:00+0000")
    test(dl, "1980-08-23T00:00+0000")
    test(dl, "1980-08-23T00:00+0000", "1980-08-23T06:00+0000")
    test(dl, "1980-08-23T00:00+0000", "1980-08-24T00:00+0000")
    test(dl, "2024-08-23T00:00+0000")


def test_goes() -> None:
    pd = ProductLocatorGOES("CMIP", "F", "C13", "G16")
    ds = DatasourceAWS(pd.get_base_url("AWS"))
    dl = Downloader(datasource=ds, locator=pd, date_format=DATE_FORMAT)

    test(dl, "2024-08-23T00:00+0000")


def main() -> None:
    test_gridsat_aws()
    test_gridsat_http()
    test_goes()


if __name__ == "__main__":
    main()
