"""
This module provides an abstract class for a cached datasource.

The DatasourceCached class is an abstract class for a datasource that
caches the file list of the directory. The cache is used to avoid
unnecessary requests to the server and should be cleared when the
directory is modified.
"""

from .datasource import Datasource


class DatasourceCached(Datasource):
    """
    Abstract class for a cached datasource.

    This class is an abstract class for a datasource that caches the
    file list of the directory. The cache is used to avoid unnecessary
    requests to the server. The cache should be cleared when the
    directory is modified.

    Attributes
    ----------
    base_url : str
        The base URL of the datasource. This is the URL where the
        datasource is located. The base URL is used to build the full
        URL to the files and directories.
    cached : dict[str, list[str]]
        The cached file lists in the datasource, organised by folder.

    Methods
    -------
    clear_cache(dir_path: str = "") -> None
        Clear the cache.
    """

    def __init__(self, base_url: str) -> None:
        """
        Initialize the datasource object.

        Parameters
        ----------
        base_url : str
            The base URL of the datasource. This is the URL where the
            datasource is located. The base URL is used to build the
            full URL to the files and directories.
        """
        super().__init__(base_url)

        self.cached: dict[str, list[str]] = {}

    def clear_cache(self, dir_path: str = "") -> None:
        """
        Clear the cache.

        Clear the file list cache of the datasource object.

        Parameters
        ----------
        dir_path : str
            The path to the directory. The path is relative to
            the base URL. If no path is provided, the entire
            cache should be cleared.

        Raises
        ------
        ValueError
            If the folder is not found in the cache.
        """
        if not dir_path:
            raise ValueError(f"Folder '{dir_path}' not found in cache.")

        if dir_path in self.cached:
            self.cached.pop(dir_path, None)
            return

        self.cached.clear()
