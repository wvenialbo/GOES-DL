import glob
import os
import pickle
from pathlib import Path


def load_dataset_list(
    root_path: Path | str, pattern: str = "*.nc"
) -> list[str]:
    """
    Lists files within a directory and its subdirectories.

    Parameters
    ----------
    root_path : Path | str
        The root path of the directory to explore.

    Returns
    -------
    list[str]
        A list with the relative path of all files within the directory.
    """
    # Recursivele retrieve the content of the root path
    content = glob.glob(os.path.join(root_path, "**", pattern), recursive=True)

    # Filtering the directory content to extract only the file elements
    files = filter(os.path.isfile, content)

    # Get the relative path
    return [os.path.relpath(file, root_path) for file in files]


def save_metadata(path, metadata):
    with open(path, "wb") as file:
        pickle.dump(metadata, file)


def load_metadata(path):
    with open(path, "rb") as file:
        return pickle.load(file)
