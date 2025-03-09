"""
Provide local repository mechanisms for managing file operations.

Classes:
    FileRepository: A local repository for managing file operations.
"""

import shutil
from pathlib import Path


class FileRepository:
    """
    A local file repository for managing file operations.

    Provide methods to handle file and directory operations such as
    listing, adding, deleting, moving, and searching files within a
    specified base directory.

    Attributes
    ----------
    base_directory : Path
        The base directory where the repository is created.
    """

    base_directory: Path

    def __init__(self, base_directory: str | Path | None = None) -> None:
        """Initialize the local file repository in a base directory.

        Initialize the repository with a base directory where downloaded
        files will be stored. Create a new directory at the given path
        if it does not exist; any missing parents of this path are
        created as needed.

        Parameters
        ----------
        base_directory : str | Path | None, optional
            The base directory where the repository will be created. If
            not specified, the current working directory is used, by
            default None.

        Raises
        ------
        NotADirectoryError
            If the given path already exists in the file system and is
            not a directory.
        """
        self.base_directory = Path(base_directory or ".")
        if not self.base_directory.exists():
            self.base_directory.mkdir(parents=True)
        elif not self.base_directory.is_dir():
            raise NotADirectoryError(
                f"The path '{base_directory}' is not a directory."
            )

    def add_file(
        self,
        source_path: str | Path,
        target_directory: str | Path = "",
        move: bool | None = None,
    ) -> None:
        """Add a file to the repository by copying it or moving it.

        Copy or move a file from an external location to the specified
        directory within the repository.

        `FileExistsError` is raised if the file already exists in the
        target directory. `FileNotFoundError` if the source file does
        not exist or is not a file. If the target path already exists in
        the file system and is not a directory, `NotADirectoryError` is
        raised.

        Parameters
        ----------
        source_path : str | Path
            The path to the file to be added.
        target_directory : str | Path, optional
            The directory to add the file to, by default "".
        move : bool | None, optional
            Whether to move the file instead of copying it, optional, by
            default False.
        """
        source_path = Path(source_path)
        target_path: Path = self._make_target_path(
            source_path, target_directory
        )
        if move:
            shutil.move(source_path, target_path)
        else:
            shutil.copy2(source_path, target_path)

    def create_directory(self, directory: str | Path) -> None:
        """Create a new directory in the repository.

        Create a new directory inside the repository provided that it
        does not already exist.

        Parameters
        ----------
        directory : str | Path
            The name or relative path of the directory to create.

        Raises
        ------
        FileExistsError
            If the directory already exists.
        """
        dir_path: Path = self.base_directory / directory
        if not dir_path.exists():
            dir_path.mkdir(parents=True)
        else:
            raise FileExistsError(
                f"The directory '{dir_path}' already exists."
            )

    def delete_directory(self, directory: str | Path) -> None:
        """Delete an empty directory from the repository.

        Remove an existing empty directory within the repository.

        Parameters
        ----------
        directory : str | Path
            The name or relative path of the directory to delete.

        Raises
        ------
        NotADirectoryError
            If the directory does not exist.
        OSError
            If the directory is not empty or cannot be deleted.
        """
        dir_path: Path = self.base_directory / directory
        if not dir_path.is_dir():
            raise NotADirectoryError(
                f"The directory '{dir_path}' does not exist "
                "or is not a directory."
            )
        try:
            dir_path.rmdir()
        except OSError as e:
            raise OSError(
                f"The directory '{dir_path}' "
                "is not empty or cannot be deleted."
            ) from e

    def delete_file(
        self, file_name: str | Path, directory: str | Path = ""
    ) -> None:
        """Delete a file from the repository.

        Delete a file by name within a directory in the repository.

        Parameters
        ----------
        file_name : str | Path
            The name or relative path of the file to delete.
        directory : str | Path, optional
            The directory where the file is located, by default "".

        Raises
        ------
        FileNotFoundError
            If the file does not exist or is not a file.
        """
        file_path: Path = self.base_directory / directory / file_name
        if file_path.is_file():
            file_path.unlink()
        else:
            raise FileNotFoundError(
                f"The file '{file_path}' does not exist or is not a file."
            )

    def get_full_path(
        self, file_name: str | Path, directory: str | Path = ""
    ) -> str:
        """Get the full path to a file in the repository.

        Get the full path to a file within a directory in the
        repository.

        Parameters
        ----------
        file_name : str | Path
            The name or relative path of the file.
        directory : str | Path, optional
            The directory where the file is located, by default "".

        Returns
        -------
        str
            The full path to the file.
        """
        return str(self.base_directory / directory / file_name)

    def is_directory(
        self, path_name: str | Path, directory: str | Path = ""
    ) -> bool:
        """Check if a path name from the repository is a directory.

        Check if a path name exists within the repository and is a
        directory.

        Parameters
        ----------
        path_name : str | Path
            The name or relative path name of an object to check.
        directory : str | Path, optional
            The directory where the object is located, by default "".

        Returns
        -------
        bool
            True if the file exists, False otherwise.
        """
        directory_path: Path = self.base_directory / directory / path_name
        return directory_path.is_dir()

    def is_file(
        self, path_name: str | Path, directory: str | Path = ""
    ) -> bool:
        """Check if a path name from the repository is a file.

        Check if a path name exists within a directory in the repository
        and is a file.

        Parameters
        ----------
        path_name : str | Path
            The name or relative path name of an object to check.
        directory : str | Path, optional
            The directory where the object is located, by default "".

        Returns
        -------
        bool
            True if the file exists, False otherwise.
        """
        file_path: Path = self.base_directory / directory / path_name
        return file_path.is_file()

    def list_files(self, directory: str | Path = "") -> list[str]:
        """List all files in the given directory.

        List all files within a given directory or the root directory if
        not specified.

        Parameters
        ----------
        directory : str | Path, optional
            The name or relative path of the directory to list files
            from, by default "".

        Returns
        -------
        list[str]
            A list of file names in the given directory.

        Raises
        ------
        NotADirectoryError
            If the given path is not a directory.
        FileNotFoundError
            If the directory does not exist.
        """
        dir_path: Path = self.base_directory / directory
        if dir_path.is_dir():
            return [item.name for item in dir_path.iterdir() if item.is_file()]
        if dir_path.exists():
            raise NotADirectoryError(
                f"The path '{dir_path}' is not a directory."
            )
        raise FileNotFoundError(f"The directory '{dir_path}' does not exist.")

    def move_file(
        self,
        file_name: str | Path,
        source_directory: str | Path,
        target_directory: str | Path,
    ) -> None:
        """Move a file within the repository.

        Move a file from one directory to another within the repository.

        `FileExistsError` is raised if the file already exists in the
        target directory. `FileNotFoundError` if the source file does
        not exist or is not a file. If the target path already exists in
        the file system and is not a directory, `NotADirectoryError` is
        raised.

        Parameters
        ----------
        file_name : str | Path
            The name or relative path of the file to move.
        source_directory : str | Path
            The directory where the file is currently located.
        target_directory : str | Path
            The directory to move the file to.
        """
        source_path: Path = self.base_directory / source_directory / file_name
        target_path: Path = self._make_target_path(
            source_path, target_directory
        )
        shutil.move(source_path, target_path)

    def path_exists(
        self, path_name: str | Path, directory: str | Path = ""
    ) -> bool:
        """Check if a path exists in the repository.

        Check if a given path exists within the repository.

        Parameters
        ----------
        path_name : str | Path
            The name or relative path name of an object to check.
        directory : str | Path, optional
            The directory where the object is located, by default "".

        Returns
        -------
        bool
            True if the file exists, False otherwise.
        """
        object_path: Path = self.base_directory / directory / path_name
        return object_path.exists()

    def read_file(
        self, file_name: str | Path, directory: str | Path = ""
    ) -> bytes:
        """Read the content of a file in the repository.

        Read the content of a file within a directory in the repository.

        Parameters
        ----------
        file_name : str | Path
            The name or relative path of the file to read.
        directory : str | Path, optional
            The directory where the file is located, by default "".

        Returns
        -------
        bytes
            The content of the file as a byte string.

        Raises
        ------
        FileNotFoundError
            If the file does not exist or is not a file.
        """
        file_path: Path = self.base_directory / directory / file_name
        if file_path.is_file():
            with open(file_path, "rb") as file:
                return file.read()
        raise FileNotFoundError(
            f"The file '{file_path}' does not exist or is not a file."
        )

    def save_file(
        self, content: bytes, file_name: str | Path, directory: str | Path = ""
    ) -> None:
        """Save content to a file in the repository.

        Save the given content to a file within a directory in the
        repository. The relative path will be recreated within the
        repository to mirror the source path.

        Parameters
        ----------
        content : bytes
            The content to save to the file.
        file_name : str | Path
            The name or relative path of the file to save the content.
        directory : str | Path, optional
            The directory to save the file to, by default "".

        Raises
        ------
        FileExistsError
            If the file already exists in the target directory or if the
            given target path already exists in the file system and is
            not a directory (via `mkdir`).
        """
        file_path: Path = self.base_directory / directory / file_name
        file_path.parent.mkdir(parents=True, exist_ok=True)
        if file_path.exists():
            raise FileExistsError(
                f"The file '{file_path}' already exists in the "
                "target directory."
            )
        with open(file_path, "wb") as file:
            file.write(content)

    def search_files(
        self, pattern: str, directory: str | Path = ""
    ) -> list[str]:
        """Search for files that match a pattern.

        Search for files in a given directory within the repository by a
        search pattern; for example, "*.txt" to search for text files.

        Parameters
        ----------
        pattern : str
            The pattern to search for.
        directory : str | Path, optional
            The name or relative path of the directory to search files
            from, by default "".

        Returns
        -------
        list[str]
            A list of file names that match the pattern.

        Raises
        ------
        NotADirectoryError
            If the directory does not exist or is not a directory.
        """
        dir_path: Path = self.base_directory / directory
        if dir_path.is_dir():
            return [item.name for item in dir_path.glob(pattern)]
        raise NotADirectoryError(
            f"The directory '{dir_path}' does not exist "
            "or is not a directory."
        )

    def _make_target_path(
        self, source_path: Path, target_directory: str | Path
    ) -> Path:
        """Create the target directory for adding a file.

        Any missing parents of the target directory path are created as
        needed.

        Parameters
        ----------
        source_path : Path
            The path to the source file.
        target_directory : str | Path
            The directory to add the file to.

        Returns
        -------
        Path
            The target directory path.

        Raises
        ------
        FileExistsError
            If the file already exists in the target directory.
        FileNotFoundError
            If the source file does not exist or is not a file.
        NotADirectoryError
            If the target path already exists in the file system and is
            not a directory.
        """
        target_path: Path = self.base_directory / target_directory
        if not source_path.exists() or not source_path.is_file():
            raise FileNotFoundError(
                f"The file '{source_path}' does not exist or is not a file."
            )
        try:
            target_path.mkdir(parents=True, exist_ok=True)
        except FileExistsError as exc:
            raise NotADirectoryError(
                f"The path '{target_path}' already exists in the "
                "file system and is not a directory."
            ) from exc
        destination: Path = target_path / source_path.name
        if destination.exists():
            raise FileExistsError(
                f"The file '{destination}' already exists in the "
                "target directory."
            )
        return target_path
