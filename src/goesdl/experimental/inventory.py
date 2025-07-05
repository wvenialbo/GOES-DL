from pathlib import Path
from typing import Any

from .config import ConfigDict
from .report_tools import print_bar, print_line
from .utilities import get_filename_prefix

_gridsatb_datasets = {"GridSat-B1"}

_gridsatg_datasets = {"GridSat-CONUS", "GridSat-GOES", "GridSat-GOES/CONUS"}

_goesr_datasets = {
    "GOES",
    "GOES-R",
    "GOES-16",
    "GOES-17",
    "GOES-18",
    "GOES-19",
}


# ---------- Inventory loading ----------


def load_inventory(settings: ConfigDict) -> tuple[list[str], list[float]]:
    from goesdl.fileio import load_metadata, save_metadata

    print_bar()

    print("Loading dataset inventory...")

    inventory_filename = _get_inventory_filename(settings)

    # Retrieve the datasets inventory

    inventory_data: tuple[list[str], list[float]]

    if inventory_filename.exists():
        # Just retrieve the preloaded inventory
        print("... retrieving preloaded inventory")

        inventory_data = load_metadata(inventory_filename)
        dataset_paths, _ = inventory_data

    else:
        # Load the inventory from local repository
        print("... creating inventory from local repository")
        inventory_data = _load_inventory_any(settings)
        dataset_paths, _ = inventory_data

        save_metadata(inventory_filename, inventory_data)

    total_files = len(dataset_paths)
    available_files = sum(path != "" for path in dataset_paths)
    missing_files = total_files - available_files

    print("Dataset inventory loaded!")

    print_line()

    if available_files > 0:
        print(
            f"Found {available_files} datasets of {total_files}, "
            f"missing {missing_files} datasets",
        )
    else:
        print(
            "Unable to acquire files: no datasets "
            "found in the specified date range",
        )

    print_bar()

    return inventory_data


def _load_inventory_any(settings: ConfigDict) -> tuple[list[str], list[float]]:
    project = settings.as_str("datasource.project")

    if project in _goesr_datasets:
        # Load the inventory using GOES-R machinery
        return _load_inventory_gr(settings)

    if project in _gridsatb_datasets:
        # Load the inventory using GridSat-B1 machinery
        return _load_inventory_gb(settings)

    if project in _gridsatg_datasets:
        # Load the inventory using GridSat-GOES/CONUS machinery
        return _load_inventory_gs(settings)

    raise ValueError(f"Unknown dataset project: '{project}'")


def _load_inventory_gr(settings: ConfigDict) -> tuple[list[str], list[float]]:
    # Import the coverage time info, locator, and dataset inventory
    from goesdl.downloader import DatasetInventory
    from goesdl.goesr import GOESCoverageTime, GOESProductLocatorCMIP

    print("... using GOES-R imagery product locator")

    origin: str | list[str]
    channel: str | list[str]
    scene: str
    time_resolution: int
    origin, channel, scene, time_resolution = _get_datasource_info(settings)

    if isinstance(origin, list):
        if len(origin) != 1:
            raise ValueError(
                "When 'origin' is a list, it must contain exactly one element, "
                f"received {len(origin)} elements"
            )
        origin = origin[0]

    # Initialise the product locator for GOES-R datasets
    grlocator = GOESProductLocatorCMIP(
        scene=scene, channels=channel, origin=origin
    )

    time_start, time_end, date_format, repository_path = _get_inventory_info(
        settings
    )

    # Initialize the inventory manager
    inventory = DatasetInventory(
        repository=repository_path,
        locator=grlocator,
        coverage=GOESCoverageTime,
        interval=24 * 3600 // time_resolution,
        dateformat=date_format,
    )

    # Load the dataset inventory within a given date range
    dataset_paths, dataset_times = inventory.get_sequence(
        start=time_start, end=time_end, use_end=True
    )

    return dataset_paths, dataset_times


def _load_inventory_gb(settings: ConfigDict) -> tuple[list[str], list[float]]:
    # Import inventory loader, the GridSat product locator, and the
    # coverage time info loader
    from goesdl.downloader import DatasetInventory
    from goesdl.gridsat import GridSatProductLocatorB1, GSCoverageTime

    print("... using GridSat-B1 imagery product locator")

    # Initialize the product locator for GridSat datasets
    gslocator = GridSatProductLocatorB1()

    time_resolution: int
    _, _, _, time_resolution = _get_datasource_info(settings)

    time_start, time_end, date_format, repository_path = _get_inventory_info(
        settings
    )

    # Initialize the inventory manager
    inventory = DatasetInventory(
        repository=repository_path,
        locator=gslocator,
        coverage=GSCoverageTime,
        interval=24 * 3600 // time_resolution,
        dateformat=date_format,
    )

    # Load the dataset inventory within a given date range
    dataset_paths, dataset_times = inventory.get_sequence(
        start=time_start, end=time_end, use_end=True
    )

    return dataset_paths, dataset_times


def _load_inventory_gs(settings: ConfigDict) -> tuple[list[str], list[float]]:
    # Import inventory loader, the GridSat product locator, and the
    # coverage time info loader
    from goesdl.downloader import DatasetInventory
    from goesdl.gridsat import GridSatProductLocatorGC, GSCoverageTime

    print("... using GridSat-GOES/CONUS imagery product locator")

    origin: str | list[str]
    scene: str
    time_resolution: int
    origin, _, scene, time_resolution = _get_datasource_info(settings)

    # Initialize the product locator for GridSat datasets
    gslocator = GridSatProductLocatorGC(scene=scene, origins=origin)

    time_start, time_end, date_format, repository_path = _get_inventory_info(
        settings
    )

    # Initialize the inventory manager
    inventory = DatasetInventory(
        repository=repository_path,
        locator=gslocator,
        coverage=GSCoverageTime,
        interval=24 * 3600 // time_resolution,
        dateformat=date_format,
    )

    # Load the dataset inventory within a given date range
    dataset_paths, dataset_times = inventory.get_sequence(
        start=time_start, end=time_end, use_end=True
    )

    return dataset_paths, dataset_times


def _get_inventory_filename(settings: ConfigDict) -> Path:
    filename_prefix = get_filename_prefix("inventory", settings)
    filename = f"{filename_prefix}.dat"

    repository_config: dict[str, Path] = settings.get("repository", {})
    repository_path = repository_config["path"]

    return repository_path / filename


def _get_datasource_info(
    settings: ConfigDict,
) -> tuple[Any, Any, str, int]:
    datasource_config = settings.section("datasource")
    channel = datasource_config["channel"]
    origin = datasource_config["origin"]
    scene = datasource_config.as_str("scene")
    time_resolution = datasource_config.as_int("time_resolution")
    return origin, channel, scene, time_resolution


def _get_inventory_info(settings: ConfigDict) -> tuple[str, str, str, Path]:
    repository_path = settings.as_path("repository.path")
    date_format = settings.as_str("date_format.input")
    time_start = settings.as_str("event.time_start")
    time_end = settings.as_str("event.time_end")
    return time_start, time_end, date_format, repository_path
