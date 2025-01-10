"""
Provide the DatasourceHTTP class for handling HTTP-based data sources.

Classes:
    DatasourceHTTP: Handle HTTP-based data sources.
"""

import re
import socket
from pathlib import Path
from urllib.parse import ParseResult

import requests

from ..dataset import ProductLocator
from ..utils.headers import APPLICATION_NETCDF4, TEXT_HTML, RequestHeaders
from ..utils.url import URL as url
from .constants import DownloadStatus
from .datasource_base import DatasourceBase
from .datasource_cache import DatasourceCache
from .datasource_repository import DatasourceRepository

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
    listdir(dir_path: str)
        List the contents of a remote directory.
    """

    def __init__(
        self,
        locator: str | ProductLocator,
        repository: str | Path | DatasourceRepository | None = None,
        cache: float | DatasourceCache | None = None,
    ) -> None:
        """
        Initialize the DatasourceHTTP object.

        Parameters
        ----------
        locator : str | ProductLocator
            The base URL of a HTTP-based data sources or a `ProductLocator`
            object.
        repository : str | Path | DatasourceRepository, optional
            The directory where the files will be stored, by default
            None.
        cache : float | DatasourceCache, optional
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

        url_parts: ParseResult = url.parse(base_url)

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

        super().__init__(base_url, repository, cache)

    def download_file(self, file_path: str) -> DownloadStatus:
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
        DownloadStatus
            `DownloadStatus.SUCCESS` if the file was downloaded
            successfully; otherwise, `DownloadStatus.ALREADY` if the
            file is already in the local repository.

        Raises
        ------
        RuntimeError
            If the file cannot be retrieved.
        """
        if self.repository.has_item(file_path):
            return DownloadStatus.ALREADY

        try:
            self._retrieve_file(file_path)
            return DownloadStatus.SUCCESS

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

    @staticmethod
    def _path_exists(folder_url: str) -> bool:
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

    @staticmethod
    def _get_content(folder_url: str) -> str:
        headers = RequestHeaders(accept=TEXT_HTML).headers
        response = requests.get(folder_url, headers=headers, timeout=15)
        if response.status_code == HTTP_STATUS_OK:
            response.encoding = response.apparent_encoding
            return response.text
        return ""

    def _retrieve_file(self, file_path: str) -> bytes:
        file_url: str = url.join(self.base_url, file_path)

        headers = RequestHeaders(accept=APPLICATION_NETCDF4).headers
        response = requests.get(file_url, headers=headers, timeout=15)

        response.raise_for_status()

        if response.status_code != HTTP_STATUS_OK:
            raise requests.HTTPError("Request failure", response=response)

        content: bytes = response.content
        self.repository.add_item(file_path, content)

        return content
