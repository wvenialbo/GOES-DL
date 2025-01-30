"""
Provide the DatasourceHTTP class for handling HTTP-based data sources.

Classes:
    DatasourceHTTP: Handle HTTP-based data sources.
"""

import re
import socket
from urllib.parse import ParseResult

import requests

from ..dataset import ProductLocator
from ..utils.headers import APPLICATION_NETCDF4, TEXT_HTML, RequestHeaders
from ..utils.url import URL
from .datasource_base import DatasourceBase
from .datasource_cache import DatasourceCache

HTTP_STATUS_OK = 200


class DatasourceHTTP(DatasourceBase):
    """
    Handle HTTP-based data sources.

    Provide methods to interact with HTTP folders and files, either
    through a base URL or a `ProductLocator` object.

    Methods
    -------
    download_file(file_path: str)
        Retrieve a file from the datasource and save it into the local
        repository.
    list_files(dir_path: str)
        List the contents of a remote directory.
    """

    def __init__(
        self,
        locator: str | ProductLocator,
        cache: float | DatasourceCache | None = None,
    ) -> None:
        """
        Initialize the DatasourceHTTP object.

        Parameters
        ----------
        locator : str | ProductLocator
            The base URL of a HTTP-based data sources or a
            `ProductLocator` object.
        cache : float | DatasourceCache | None, optional
            The cache expiration time in seconds, by default None.

        Raises
        ------
        ValueError
            If the resource does not exist or the user has no access.
        """
        base_url: str = (
            locator
            if isinstance(locator, str)
            else locator.get_base_url("HTTP")[0]
        )

        url_parts: ParseResult = URL.parse(base_url)

        host_name: str = url_parts.netloc
        base_path = url_parts.path

        if not self._host_exists(host_name):
            raise ValueError(
                f"Host '{host_name}' does not exist or is out of service."
            )
        if not self._path_exists(base_url):
            raise ValueError(
                f"Path '{base_path}' does not exist or you have no access."
            )

        super().__init__(base_url, cache)

    def download_file(self, file_path: str) -> bytes:
        """
        Download a file from the datasource into the local repository.

        Get a file from a remote location or local repository. The path
        provided must be relative to the base URL and local repository
        root directory. The remote path is reconstructed in the local
        repository.

        Parameters
        ----------
        file_path : str
            The path to the remote file to be downloaded.

        Returns
        -------
        bytes
            The content of the file as a byte string.

        Raises
        ------
        RuntimeError
            If the file cannot be retrieved.
        """
        try:
            return self._retrieve_file(file_path)

        except requests.HTTPError as exc:
            raise RuntimeError(
                f"Unable to retrieve the file '{file_path}': {exc}"
            ) from exc

    def list_files(self, dir_path: str) -> list[str]:
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

        folder_url = URL.join(self.base_url, dir_path)
        index_html = self._get_content(folder_url)

        if not index_html:
            return []

        href_links = re.findall(r'<a\s+href="([^"]+)"', index_html)
        href_links = [URL.join(folder_url, href) for href in href_links]
        href_links = [href.replace(self.base_url, "") for href in href_links]

        self.cache.add_item(dir_path, href_links)

        return href_links

    @staticmethod
    def _host_exists(host_name: str) -> bool:
        try:
            socket.gethostbyname(host_name)

        except socket.gaierror:  # as exc
            # Host does not exist or is out of service (log this!)
            return False

        return True

    @staticmethod
    def _path_exists(folder_url: str) -> bool:
        response = requests.head(folder_url, timeout=10)

        return response.status_code == HTTP_STATUS_OK

    @staticmethod
    def _get_content(folder_url: str) -> str:
        headers = RequestHeaders(accept=TEXT_HTML).headers

        response = requests.get(folder_url, headers=headers, timeout=15)

        if response.status_code == HTTP_STATUS_OK:
            response.encoding = response.apparent_encoding
            return response.text

        return ""

    def _retrieve_file(self, file_path: str) -> bytes:
        file_url = URL.join(self.base_url, file_path)

        headers = RequestHeaders(accept=APPLICATION_NETCDF4).headers

        response = requests.get(file_url, headers=headers, timeout=15)

        response.raise_for_status()

        if response.status_code != HTTP_STATUS_OK:
            raise requests.HTTPError("Request failure", response=response)

        return bytes(response.content)
