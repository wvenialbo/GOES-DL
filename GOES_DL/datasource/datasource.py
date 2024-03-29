from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any


@dataclass(eq=False, frozen=True)
class Datasource(ABC):
    """
    Abstract a datasource object.

    This class defines the interface for a datasource object. The
    datasource is responsible for listing the contents of a directory
    in a remote location and for downloading files from that location.

    Attributes
    ----------
    base_url : str
        The base URL of the datasource. This is the URL where the
        datasource is located. The base URL is used to build the full
        URL to the files and directories.

    Methods
    -------
    clear_cache(dir_path: str = "") -> None
        Clear the cache.
    listdir(dir_path: str) -> list[str]
        List the contents of a directory.
    """

    base_url: str

    @abstractmethod
    def clear_cache(self, dir_path: str = "") -> None:
        """
        Clear the cache.

        Clear the cache of the datasource object. This method should
        remove all the files in the cache directory.

        Parameters
        ----------
        path : str
            The path to the directory. The path is relative to the base
            URL. If no path is provided, the entire cache should be
            cleared.
        """
        ...

    @abstractmethod
    def get_file(self, file_path: str) -> Any:
        """
        Get a file.

        Get a file from a remote location. The path is relative to the
        base URL.

        Parameters
        ----------
        path : str
            The path to the file. The path is relative to the base URL.

        Returns
        -------
        Any
            The file object.
        """
        ...

    @abstractmethod
    def listdir(self, dir_path: str) -> list[str]:
        """
        List the contents of a directory.

        List the contents of a directory in a remote location. The path
        is relative to the base URL.

        Parameters
        ----------
        path : str
            The path to the directory. The path is relative to the base
            URL.

        Returns
        -------
        list[str]
            A list of file names in the directory.
        """
        ...
