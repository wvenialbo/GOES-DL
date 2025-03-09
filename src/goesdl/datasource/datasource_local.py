"""
Provide the DatasourceLocal class for handling local-based data sources.

Classes:
    DatasourceLocal: Handle local-based data sources.
"""

import contextlib
import os
from pathlib import Path

from ..utils import FileRepository
from .datasource_base import DatasourceBase
from .datasource_cache import DatasourceCache


class DatasourceLocal(DatasourceBase):
    """
    Handle local-based data sources.

    Provide methods to interact with local folders and files.

    Methods
    -------
    download_file(file_path: str)
        Retrieve a file from the datasource.
    list_files(dir_path: str)
        List the contents of a remote directory.

    Attributes
    ----------
    source : FileRepository
        A repository to manage files in a local drive
    """

    source: FileRepository

    def __init__(
        self,
        root_path: str | Path,
        cache: float | DatasourceCache | None = None,
    ) -> None:
        """
        Initialize the DatasourceLocal object.

        Parameters
        ----------
        root_path : str | Path
            The root path of a local-based data source.
        cache : float | DatasourceCache | None, optional
            The cache expiration time in seconds, by default None.

        Raises
        ------
        ValueError
            If the resource does not exist or the user has no access.
        """
        if not os.path.isdir(root_path):
            raise ValueError(
                f"Path '{root_path}' does not exist or you have no access."
            )

        self.source = FileRepository(root_path)

        super().__init__(str(root_path), cache)

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
            If the file cannot be retrieved or does not exist.
        """
        try:
            return self.source.read_file(file_path)

        except FileNotFoundError as exc:
            raise RuntimeError(
                f"The file '{file_path}' does not exist: {exc}"
            ) from exc
        except IOError as exc:
            raise RuntimeError(
                f"Unable to retrieve the file '{file_path}': {exc}"
            ) from exc

    def list_files(self, dir_path: str) -> list[str]:
        """
        List the contents of a directory.

        Lists files within a directory in a local drive and its
        subdirectories. The path is relative to the root path.

        Parameters
        ----------
        dir_path : str
            The path to the directory. The path is relative to the root
            path.

        Returns
        -------
        list[str]
            A list of file names in the directory.
        """
        cached_paths = self.cache.get_item(dir_path)

        if cached_paths is not None:
            return cached_paths

        folder_content: list[str] = []

        with contextlib.suppress(FileNotFoundError):
            folder_content = self.source.list_files(dir_path)

        folder_content = [os.path.join(dir_path, f) for f in folder_content]

        self.cache.add_item(dir_path, folder_content)

        return folder_content
