from pathlib import Path


def validate_dataset_file(path: str | Path) -> Path:
    """
    Validate the dataset file path.

    If the path is a string, convert it to a Path object.
    If the path is not a file, raise a FileNotFoundError.

    Parameters
    ----------
    path : str | Path
        The path to the dataset file.

    Returns
    -------
    Path
        The validated Path object.

    Raises
    ------
    FileNotFoundError
        If the path does not exist or is not a file.
    """
    path = Path(path)

    if not path.is_file():
        raise FileNotFoundError(f"File '{path}' does not exist.")

    return path
