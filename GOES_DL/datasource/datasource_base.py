"""
Extend the Datasource interface with cache and repository support.

Classes:
    DatasourceBase: Extend the Datasource interface.
"""

from pathlib import Path

from .datasource import Datasource
from .datasource_cache import DatasourceCache
from .datasource_repository import DatasourceRepository


class DatasourceBase(Datasource):
    """
    Extend the Datasource interface with cache and repository support.

    Attributes
    ----------
    cache : DatasourceCache
        The cache for the datasource.
    repository : DatasourceRepository
        The repository for the datasource.
    """

    cache: DatasourceCache
    repository: DatasourceRepository

    def __init__(
        self,
        base_url: str,
        repository: str | Path | DatasourceRepository | None,
        cache: float | DatasourceCache | None,
    ) -> None:
        """
        Initialize the DatasourceBase.

        Parameters
        ----------
        base_url : str
            The base URL for the datasource.
        repository : str | Path | DatasourceRepository | None
            The repository for the datasource. If a path string is
            provided, it will be used as the base path for the
            repository. If `None` is provided, the repository will be
            set to the current directory.
        cache : float | DatasourceCache | None
            The cache for the datasource. If a float is provided, it
            will be used as the life time for each entry in the cache.
            If `None` is provided, the cache will be set to have a life
            time of 0.0 seconds, i.e. no caching.
        """
        super().__init__(base_url)
        if repository is None:
            repository = "."
        if isinstance(repository, (str, Path)):
            base_path = repository
            repository = DatasourceRepository(base_path)
        self.repository = repository

        if cache is None:
            cache = 0.0
        if isinstance(cache, float):
            life_time: float = cache
            cache = DatasourceCache(life_time)
        self.cache = cache
