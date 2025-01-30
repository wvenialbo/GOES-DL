"""
Define the class for the downloader object.

The downloader object is responsible for downloading files from a
specified location using a datasource and product locator.

Classes
-------
Downloader
    Represent a downloader object.
"""

from pathlib import Path

from ..dataset import ProductLocator
from ..datasource import Datasource
from ..utils import FileRepository
from .constants import ISO_TIMESTAMP_FORMAT, TIME_TOLERANCE_DEFAULT
from .downloader_base import DownloaderBase


class Downloader(DownloaderBase):
    """
    Represent a downloader object.

    The downloader object is responsible for downloading files from a
    datasource and store it in a local repository. It receives a
    `Datasource` object, a `ProductLocator` object, and a
    `FileRepository` object. Optional parameters are a date format
    specification, a time tolerance value and a flag to show the
    download progress. It provides methods to download files from the
    datasource that match the timestamps between a start and end time.

    The downloader object is agnostic to the datasource, dataset, and
    dataset's product implementations. It only requires that the
    datasource and product locator objects implement the methods
    specified in the `GOES_DL.datasource.Datasource`,
    `GOES_DL.dataset.ProductLocator` and `GOES_DL.dataset.Product`
    interfaces.
    """

    def __init__(
        self,
        datasource: Datasource,
        locator: ProductLocator,
        repository: str | Path | FileRepository | None = None,
        date_format: str = ISO_TIMESTAMP_FORMAT,
        time_tolerance: int = TIME_TOLERANCE_DEFAULT,
        show_progress: bool = True,
    ) -> None:
        if not isinstance(repository, FileRepository):
            repository = FileRepository(repository)

        super().__init__(
            datasource=datasource,
            locator=locator,
            repository=repository,
            date_format=date_format,
            time_tolerance=time_tolerance,
            show_progress=show_progress,
        )
