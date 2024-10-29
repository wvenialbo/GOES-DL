"""
Contain test functions for the GOES-DL project.

These functions are responsible for testing the functionality of the
downloader objects with different product locators and datasources.

Attributes
----------
DATE_FORMAT : str
    The date format specification used for parsing dates.
REPO_GRISAT_B1 : str
    The repository path for GridSat-B1 data.
REPO_GRISAT_GOES : str
    The repository path for GridSat-GOES/CONUS data.
REPO_GOES : str
    The repository path for GOES-16 data.

Functions
---------
test(dl: Downloader, start: str, end: str = "")
    Test the downloader object by downloading files within a date range.
test_gridsat_aws()
    Test the downloader object with GridSat-B1 data and AWS datasource.
test_gridsat_http()
    Test the downloader object with GridSat-B1 data and HTTP datasource.
test_gridsat_goes()
    Test the downloader object with GridSat-GOES/CONUS data and HTTP
    datasource.
test_goes()
    Test the downloader object with GOES-16 data and AWS datasource.
"""

from GOES_DL.dataset.goes import GOESProductLocatorABIPP as ProductLocatorGOES
from GOES_DL.dataset.gridsat import GridSatProductLocatorB1 as ProductLocatorB1
from GOES_DL.dataset.gridsat import GridSatProductLocatorGC as ProductLocatorGC
from GOES_DL.datasource import DatasourceAWS, DatasourceHTTP
from GOES_DL.downloader import Downloader

DATE_FORMAT = "%Y-%m-%dT%H:%M%z"


REPO_GRISAT_B1 = "../temp/gridsat/B1"
REPO_GRISAT_GOES = "../temp/gridsat/goes-conus"
REPO_GOES = "../temp/GOES-16"


def test(dl: Downloader, start: str, end: str = "") -> list[tuple[str, bytes]]:
    """
    Test the downloader object by downloading files within a date range.

    Parameters
    ----------
    dl : Downloader
        The downloader object to test.
    start : str
        The start date of the download range.
    end : str, optional
        The end date of the download range.

    Returns
    -------
    list[tuple[str, bytes]]
        The list of downloaded files.
    """
    if end:
        print(f"Downloading data from {start} to {end}")
    else:
        print(f"Downloading data from {start}")

    dl.download_files(start=start, end=end)

    files: list[tuple[str, bytes]] = dl.get_files(start=start, end=end)

    return files


def test_gridsat_aws() -> None:
    """
    Test the downloader object with GridSat-B1 data and AWS datasource.
    """
    pd = ProductLocatorB1()
    ds = DatasourceAWS(pd.get_base_url("AWS"), REPO_GRISAT_B1)
    dl = Downloader(datasource=ds, locator=pd, date_format=DATE_FORMAT)

    test(dl, "1984-08-23T00:00Z")


def test_gridsat_http() -> None:
    """
    Test the downloader object with GridSat-B1 data and HTTP datasource.
    """
    pd = ProductLocatorB1()
    ds = DatasourceHTTP(pd, REPO_GRISAT_B1)
    dl = Downloader(datasource=ds, locator=pd, date_format=DATE_FORMAT)

    test(dl, "1984-08-23T00:00Z")
    test(dl, "1982-08-23T00:00Z")


def test_gridsat_goes() -> None:
    """
    Test the downloader object with GridSat-GOES/CONUS data and HTTP
    datasource.
    """
    pd = ProductLocatorGC("F", "G12")
    ds = DatasourceHTTP(pd, REPO_GRISAT_GOES)
    dl = Downloader(datasource=ds, locator=pd, date_format=DATE_FORMAT)

    test(dl, "2008-11-09T14:00+0000")


def test_goes() -> None:
    """
    Test the downloader object with GOES-16 data and AWS datasource.
    """
    pd = ProductLocatorGOES("CMIP", "F", "C13", "G16")

    # GOES-16 data is updated every 10 minutes. If you are downloading
    # old data, you may leave the refresh rate as default.
    ds = DatasourceAWS(pd, REPO_GOES, 10 * 60)
    dl = Downloader(datasource=ds, locator=pd, date_format=DATE_FORMAT)

    test(dl, "2024-08-23T00:00+0000")


def main() -> None:
    """
    Run all test functions.
    """
    test_goes()
    test_gridsat_goes()
    test_gridsat_aws()
    test_gridsat_http()


if __name__ == "__main__":
    main()
