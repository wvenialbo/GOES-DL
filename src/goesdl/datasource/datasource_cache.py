"""
Provide a caching mechanism for directory file lists.

Classes:
    DatasourceCacheItem: A data class representing a cached item.
    DatasourceCache: A class for caching the file list of a directory.
"""

import time
from dataclasses import dataclass


@dataclass(frozen=True)
class DatasourceCacheItem:
    """
    Data class for a cached datasource item.

    Represent an item in the cache. The item contains the list of files
    in a directory and the time when the cache was created.

    Attributes
    ----------
    files : list[str]
        The list of files in the directory.
    created_at : float
        The time when the cache was created.
    """

    files: list[str]
    created_at: float


class DatasourceCache:
    """
    Cache for the file list of a datasource directory/bucket.

    Implement a caching mechanism for the file list of a directory.  The
    cache is used to store the list of files in a directory for a
    certain amount of time. The cache is cleared every time the time
    life is reached.

    Methods
    -------
    add_item(dir_path: str, files: list[str]) -> None
        Add a list of files to the cache.
    clean_cache(all_items: bool = False) -> None
        Clean the cache.
    get_item(dir_path: str) -> list[str] | None
        Get the list of files in a directory.
    has_item(dir_path: str) -> bool
        Check if a directory is in the cache.
    remove_item(dir_path: str = "") -> None
        Clear the cache.

    Notes
    -----
    Set `life_time` to a positive number of second to enable the cache.
    The cache will be cleared every time the `life_time` is reached.
    Setting `life_time` to a non-positive number will disable the cache.
    If `life_time` is set to "nan", the behavior is undefined. The
    default value is +inf.
    """

    def __init__(self, life_time: float | None = None) -> None:
        """
        Initialize the cache.

        Initialize the cache with an optional life time.

        Parameters
        ----------
        life_time : float | None, optional
            The time in seconds that an item will be kept in the cache.
            (default: +inf)
        """
        self.life_time: float = (
            float("+inf") if life_time is None else life_time
        )
        self.cache: dict[str, DatasourceCacheItem] = {}

    def add_item(self, dir_path: str, files: list[str]) -> None:
        """
        Add a list of files to the cache.

        Add a list of files to the cache. The list of files is
        associated with the directory path.

        Parameters
        ----------
        dir_path : str
            The path to the directory. The path is relative to the base
            URL.
        files : list[str]
            The list of files in the directory.

        Raises
        ------
        ValueError
            If the folder is already in the cache.
        """
        if dir_path in self.cache:
            raise ValueError(f"Folder '{dir_path}' already in cache.")

        current_time: float = time.time()

        cache_item: DatasourceCacheItem = DatasourceCacheItem(
            files, current_time
        )
        self.cache[dir_path] = cache_item

    def clean_cache(self, all_items: bool = False) -> None:
        """
        Clean the cache.

        Clean the cache by removing items that have expired. If
        `all_items` is True, all items in the cache will be removed.

        Parameters
        ----------
        all_items : bool
            If True, all items in the cache will be removed.
        """
        if all_items:
            self.cache.clear()
            return

        current_time: float = time.time()

        for dir_path, cache_item in list(self.cache.items()):
            expire_time: float = cache_item.created_at + self.life_time

            if expire_time < current_time:
                self.cache.pop(dir_path)

    def get_item(self, dir_path: str) -> list[str] | None:
        """
        Get the list of files in a directory.

        Get the list of files in a directory from the cache.

        Parameters
        ----------
        dir_path : str
            The path to the directory. The path is relative to
            the base URL.

        Returns
        -------
        list[str] | None
            The list of files in the directory or None if the
            directory is not found in the cache.
        """
        if dir_path in self.cache:
            cache_item: DatasourceCacheItem = self.cache[dir_path]

            expire_time: float = cache_item.created_at + self.life_time
            current_time: float = time.time()

            if expire_time > current_time:
                return cache_item.files

            self.remove_item(dir_path)

        return None

    def has_item(self, dir_path: str) -> bool:
        """
        Check if a directory is in the cache.

        Check if a directory is in the cache.

        Parameters
        ----------
        dir_path : str
            The path to the directory. The path is relative to
            the base URL.

        Returns
        -------
        bool
            True if the directory is in the cache, False otherwise.
        """
        return dir_path in self.cache

    def remove_item(self, dir_path: str = "") -> None:
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

        if dir_path in self.cache:
            self.cache.pop(dir_path, None)
            return

        self.cache.clear()
