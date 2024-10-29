"""
Provide the Datasource abstract interface for handling datasources.

Classes:
    Datasource: Abstract a datasource object.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass(eq=False, frozen=True)
class Datasource(ABC):
    """
    Abstract a datasource object.

    This class defines the interface for a datasource object. The
    datasource is responsible for listing the contents of a directory in
    a remote location and for downloading files from that location.

    Attributes
    ----------
    base_url : str
        The base URL of the datasource. This is the URL where the
        datasource is located. The base URL is used to build the full
        URL to the files and directories.

    Methods
    -------
    download_file(file_path: str)
        Retrieve a file from the datasource and save it into the local
        repository.
    get_file(file_path: str)
        Get a file from the datasource or local repository.
    listdir(dir_path: str)
        List the contents of a remote directory.
    """

    base_url: str

    @abstractmethod
    def download_file(self, file_path: str) -> None:
        """
        Download a file from the datasource into the local repository.

        Get a file from a remote location or local repository. The path
        is relative to the base URL and local repository root directory.

        Parameters
        ----------
        file_path : str
            The path to the file. The path is relative to the base URL.
        """

    @abstractmethod
    def get_file(self, file_path: str) -> bytes:
        """
        Get a file from the datasource or local repository.

        Get a file from a remote location or local repository. The path
        is relative to the base URL and local repository root directory.

        Parameters
        ----------
        file_path : str
            The path to the file. The path is relative to the base URL.

        Returns
        -------
        bytes
            The file object.
        """

    @abstractmethod
    def listdir(self, dir_path: str) -> list[str]:
        """
        List the contents of a remote directory.

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
