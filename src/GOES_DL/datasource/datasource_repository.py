"""
Provide a repository mechanism for downloaded objects.

Classes:
    DatasourceRepository: A local repository for managing downloaded
    objects.
"""

from pathlib import Path

from ..utils import FileRepository


class DatasourceRepository:
    """
    A local file repository for managing downloaded objects.

    Attributes
    ----------
    repository : FileRepository
        The underlying file repository object.
    """

    repository: FileRepository

    def __init__(
        self, repository: str | Path | FileRepository | None = None
    ) -> None:
        """Initialize the local repository in a base directory.

        Initialize the repository with a base directory where downloaded
        files will be stored. Create a new directory at the given path
        if it does not exist; any missing parents of this path are
        created as needed.

        Parameters
        ----------
        repository : str | Path  | FileRepository, optional
            An initialised `FileRepository` instance or the path to the
            base directory where the repository will be created. If not
            specified, the current working directory is used; by default
            None.
        """
        if isinstance(repository, FileRepository):
            self.repository = repository
        else:
            self.repository = FileRepository(repository)

    def add_item(self, file_path: str, file: bytes) -> None:
        """
        Add a file to the repository.

        Parameters
        ----------
        file_path : str
            The path where the file will be stored within the repository.
        file : bytes
            The file content to be stored.

        Raises
        ------
        ValueError
            If the file already exists in the repository.
        """
        if self.has_item(file_path):
            raise ValueError(f"File '{file_path}' already in repository.")
        self.repository.save_file(file, file_path)

    def get_item(self, file_path: str) -> bytes | None:
        """
        Retrieve a file from the repository.

        Parameters
        ----------
        file_path : str
            The path to the file within the repository.

        Returns
        -------
        bytes or None
            The file content as bytes if the file exists, otherwise None.
        """
        if self.has_item(file_path):
            return self.repository.read_file(file_path)
        return None

    def has_item(self, file_path: str) -> bool:
        """
        Check if a file exists in the repository.

        Parameters
        ----------
        file_path : str
            The path to the file within the repository.

        Returns
        -------
        bool
            True if the file exists, False otherwise.
        """
        return self.repository.is_file(file_path)
