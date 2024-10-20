"""
Provide the DatasourceHTTP class for handling HTTP-based data sources.

Classes:
    DatasourceHTTP: Handle HTTP-based data sources.
"""

import re
import socket
from typing import Any, overload
from urllib.parse import ParseResult

import requests

from ..dataset import ProductLocator
from ..utils.headers import APPLICATION_NETCDF4, TEXT_HTML, RequestHeaders
from ..utils.url import url
from .datasource import Datasource
from .datasource_cache import DatasourceCache

HTTP_STATUS_OK = 200


class DatasourceHTTP(Datasource):
    """
    Handle HTTP-based data sources.

    Provide methods to interact with HTTP folders and files, either
    through a base URL or a `ProductLocator` object.

    Parameters
    ----------
    locator : str | ProductLocator
        The base URL of a HTTP-based data sources or a `ProductLocator`
        object.

    Raises
    ------
    ValueError
        If the resource does not exist or the user has no access.
    """

    @overload
    def __init__(
        self, locator: str, cache: DatasourceCache | None = None
    ) -> None: ...

    @overload
    def __init__(
        self, locator: ProductLocator, cache: DatasourceCache | None = None
    ) -> None: ...

    def __init__(
        self,
        locator: str | ProductLocator,
        cache: DatasourceCache | None = None,
    ) -> None:
        if isinstance(locator, ProductLocator):
            base_url: str = locator.get_base_url("HTTP")[0]
        else:
            base_url = locator

        url_parts: ParseResult = url.parse(base_url)

        host_name: str = url_parts.netloc
        base_path: str = url_parts.path

        if not self._host_exists(host_name):
            raise ValueError(
                f"Host '{host_name}' does not exist or is out of service."
            )

        if not self._path_exists(base_url):
            raise ValueError(
                f"Path '{base_path}' does not exist or you have no access."
            )

        super().__init__(base_url)

        self.cache: DatasourceCache = cache or DatasourceCache()

    @overload
    @staticmethod
    def create(
        locator: ProductLocator, life_time: float | None = None
    ) -> "DatasourceHTTP": ...

    @overload
    @staticmethod
    def create(
        locator: str, life_time: float | None = None
    ) -> "DatasourceHTTP": ...

    @staticmethod
    def create(
        locator: str | ProductLocator,
        life_time: float | None = None,
    ) -> "DatasourceHTTP":
        """
        Create a new HTTP datasource.

        Create a new HTTP datasource with a base URL or a ProductLocator
        object.

        Parameters
        ----------
        locator : str
            The base URL of a HTTP folder or a `ProductLocator` object.
        life_time : float, optional
            The cache life time in seconds, by default None.

        Returns
        -------
        DatasourceHTTP
            A new `DatasourceHTTP` object.

        Raises
        ------
        ValueError
            If the resource does not exist or the user has no access.
        """
        cache = DatasourceCache(life_time)
        return DatasourceHTTP(locator, cache)

    def get_file(self, file_path: str) -> Any:
        """
        Download a file into memory.

        Get a file from a remote location. The path is relative to the
        base URL.

        Parameters
        ----------
        file_path : str
            The path to the file. The path is relative to the base URL.

        Returns
        -------
        Any
            The file object.

        Raises
        ------
        HTTPError
            If the request fails.
        RuntimeError
            If the file cannot be retrieved.
        """
        try:

            file_url: str = url.join(self.base_url, file_path)

            headers = RequestHeaders(accept=APPLICATION_NETCDF4).headers
            response = requests.get(file_url, headers=headers, timeout=15)

            response.raise_for_status()

            if response.status_code == HTTP_STATUS_OK:
                return response.content

            raise requests.HTTPError("Request failure", response=response)

        except requests.HTTPError as exc:
            message: str = f"Unable to retrieve the file '{file_path}': {exc}"
            raise RuntimeError(message) from exc

    @staticmethod
    def _host_exists(host_name: str) -> bool:
        """Check if a host server exists or is not out of service.

        This function takes the hostname part of a URL as input and
        uses the socket.gethostbyname() function to try to resolve the
        hostname to an IP address. If this is successful, it means the
        host server exists and is not out of service, so the function
        returns True. If an exception is raised, it means the host
        server does not exist or is out of service, so the function
        returns False.

        Parameters
        ----------
        host_name : str
            The host server name.

        Returns
        -------
        bool
            True if the host server exists, False otherwise.
        """
        try:
            socket.gethostbyname(host_name)
            return True
        except socket.gaierror:
            return False

    def listdir(self, dir_path: str) -> list[str]:
        """
        List the contents of a directory.

        List the contents of a directory in a remote location. The path
        is relative to the base URL.

        Parameters
        ----------
        dir_path : str
            The path to the directory. The path is relative to the base
            URL.

        Returns
        -------
        list[str]
            A list of file names in the directory.
        """
        cached_links = self.cache.get_item(dir_path)

        if cached_links is not None:
            return cached_links

        folder_url: str = url.join(self.base_url, dir_path)
        index_html: str = self._get_content(folder_url)

        if not index_html:
            return []

        href_links = re.findall(r'<a\s+href="([^"]+)"', index_html)
        href_links = [url.join(folder_url, href) for href in href_links]
        href_links = [href.replace(self.base_url, "") for href in href_links]

        self.cache.add_item(dir_path, href_links)

        return href_links

    def _path_exists(self, folder_url: str) -> bool:
        """Check if a folder exists in a host server.

        Parameters
        ----------
        folder_url : str
            The URL of the folder to check.

        Returns
        -------
        bool
            True if the folder exists, False otherwise.
        """
        response = requests.head(folder_url, timeout=10)
        return response.status_code == HTTP_STATUS_OK

    def _get_content(self, folder_url: str) -> str:
        headers = RequestHeaders(accept=TEXT_HTML).headers
        response = requests.get(folder_url, headers=headers, timeout=15)
        if response.status_code == HTTP_STATUS_OK:
            response.encoding = response.apparent_encoding
            return response.text
        return ""
