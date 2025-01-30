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

from goesdl.dataset.goes import GOESProductLocatorABIPP as ProductLocatorGOES
from goesdl.dataset.gridsat import GridSatProductLocatorB1 as ProductLocatorB1
from goesdl.dataset.gridsat import GridSatProductLocatorGC as ProductLocatorGC
from goesdl.datasource import DatasourceAWS, DatasourceHTTP, DatasourceLocal
from goesdl.downloader import Downloader

DATE_FORMAT = "%Y-%m-%dT%H:%M%z"


REPO_GRISAT_B1 = "../temp/gridsat/B1"
REPO_GRISAT_GOES = "../temp/gridsat/goes-conus"
REPO_GOES = "../temp/GOES-16"


def test(dl: Downloader, start: str, end: str = "") -> list[str]:
    """
    Test the downloader object by downloading files within a date range.

    Parameters
    ----------
    dl : Downloader
        The downloader object to test.
    start : str
        The start date of the download range.
    end : str
        The end date of the download range, if any. The default is "".

    Returns
    -------
    list[str]
        The list of downloaded files.
    """
    if end:
        print(f"Downloading data from {start} to {end}")
    else:
        print(f"Downloading data from {start}")

    return dl.download_files(start=start, end=end)


def test_gridsat_aws() -> list[str]:
    """
    Test the downloader object with GridSat-B1 data and AWS datasource.

    Returns
    -------
    list[str]
        The list of downloaded files.
    """
    pd = ProductLocatorB1()
    ds = DatasourceAWS(pd.get_base_url("AWS"))

    dl = Downloader(
        datasource=ds,
        locator=pd,
        repository=REPO_GRISAT_B1,
        date_format=DATE_FORMAT,
    )

    return test(dl, "1984-08-23T00:00Z")


def test_gridsat_http() -> tuple[list[str], list[str]]:
    """
    Test the downloader object with GridSat-B1 data and HTTP datasource.

    Returns
    -------
    tuple[list[str], list[str]]
        A tuple of lists of downloaded files.
    """
    pd = ProductLocatorB1()
    ds = DatasourceHTTP(pd)

    dl = Downloader(
        datasource=ds,
        locator=pd,
        repository=REPO_GRISAT_B1,
        date_format=DATE_FORMAT,
    )

    files1 = test(dl, "1984-08-23T00:00Z")
    files2 = test(dl, "1982-08-23T00:00Z")

    return files1, files2


def test_gridsat_goes() -> list[str]:
    """
    Test the downloader with GridSat-GOES/CONUS and HTTP datasource.

    Returns
    -------
    list[str]
        The list of downloaded files.
    """
    pd = ProductLocatorGC("F", "G12")
    ds = DatasourceHTTP(pd)

    dl = Downloader(
        datasource=ds,
        locator=pd,
        repository=REPO_GRISAT_GOES,
        date_format=DATE_FORMAT,
    )

    return test(dl, "2008-11-09T14:00Z")


def test_goes1() -> list[str]:
    """
    Test the downloader object with GOES-16 data and AWS datasource.

    Returns
    -------
    list[str]
        The list of downloaded files.
    """
    pd = ProductLocatorGOES("CMIP", "F", "C13", "G16")

    # GOES-16 data is updated every 10 minutes. If you are downloading
    # old data, you may leave the refresh rate as default.

    ds = DatasourceAWS(pd, 10 * 60)

    dl = Downloader(
        datasource=ds,
        locator=pd,
        repository=REPO_GOES,
        date_format=DATE_FORMAT,
    )

    return test(dl, "2024-08-23T00:00+0000")


def test_goes2() -> tuple[list[str], list[str]]:
    """
    Test the downloader object with GOES-16 data and AWS datasource.

    Returns
    -------
    tuple[list[str], list[str]]
        A tuple of lists of downloaded files.
    """
    pd = ProductLocatorGOES("CMIP", "F", "C13", "G16")

    # GOES-16 data is updated every 10 minutes. If you are downloading
    # old data, you may leave the refresh rate as default.

    ds = DatasourceAWS(pd, 10 * 60)

    repo_goes_l = "../../TFG_Tools/repository/20201114T20"

    dl = Downloader(
        datasource=ds,
        locator=pd,
        repository=repo_goes_l,
        date_format=DATE_FORMAT,
    )

    files1 = test(dl, "2020-11-14T20:00Z")
    files2 = test(dl, "2020-11-14T20:00Z", "2020-11-15T19:00Z")

    return files1, files2


def test_goes3() -> tuple[list[str], list[str]]:
    """
    Test the downloader object with GOES-16 data and local datasource.

    Returns
    -------
    tuple[list[str], list[str]]
        A tuple of lists of downloaded files.
    """
    pd = ProductLocatorGOES("CMIP", "F", "C13", "G16")

    repo_goes_s = "../../TFG_Tools/repository/20201114T20"

    ds = DatasourceLocal(repo_goes_s, 0)

    repo_goes_d = "../../TFG_Tools/repository/20201114T21"

    dl = Downloader(
        datasource=ds,
        locator=pd,
        repository=repo_goes_d,
        date_format=DATE_FORMAT,
    )

    files1 = test(dl, "2020-11-14T20:00Z")
    files2 = test(dl, "2020-11-14T20:00Z", "2020-11-15T19:00Z")

    return files1, files2


def main() -> None:
    """Run all test functions."""
    files2 = test_goes3()
    print(files2)

    files2 = test_goes2()
    print(files2)

    files = test_goes1()
    print(files)

    files = test_gridsat_goes()
    print(files)

    files = test_gridsat_aws()
    print(files)

    files2 = test_gridsat_http()
    print(files2)


if __name__ == "__main__":
    main()
