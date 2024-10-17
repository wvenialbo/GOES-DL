"""
Provide the DatasourceHTTP class for handling HTTP-based data sources.

The DatasourceHTTP class extends DatasourceCached and provides methods
to interact with HTTP folders and files, either through a base URL or a
ProductLocator object.
"""

import socket
from typing import Any, overload
import re
import requests

from ..dataset import ProductLocator
from ..utils.url import ParseResult, url
from .datasource_cached import DatasourceCached
from .headers import Headers, TEXT_HTML, APPLICATION_NETCDF4

HTTP_STATUS_OK = 200


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

    @overload
    def __init__(self, locator: str) -> None:
        """
        Initialize the HTTP datasource with a base URL.

        Parameters
        ----------
        locator : str
            The base URL of a HTTP folder.
        """

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

        self.host_name: str = host_name
        self.base_path: str = base_path

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
        RuntimeError
            If the file cannot be retrieved.
        """
        try:

            file_url: str = url.join(self.base_url, file_path)

            headers = Headers(APPLICATION_NETCDF4).headers
            response = requests.get(file_url, headers=headers, timeout=15)

            response.raise_for_status()

            if response.status_code is HTTP_STATUS_OK:
                return response.content

            raise requests.HTTPError("Request failure", response=response)

        except requests.HTTPError as exc:
            message: str = f"Unable to retrieve the file '{file_path}': {exc}"
            raise RuntimeError(message) from exc

    def _host_exists(self, host_name: str) -> bool:
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
        # TODO: Implement caching or repository in a separate module.
        if dir_path in self.cached:
            return self.cached[dir_path]

        folder_url: str = url.join(self.base_url, dir_path)
        index_html: str = self._get_content(folder_url)

        if not index_html:
            return []

        href_links: list[str] = re.findall(r'<a\s+href="([^"]+)"', index_html)
        href_links = [url.join(folder_url, href) for href in href_links]
        href_links = [href.replace(self.base_url, "") for href in href_links]

        self.cached[dir_path] = href_links

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
        return response.status_code is HTTP_STATUS_OK

    def _get_content(self, folder_url: str) -> str:
        headers = Headers(TEXT_HTML).headers
        response = requests.get(folder_url, headers=headers, timeout=15)
        if response.status_code is HTTP_STATUS_OK:
            response.encoding = response.apparent_encoding
            return response.text
        return ""
