from pathlib import Path
from typing import cast

from .config import ConfigDict
from .report_tools import print_bar, print_setup_report
from .utilities import is_colab

_dependencies: dict[str, str] = {
    "goesdl": "goes-dl",
    "gudhi": "gudhi",
    "optype": "optype",
    "statsmodels": "statsmodels",
    "yaml": "pyyaml",
}

_legacy_folder_map = {
    "difference": "differences",
    "profile": "profiles",
    "reprojection": "reprojected",
}

_data_archives = ["difference", "profile", "reprojection"]


# ---------- Project initialisation ----------


def initialize_project(
    event_name_or_id: str,
    algorithm_id: str,
    config_settings_filepath: Path | str,
    verbose: bool = True,
) -> ConfigDict:
    if verbose:
        print_bar()
        print("Initialising project...")

    # --- Setup the environment
    _setup_environment(verbose)

    if verbose:
        print("Loading configuration file...")

    # --- Load project settings
    project_settings = ConfigDict.load(config_settings_filepath)

    if verbose:
        print(f"... configuration loaded from '{config_settings_filepath}'")

    # --- Initialise settings
    settings = _initialize_settings(
        project_settings, event_name_or_id, algorithm_id, verbose
    )

    # --- Initialise data (for remote environments)
    _initialize_data(settings, verbose)

    settings["file_path"] = config_settings_filepath

    if verbose:
        print("Project initialised!")
        print_setup_report(settings)

    return settings


def _setup_environment(verbose: bool) -> None:
    """Sets up the environment (library installations)."""
    from importlib.util import find_spec

    if verbose:
        print("Setting up environment...")

    if find_spec("IPython") is None:
        raise RuntimeError(
            "The 'IPython' environment is not installed: pip install ipython"
        )

    from IPython.core.getipython import get_ipython

    ipython = get_ipython()  # type: ignore

    if not ipython:
        raise RuntimeError("No InteractiveShell instance is registered")

    dependencies = list(_dependencies.keys())

    for dependency in dependencies:
        if find_spec(dependency) is None:
            try:
                ipython.system(f"pip install {_dependencies[dependency]}")
            except NameError as error:
                raise RuntimeError(
                    f"Could not install '{dependency}', "
                    "ensure you are running this in Jupyter or Colab"
                ) from error

    if verbose:
        print("Environment configured...")


def _initialize_settings(
    settings: ConfigDict,
    event_name_or_id: str,
    algorithm_id: str,
    verbose: bool,
) -> ConfigDict:
    if verbose:
        print("Initialising configuration...")

    # Load the 'event' section
    settings = _initialize_event(settings, event_name_or_id, verbose)

    # Load the 'datasource' section
    settings = _initialize_datasource(settings, verbose)

    # Load the 'algorithm' section
    settings = _initialize_algorithm(settings, algorithm_id, verbose)

    # Initialise an empty parameters secction
    settings["parameters"] = {}

    # Initialise working paths
    _initialize_paths(settings, verbose)

    if verbose:
        print("Configuration initialised...")

    return settings


def _initialize_algorithm(
    settings: ConfigDict,
    algorithm_id: str,
    verbose: bool,
) -> ConfigDict:
    if verbose:
        print("Initialising algorithm...")

    # Replaces the entire 'algorithm' section with the selected
    # algorithm
    algorithm_keypath = f"algorithm.{algorithm_id}"

    if algorithm_keypath not in settings:
        raise ValueError(f"Algorithm '{algorithm_id}' is not registered")

    settings["algorithm"] = settings[algorithm_keypath]

    # Replace event specific configuration for the current algorithm
    algorithm_keypath = f"event.{algorithm_id}"

    if algorithm_keypath in settings:
        settings["algorithm"] |= settings[algorithm_keypath]

    settings["algorithm_id"] = algorithm_id

    if verbose:
        print("Algorithm initialised...")

    return settings


def _initialize_datasource(
    settings: ConfigDict,
    verbose: bool,
) -> ConfigDict:
    if verbose:
        print("Initialising datasource...")

    # Replaces the entire 'datasource' section with the selected event's
    # datasource
    datasource_keypath = "event.datasource"

    if datasource_keypath not in settings:
        event_name = _get_event_name(settings)
        raise ValueError(f"Event '{event_name}' has no associated datasource")

    datasource_id = settings[datasource_keypath]

    datasource_keypath = f"datasource.{datasource_id}"

    if datasource_keypath not in settings:
        raise ValueError(f"Datasource '{datasource_id}' is not registered")

    settings["datasource"] = settings[datasource_keypath]

    if verbose:
        print("Datasource initialised...")

    return settings


def _initialize_event(
    settings: ConfigDict,
    event_name_or_id: str,
    verbose: bool,
) -> ConfigDict:
    if verbose:
        print("Initialising event...")

    # Replaces the entire 'event' section with the selected event
    event_keypath = f"event.{event_name_or_id}"

    if event_keypath in settings:
        settings["event"] = settings[event_keypath]

    else:
        event_found: bool = False

        for event_data in settings.section("event").values():
            event = cast(ConfigDict.Settings, event_data)
            if event["name"] == event_name_or_id:
                event_found = True
                settings["event"] = event
                break

        if not event_found:
            raise ValueError(f"Event '{event_name_or_id}' is not registered")

    settings["event_id"] = event_name_or_id

    if verbose:
        print("Event initialised...")

    return settings


def _initialize_data(settings: ConfigDict, verbose: bool) -> None:
    """Extracts the data ZIP file if it exists in Google Colab."""
    from zipfile import ZipFile

    if not is_colab():
        return

    if verbose:
        print("Mounting uploaded data...")

    repository_config = settings.section("repository")

    event_name = _get_event_name(settings)
    repository_path: Path = repository_config["path"]

    for archive in _data_archives:
        zipfile_path = Path(f"./{event_name}_{archive}.zip")
        if zipfile_path.exists():
            if verbose:
                print(f"ZIP file '{zipfile_path}' detected, extracting...")
            with ZipFile(zipfile_path, "r") as zip_ref:
                zip_ref.extractall(
                    repository_path
                )  # Extract to the data repository
            if verbose:
                print(
                    f"ZIP file '{zipfile_path}' "
                    f"extracted to '{repository_path}'...",
                )

    if verbose:
        print("Uploaded data mounted...")


def _get_event_name(settings: ConfigDict) -> str:
    return settings.as_str("event.name")


def _initialize_paths(settings: ConfigDict, verbose: bool) -> None:
    if verbose:
        print("Initialising repository paths...")

    repository_config = settings.section("repository")

    # Set the root path to the data repositories
    root = Path(repository_config["root"])
    repository_config["root"] = root

    # Set the path of the datasets repository for the event
    event_name = _get_event_name(settings)
    path = _set_working_path(repository_config, root, event_name)

    # Set the path for the project product folders
    for product_folder in _data_archives:
        _set_path(repository_config, path, product_folder)

    # Normalize path names
    _rename_legacy_paths(settings, verbose)

    if verbose:
        print("Repository paths initialised...")


def _set_working_path(
    repository_config: ConfigDict, root: Path, event_name: str
) -> Path:
    if repository_config["path"] is None:
        calculated_path = root / event_name
    else:
        calculated_path = Path(repository_config["path"])
    repository_config["path"] = calculated_path
    return calculated_path


def _set_path(
    repository_config: ConfigDict, base: Path, path_name: str
) -> None:
    if repository_config[path_name] is None:
        calculated_path = base / path_name
    else:
        calculated_path = Path(repository_config[path_name])
    repository_config[path_name] = calculated_path


def _rename_legacy_paths(settings: ConfigDict, verbose: bool) -> None:
    if verbose:
        print("Updating legacy paths...")

    repository_config: dict[str, Path] = settings.get("repository", {})

    cfg_suffix = ".cfg"

    path = repository_config["path"]

    for new_folder_name, old_folder_name in _legacy_folder_map.items():
        new_folder = repository_config[new_folder_name]
        old_folder = path / old_folder_name
        if old_folder.exists() and not new_folder.exists():
            _move_legacy(old_folder, new_folder, verbose)

        new_file = new_folder.with_suffix(cfg_suffix)
        old_file = old_folder.with_suffix(cfg_suffix)
        if old_file.exists() and not new_file.exists():
            _move_legacy(old_file, new_file, verbose)

    if verbose:
        print("Legacy paths updated...")


def _move_legacy(old_folder: Path, new_folder: Path, verbose: bool) -> None:
    if verbose:
        print(f"... renaming '{old_folder}'")
        print(f"... to '{new_folder}'")

    old_folder.rename(new_folder)


# ---------- Project reinitialisation ----------


def reload_project(
    settings: ConfigDict,
    verbose: bool = True,
) -> ConfigDict:
    if verbose:
        print_bar()
        print("Loading configuration file...")

    config_settings_filepath = settings.as_str("file_path")
    event_name_or_id = settings.as_str("event_id")
    algorithm_id = settings.as_str("algorithm_id")

    # --- Load project settings
    project_settings = ConfigDict.load(config_settings_filepath)

    if verbose:
        print(f"... configuration loaded from '{config_settings_filepath}'")

    # --- Initialise settings
    settings = _initialize_settings(
        project_settings, event_name_or_id, algorithm_id, verbose
    )

    if verbose:
        print("Project settings reloaded!")
        print_setup_report(settings)

    settings["file_path"] = config_settings_filepath

    return settings
