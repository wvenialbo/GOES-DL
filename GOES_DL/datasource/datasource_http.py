from typing import Any, overload

from ..dataset import ProductLocator
from .datasource_cached import DatasourceCached


class DatasourceHTTP(DatasourceCached):
    """
    DatasourceHTTP is a class for handling HTTP-based data sources.

    This class extends `DatasourceCached` and provides methods to
    interact with HTTP folders and files, either through a base URL or a
    `ProductLocator` object.
    """

    @overload
    def __init__(self, locator: ProductLocator) -> None:
        """
        Initialize the HTTP datasource with a ProductLocator.

        Parameters
        ----------
        locator : ProductLocator
            A `ProductLocator` object.
        """
        ...

    @overload
    def __init__(self, locator: str) -> None:
        """
        Initialize the HTTP datasource with a base URL.

        Parameters
        ----------
        locator : str
            The base URL of a HTTP folder.
        """
        ...

    def __init__(self, locator: str | ProductLocator) -> None:
        """
        Initialize the HTTP datasource.

        Parameters
        ----------
        locator : str
            The base URL of a HTTP folder or a `ProductLocator` object.

        Raises
        ------
        ValueError
            If the resource does not exist or the user has no access.
        """
        if isinstance(locator, ProductLocator):
            base_url: str = locator.get_base_url("HTTP")[0]
        else:
            base_url = locator

    def get_file(self, file_path: str) -> Any:
        return None

    def get_folder_path(self, dir_path: str) -> str:
        return ""

    def listdir(self, dir_path: str) -> list[str]:
        return []
