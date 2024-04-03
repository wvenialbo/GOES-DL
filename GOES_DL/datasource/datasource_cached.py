from abc import abstractmethod

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
        if dir_path:
            folder_path: str = self.get_folder_path(dir_path)

            if folder_path in self.cached:
                self.cached.pop(folder_path, None)
                return

            raise ValueError(f"Folder '{dir_path}' not found in cache.")

        else:
            self.cached.clear()

    @abstractmethod
    def get_folder_path(self, dir_path: str) -> str:
        """
        Get the folder path.

        Get the folder path from the base URL and the directory path.

        Parameters
        ----------
        dir_path : str
            The path to the directory. The path is relative to the base
            URL.

        Returns
        -------
        str
            The folder path.
        """
        ...
