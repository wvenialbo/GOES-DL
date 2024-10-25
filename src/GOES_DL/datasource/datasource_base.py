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
        repository: str | Path | DatasourceRepository,
        cache: float | DatasourceCache,
    ) -> None:
        """
        Initialize the DatasourceBase.

        Parameters
        ----------
        base_url : str
            The base URL for the datasource.
        repository : str | Path | DatasourceRepository
            The repository for the datasource. If a string is provided,
            it will be used as the base path for the repository.
        cache : float | DatasourceCache
            The cache for the datasource. If a float is provided, it
            will be used as the life time for each entry in the cache.
        """
        super().__init__(base_url)
        if isinstance(repository, (str, Path)):
            base_path = repository
            repository = DatasourceRepository(base_path)
        self.repository = repository
        if isinstance(cache, float):
            life_time: float = cache
            cache = DatasourceCache(life_time)
        self.cache = cache
