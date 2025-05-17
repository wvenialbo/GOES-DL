from pathlib import Path
from pickle import dump, load
from typing import Any


def save_metadata(path: str | Path, metadata: Any) -> None:
    with open(path, "wb") as file:
        dump(metadata, file)


def load_metadata(path: str | Path) -> Any:
    with open(path, "rb") as file:
        return load(file)
