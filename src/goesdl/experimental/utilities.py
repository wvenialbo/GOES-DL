from datetime import datetime, timedelta
from math import ceil, floor, inf, nan
from pathlib import Path
from typing import Any, TypeGuard, cast

from numpy import abs, arange, float64, floating, integer, max, min, std, zeros
from numpy.typing import NDArray

_Array = NDArray[floating[Any]]
_Series = list[_Array]
_Settings = dict[str, Any]
_Spectrum = Any
_Spectra = list[_Spectrum]

_dependencies: dict[str, str] = {
    "goesdl": "goes-dl",
    "gudhi": "gudhi",
    "optype": "optype",
    "statsmodels": "statsmodels",
    "yaml": "pyyaml",
}

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

_prof_suffix = ".npz"


# ---------- Environment tool utilities ----------


def is_colab() -> bool:
    """Detecta si corremos en el entorno Google Colab."""
    from os import getenv

    return bool(getenv("COLAB_RELEASE_TAG"))


# ---------- Report printing utilities ----------


def print_separator(char: str = "=", length: int = 50) -> None:
    """Prints a customizable separator line."""
    print(char * length)


def print_line(length: int = 50) -> None:
    print_separator(char="-", length=length)


def print_bar(length: int = 50) -> None:
    print_separator(char="=", length=length)


def print_event_report(settings: _Settings) -> None:
    event_config: dict[str, str] = settings.get("event", {})

    # Extract values
    event_name = event_config.get("name", "N/A")
    time_start = event_config.get("time_start", "N/A")
    time_end = event_config.get("time_end", "N/A")

    # Print values
    print(f"Event name              : {event_name}")
    print(f"Coverage start time     : {time_start}")
    print(f"Coverage end time       : {time_end}")


def print_datasource_report(settings: _Settings) -> None:
    datasource_config: _Settings = settings.get("datasource", {})

    # Extract values
    project = datasource_config.get("project", "N/A")
    origin = ", ".join(datasource_config.get("origin", ["N/A"]))
    channel = datasource_config.get("channel", "N/A")
    scene = datasource_config.get("scene", "N/A")
    spatial_resolution = datasource_config.get("spatial_resolution", "N/A")
    time_resolution = datasource_config.get("time_resolution", "N/A")

    # Print values
    print(f"Datasets                : {project}")
    print(f"Satellite               : {origin}")
    print(f"Channel                 : {channel}")
    print(f"Scene                   : {scene}")
    print(f"Spatial resolution      : {spatial_resolution:>2.1f} km/pixel")
    print(f"Time resolution         : {time_resolution:>3d} frames/hour")


def print_repository_report(settings: _Settings) -> None:
    repo_config: dict[str, str] = settings.get("repository", {})

    # Extract values
    root_path = repo_config.get("root", "N/A")
    dataset_path = repo_config.get("path", "N/A")
    difference_directory = repo_config.get("difference", "N/A")
    profile_directory = repo_config.get("profile", "N/A")
    reprojection_directory = repo_config.get("reprojection", "N/A")

    # Print values
    print(f"Repository root path    : {root_path}")
    print(f"Dataset directory path  : {dataset_path}")
    print(f"Difference files path   : {difference_directory}")
    print(f"Profile files path      : {profile_directory}")
    print(f"Reprojection files path : {reprojection_directory}")


def print_setup_report(settings: _Settings) -> None:
    print_bar()
    print("Project configuration values")
    print_line()

    # Event configuration
    print_event_report(settings)

    print_line()

    # Datasource configuration
    print_datasource_report(settings)

    print_line()

    # Repository configuration
    print_repository_report(settings)

    print_bar()


def print_derived_parameters_report(
    settings: _Settings, params: _Settings
) -> None:
    vmax: float = params["vmax"]
    vmin: float = params["vmin"]

    print_bar()
    print("Computed Parameters")
    print_line()

    print(f"Minimum BT           : {vmin:>4.0f} K")
    print(f"Maximum BT           : {vmax:>4.0f} K")
    print_line()

    algorithm_config: _Settings = settings.get("algorithm", {})
    sampling_rate: int = algorithm_config["sampling_rate"]

    datasource_config: _Settings = settings.get("datasource", {})
    time_resolution: int = datasource_config["time_resolution"]

    resolution_ratio = f"{sampling_rate:>0.0f}:{time_resolution:>0.0f}"

    sequence_length: int = params["sequence_length"]
    sequence_step: int = params["sequence_step"]
    series_length: int = params["series_length"]

    print(f"Sequence length      : {sequence_length:>4d} data points")
    print(f"Sequence interval    : {sequence_step:>4d} data points")
    print(f"Time series lenght   : {series_length:>4d} data points")
    print(
        f"Ser./data res. ratio : {resolution_ratio:>4} data points/h",
    )
    print_line()

    ignore: int = params["ignore"]
    window: int = params["window"]

    x_min: float = params["x_min"]
    x_max: float = params["x_max"]

    print(
        f"Central mask         : {ignore:>4d} pixels   (~{x_min:.0f}-km)",
    )
    print(
        f"Analysis window      : {window:>4d} pixels   (~{x_max:.0f}-km)",
    )
    print_line()

    label, sep = "Analysis radii", ":"

    radii: list[float] = params["radii"]
    radii_km: list[float] = params["radii_km"]

    for radius, radius_km in zip(radii, radii_km):
        print(f"{label:<21}{sep} {radius:>4d}-th pixel (~{radius_km:.0f}-km)")
        label, sep = "", " "


def print_algorithm_parameters_report(settings: _Settings) -> None:
    """
    Prints a formatted report of the algorithm configuration.

    Args:
        config_data (dict): A dictionary containing the loaded configuration.
    """
    print_bar()
    print("Algorithm Parameters")

    algo_config: _Settings = settings.get("algorithm", {})

    # Extract values
    delta = algo_config.get("delta", "N/A")
    radius_min = algo_config.get("radius_min", "N/A")
    radius_step = algo_config.get("radius_step", "N/A")
    central_mask = algo_config.get("central_mask", "N/A")
    windows_size = algo_config.get("windows_size", "N/A")
    fft_size = algo_config.get("fft_size", "N/A")
    sampling_rate = algo_config.get("sampling_rate", "N/A")
    invert_difference = algo_config.get("invert_difference", "N/A")
    window_function = algo_config.get("window_function", "N/A")
    filter_frequency = algo_config.get("filter_frequency", "N/A")
    filter_bandwidth = algo_config.get("filter_bandwidth", "N/A")
    filter_order = algo_config.get("filter_order", "N/A")
    control_samples = algo_config.get("control_samples", "N/A")
    analytic_samples = algo_config.get("analytic_samples", "N/A")
    analytic_offset = algo_config.get("analytic_offset", "N/A")
    nperseg = algo_config.get("nperseg", "N/A")
    noverlap = algo_config.get("noverlap", "N/A")

    # Print values
    print_line()
    print(f"Profile difference offset     : {delta} hours")
    print(f"Invert profile difference     : {invert_difference}")
    print_line()
    print(f"Minimum analysis radius       : {radius_min} km")
    print(f"Analysis radius increment     : {radius_step} km")
    print_line()
    print(f"Central mask extent           : {central_mask}%")
    print(f"Analysis window extent        : {windows_size}%")
    print_line()
    print(f"FFT analysis block size       : {fft_size}")
    print(f"FFT window function           : {window_function}")
    print(f"FFT sampling rate             : {sampling_rate} frames/hour")
    print_line()
    print(f"Welch periodogram nperseg     : {nperseg}")
    print(f"Welch periodogram noverlap    : {noverlap}")
    print_line()
    print(f"Filter frequency (central)    : {filter_frequency} cycles/day")
    print(f"Filter bandwidth              : {filter_bandwidth} cycles/day")
    print(f"Filter order                  : {filter_order}")
    print_line()
    print(f"Interpolation control samples : {control_samples} samples/day")
    print(f"Spectral analytic samples     : {analytic_samples} samples/day")
    print(f"Analytic offset               : {analytic_offset} samples")

    print_bar()


# ---------- Settings information retrieval utilities ----------


def get_algorithm_info(
    settings: _Settings,
) -> tuple[float, float, float, float]:
    algorithm_config: dict[str, float] = settings.get("algorithm", {})

    # Extract values
    central_mask = algorithm_config.get("central_mask", nan)
    windows_size = algorithm_config.get("windows_size", nan)
    radius_min = algorithm_config.get("radius_min", nan)
    radius_step = algorithm_config.get("radius_step", nan)

    return central_mask, windows_size, radius_min, radius_step


def get_algorithm_extra(
    settings: _Settings,
) -> tuple[float, int, bool, str]:
    algorithm_config: _Settings = settings.get("algorithm", {})

    # Extract values
    delta: float = algorithm_config.get("delta", nan)
    sampling_rate: int = algorithm_config.get("sampling_rate", 0)
    invert_difference: bool = algorithm_config.get("invert_difference", False)
    diff_mode = "reversed" if invert_difference else "direct"

    return delta, sampling_rate, invert_difference, diff_mode


def get_event_info(
    settings: _Settings, flat_time: bool = False
) -> tuple[str, str, str]:
    event_config: dict[str, str] = settings.get("event", {})

    # Extract values
    event_name = event_config.get("name", "N/A")
    time_start = event_config.get("time_start", "N/A")
    time_end = event_config.get("time_end", "N/A")

    if flat_time:
        time_start = time_start.replace("-", "").replace(":", "")
        time_end = time_end.replace("-", "").replace(":", "")

    return event_name, time_start, time_end


# ---------- Profile loading utilities ----------


def load_profile(profile_directory: Path, path: str) -> _Array:
    # Load the profile data
    profile_data = load_profile_data(profile_directory, path)

    profile: _Array = profile_data["profile"]

    return profile


def load_profile_data(profile_directory: Path, path: str) -> _Settings:
    from numpy import load

    # Create the profile file path
    profile_path = Path(path)
    profile_path = profile_path.with_suffix(_prof_suffix)
    profile_path = profile_directory / profile_path.name

    # Load the profile data
    profile_data: _Settings = load(profile_path)

    return profile_data


# ---------- Project initialisation ----------


def initialize_project(
    event_settings_filepath: Path | str,
    config_settings_filepath: Path | str,
    verbose: bool = True,
) -> _Settings:
    if verbose:
        print_bar()
        print("Initialising project...")

    # --- Setup the environment
    _setup_environment(verbose)

    if verbose:
        print("Loading configuration files...")

    # --- load default settings
    default_settings = _load_config(config_settings_filepath, verbose)

    # --- load event settings
    event_settings = _load_config(event_settings_filepath, verbose)

    # --- Initialise settings
    settings = _initialize_settings(default_settings, event_settings, verbose)

    # --- Initialise data (for remote environments)
    _initialize_data(settings, verbose)

    if verbose:
        print("Project initialised!")
        print_setup_report(settings)

    return settings


def reload_project(
    event_settings_filepath: Path | str,
    config_settings_filepath: Path | str,
    verbose: bool = True,
) -> _Settings:
    if verbose:
        print_bar()
        print("Loading configuration files...")

    # --- load default settings
    default_settings = _load_config(config_settings_filepath, verbose)

    # --- load event settings
    event_settings = _load_config(event_settings_filepath, verbose)

    # --- Initialise settings
    settings = _initialize_settings(default_settings, event_settings, verbose)

    if verbose:
        print("Project reloaded!")
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


def _load_config(settings_filepath: Path | str, verbose: bool) -> _Settings:
    """Loads the configuration from a YAML file."""
    from yaml import YAMLError, safe_load

    try:
        settings_filepath = Path(settings_filepath)
        with open(settings_filepath, "r") as file:
            config = safe_load(file)
        if verbose:
            print(f"... configuration loaded from '{settings_filepath.name}'")
        return cast(_Settings, config)
    except FileNotFoundError as error:
        raise ValueError(
            f"The configuration file '{settings_filepath}' was not found"
        ) from error
    except YAMLError as error:
        raise ValueError(f"Error parsing the YAML file: {error}") from error


def _initialize_settings(
    default_settings: _Settings, event_settings: _Settings, verbose: bool
) -> _Settings:
    if verbose:
        print("Initialising configuration...")

    settings = default_settings | event_settings

    _initialize_paths(settings, verbose)

    if verbose:
        print("Configuration initialised...")

    return settings


def _initialize_paths(settings: _Settings, verbose: bool) -> None:
    if verbose:
        print("Initiliasing repository paths...")

    event_config: dict[str, str] = settings.get("event", {})
    repository_config: _Settings = settings.get("repository", {})

    # Extract values
    event_name = event_config["name"]

    # Set the root path to the data repositories
    root = Path(repository_config["root"])
    repository_config["root"] = root

    # Set the path of the datasets repository for the event
    path = root / event_name
    repository_config["path"] = path

    # Set the path for the difference matrix files
    repository_config["difference"] = path / "difference"

    # Set the path for the radial profile array files
    repository_config["profile"] = path / "profile"

    # Set the path for the reprojected matrix files
    repository_config["reprojection"] = path / "reprojection"

    _rename_legacy_paths(settings, verbose)

    if verbose:
        print("Repository paths initialised...")


def _rename_legacy_paths(settings: _Settings, verbose: bool) -> None:
    if verbose:
        print("Updating legacy paths...")

    repository_config: dict[str, Path] = settings.get("repository", {})

    legacy_map = {
        "difference": "differences",
        "profile": "profiles",
        "reprojection": "reprojected",
    }

    cfg_suffix = ".cfg"

    path = repository_config["path"]

    for new_folder_name, old_folder_name in legacy_map.items():
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


def _initialize_data(settings: _Settings, verbose: bool) -> None:
    """Extracts the data ZIP file if it exists in Google Colab."""
    from zipfile import ZipFile

    if not is_colab():
        return

    if verbose:
        print("Mounting uploaded data...")

    event_config: dict[str, str] = settings.get("event", {})
    repository_config: _Settings = settings.get("repository", {})

    event_name = event_config["name"]
    repository_path: Path = repository_config["path"]

    data_archives = ["reprojection", "difference", "profile"]

    for archive in data_archives:
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


# ---------- Inventory loading ----------


def load_inventory(settings: _Settings) -> tuple[list[str], list[float]]:
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


def _load_inventory_any(settings: _Settings) -> tuple[list[str], list[float]]:
    datasource_config: dict[str, str] = settings.get("datasource", {})

    project = datasource_config["project"]

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


def _load_inventory_gr(settings: _Settings) -> tuple[list[str], list[float]]:
    # Import the coverage time info, locator, and dataset inventory
    from goesdl.downloader import DatasetInventory
    from goesdl.goesr import GOESCoverageTime, GOESProductLocatorCMIP

    print("... using GOES-R imagery product locator")

    datasource_config: _Settings = settings.get("datasource", {})
    channel: str = datasource_config["channel"]
    origin: str = datasource_config["origin"]
    scene: str = datasource_config["scene"]

    # Initialize the product locator for GOES-R datasets
    grlocator = GOESProductLocatorCMIP(
        scene=scene, channels=channel, origin=origin
    )

    repository_config: _Settings = settings.get("repository", {})
    repository_path: Path = repository_config["path"]
    time_resolution: int = datasource_config["time_resolution"]

    format_config = settings.get("date_format", {})
    date_format: str = format_config["input"]

    # Initialize the inventory manager
    inventory = DatasetInventory(
        repository=repository_path,
        locator=grlocator,
        coverage=GOESCoverageTime,
        interval=3600 // time_resolution,
        dateformat=date_format,
    )

    event_config: dict[str, str] = settings.get("event", {})
    time_start = event_config["time_start"]
    time_end = event_config["time_end"]

    # Load the dataset inventory within a given date range
    dataset_paths, dataset_times = inventory.get_sequence(
        start=time_start, end=time_end, use_end=True
    )

    return dataset_paths, dataset_times


def _load_inventory_gb(
    settings: _Settings,
) -> tuple[list[str], list[float]]:
    # Import inventory loader, the GridSat product locator, and the
    # coverage time info loader
    from goesdl.downloader import DatasetInventory
    from goesdl.gridsat import GridSatProductLocatorB1, GSCoverageTime

    print("... using GridSat-B1 imagery product locator")

    datasource_config: _Settings = settings.get("datasource", {})

    # Initialize the product locator for GridSat datasets
    gslocator = GridSatProductLocatorB1()

    repository_config: _Settings = settings.get("repository", {})
    repository_path: Path = repository_config["path"]
    time_resolution: int = datasource_config["time_resolution"]

    format_config = settings.get("date_format", {})
    date_format: str = format_config["input"]

    # Initialize the inventory manager
    inventory = DatasetInventory(
        repository=repository_path,
        locator=gslocator,
        coverage=GSCoverageTime,
        interval=3600 // time_resolution,
        dateformat=date_format,
    )

    event_config: dict[str, str] = settings.get("event", {})
    time_start = event_config["time_start"]
    time_end = event_config["time_end"]

    # Load the dataset inventory within a given date range
    dataset_paths, dataset_times = inventory.get_sequence(
        start=time_start, end=time_end, use_end=True
    )

    return dataset_paths, dataset_times


def _load_inventory_gs(
    settings: _Settings,
) -> tuple[list[str], list[float]]:
    # Import inventory loader, the GridSat product locator, and the
    # coverage time info loader
    from goesdl.downloader import DatasetInventory
    from goesdl.gridsat import GridSatProductLocatorGC, GSCoverageTime

    print("... using GridSat-GOES/CONUS imagery product locator")

    datasource_config: _Settings = settings.get("datasource", {})
    origin: list[str] = datasource_config["origin"]
    scene: str = datasource_config["scene"]

    # Initialize the product locator for GridSat datasets
    gslocator = GridSatProductLocatorGC(scene=scene, origins=origin)

    repository_config: _Settings = settings.get("repository", {})
    repository_path: Path = repository_config["path"]
    time_resolution: int = datasource_config["time_resolution"]

    format_config = settings.get("date_format", {})
    date_format: str = format_config["input"]

    # Initialize the inventory manager
    inventory = DatasetInventory(
        repository=repository_path,
        locator=gslocator,
        coverage=GSCoverageTime,
        interval=3600 // time_resolution,
        dateformat=date_format,
    )

    event_config: dict[str, str] = settings.get("event", {})
    time_start = event_config["time_start"]
    time_end = event_config["time_end"]

    # Load the dataset inventory within a given date range
    dataset_paths, dataset_times = inventory.get_sequence(
        start=time_start, end=time_end, use_end=True
    )

    return dataset_paths, dataset_times


def _get_inventory_filename(settings: _Settings) -> Path:
    event_name, time_start, time_end = get_event_info(settings, True)

    filename_base = f"s{time_start}_e{time_end}"
    filename = f"{event_name}_inventory_{filename_base}.dat"

    repository_config: dict[str, Path] = settings.get("repository", {})
    repository_path = repository_config["path"]

    return repository_path / filename


# ---------- Derived parameters computation or retrieval  ----------


def get_computed_parameters(
    settings: _Settings, dataset_paths: list[str]
) -> _Settings:
    from goesdl.fileio import load_metadata, save_metadata

    print_bar()

    # Retrieve or calculate derived parameters
    parameters_filename = _get_parameters_filename(settings)

    parameters_data: _Settings

    if parameters_filename.exists():
        # Just retrieve the precomputed parameters
        print("Retrieving precomputed parameters...")

        parameters_data = load_metadata(parameters_filename)

        print("Precomputed parameters retrieved!")

    else:
        # Compute parameters with values derived from data and other
        # parameters
        print("Computing derived parameters...")

        parameters_data = _compute_parameters(settings, dataset_paths)

        save_metadata(parameters_filename, parameters_data)

        print("Derived parameters computed!")

    print_derived_parameters_report(settings, parameters_data)

    print_bar()

    return parameters_data


def _compute_parameters(
    settings: _Settings, dataset_paths: list[str]
) -> _Settings:
    from numpy import inf, nanmax, nanmin

    algorithm_config: _Settings = settings.get("algorithm", {})
    central_mask: float = algorithm_config["central_mask"]
    windows_size: float = algorithm_config["windows_size"]
    radius_min: float = algorithm_config["radius_min"]
    radius_step: float = algorithm_config["radius_step"]
    delta_hours: float = algorithm_config["delta"]
    sampling_rate: int = algorithm_config["sampling_rate"]
    filter_frequency: float = algorithm_config["filter_frequency"]
    filter_bandwidth: float = algorithm_config["filter_bandwidth"]

    datasource_config: _Settings = settings.get("datasource", {})
    spatial_resolution: float = datasource_config["spatial_resolution"]
    time_resolution: int = datasource_config["time_resolution"]

    repository_config: dict[str, Path] = settings.get("repository", {})
    profile_directory: Path = repository_config["profile"]

    # Retrieve or calculate the derived parameters

    ignore = 0
    radii = [0]
    radius = 0
    vmin = inf
    vmax = -inf
    window = 0
    x_min = 0.0
    x_max = 0.0
    x_ticks = [0.0]

    # Compute parameters with values derived from data and other
    # parameters
    for dataset_path in dataset_paths:
        if not dataset_path:
            continue

        # Load the profile data
        profile_data = load_profile_data(profile_directory, dataset_path)

        if radius == 0:
            radius = profile_data["radius"]

            # Calculate the central-ignore and analysis sizes
            ignore = max(int(central_mask * radius / 100), 1)
            window = min(int(windows_size * radius / 100), radius)

            # Create the x-axis tick and limit values (kilometres per pixel)
            x_ticks = [spatial_resolution * (i + 0.5) for i in range(window)]
            x_min = spatial_resolution * ignore
            x_max = spatial_resolution * window

            # Create a list of radii for the analysis
            radius_max = x_max + radius_step
            nrange = ceil((radius_max - radius_min) / radius_step)

            radii = [
                floor(i * radius_step / spatial_resolution)
                for i in range(nrange)
                if x_min <= i * radius_step <= x_max
            ]

        profile = profile_data["profile"]
        vmax = max(vmax, nanmax(profile))
        vmin = min(vmin, nanmin(profile))

    # Calculate the effective offset and sampling interval
    time_offset = int(delta_hours * time_resolution)
    sampling_interval = time_resolution / sampling_rate

    # Sequence and time series lengths, and step size
    sequence_length = len(dataset_paths) - time_offset
    sequence_step = int(sampling_interval)
    series_length = ceil(sequence_length / sequence_step)

    if sampling_interval != sequence_step or sequence_step > time_resolution:
        raise ValueError(
            "`algorithm.sampling_rate` must be an integer "
            "submultiple of `datasource.time_resolution`"
        )

    # Compute the filter cut frequencies in cycles per hour
    filter_highcut = (filter_frequency + 0.5 * filter_bandwidth) / 24
    filter_lowcut = (filter_frequency - 0.5 * filter_bandwidth) / 24

    radii_km = [spatial_resolution * r for r in radii]

    return {
        "filter_highcut": filter_highcut,
        "filter_lowcut": filter_lowcut,
        "ignore": ignore,
        "radii": radii,
        "radii_km": radii_km,
        "radius": radius,
        "sequence_length": sequence_length,
        "sequence_step": sequence_step,
        "series_length": series_length,
        "time_offset": time_offset,
        "vmax": vmax,
        "vmin": vmin,
        "window": window,
        "x_min": x_min,
        "x_max": x_max,
        "x_ticks": x_ticks,
    }


def _get_parameters_filename(settings: _Settings) -> Path:
    event_name, time_start, time_end = get_event_info(settings, True)
    central_mask, windows_size, radius_min, radius_step = get_algorithm_info(
        settings
    )

    algorithm_config: dict[str, float] = settings.get("algorithm", {})
    filter_frequency = algorithm_config["filter_frequency"]
    filter_bandwidth = algorithm_config["filter_bandwidth"]

    filename_parts = [
        f"s{time_start}_e{time_end}",
        f"r{radius_min:0.0f}-{radius_step:0.0f}",
        f"s{windows_size:0.1f}-{central_mask:0.1f}",
        f"fc{filter_frequency:0.1f}-{filter_bandwidth:0.1f}",
    ]

    filename_base = "_".join(filename_parts)
    filename = f"{event_name}_parameters_{filename_base}.dat"

    repository_config: dict[str, Path] = settings.get("repository", {})
    repository_path = repository_config["path"]

    return repository_path / filename


# ---------- Time series handling utilities ----------


def trim_timeseries(
    input_series: list[list[float]], params: _Settings
) -> _Series:
    from goesdl.experimental.sequence import Sequencer

    print_bar()
    print("Trimming timeseries...")

    begin_offset = None
    series_length = 0
    output_series: _Series = []

    for time_series in input_series:
        trimmed_time_series, start, _ = Sequencer.trim(time_series)
        if begin_offset is None:
            begin_offset = start
            series_length = len(trimmed_time_series)
        output_series.append(cast(_Array, trimmed_time_series))

    # Update affected parameters
    params["begin_offset"] = begin_offset
    params["series_length"] = series_length

    print("Trimming finished!")

    if begin_offset:
        print_bar()
        sequence_length: int = params["sequence_length"]
        print(f"Sequence length    : {sequence_length:>4d} data points")
        print(f"Begin offset       : {begin_offset:>4d} data points")
        print(f"Time series lenght : {series_length:>4d} data points")
    else:
        print("No change in series length")

    print_bar()

    return output_series


def fill_timeseries(
    input_series: _Series, settings: _Settings
) -> tuple[_Series, NDArray[integer[Any]]]:
    from goesdl.experimental.imputation import SignalImputator
    from goesdl.experimental.sequence import Sequencer

    print_bar()
    print("Imputing timeseries...")

    algorithm_config: _Settings = settings.get("algorithm", {})
    control_samples: int = algorithm_config["control_samples"]
    sampling_rate: int = algorithm_config["sampling_rate"]

    # Sampling rate is in samples/hour
    samples_per_day = int(24 * sampling_rate)

    nan_interp = SignalImputator(samples_per_day, control_samples)

    output_series: _Series = []

    # Fill missing data using sparse cubic spline interpolation
    for time_series in input_series:
        filled_time_series = nan_interp.fill(time_series)
        output_series.append(cast(_Array, filled_time_series))

    # Get the indices of the original gaps
    sequencer = Sequencer(sampling_rate)

    gap_indices = sequencer.gap_indices(input_series[0])

    print("Imputing finished!")

    if gap_indices.size:
        print_bar()
        print(f"Imputed values : {gap_indices.size:>4d} data points")
    else:
        print("No change in series content")

    print_bar()

    return output_series, gap_indices


def subsample_timeseries(
    input_series: _Series, settings: _Settings, params: _Settings
) -> _Series:
    print_bar()

    algorithm_config: _Settings = settings.get("algorithm", {})
    analytic_samples: int = algorithm_config["analytic_samples"]
    analytic_offset: int = algorithm_config["analytic_offset"]
    sampling_rate: int = algorithm_config["sampling_rate"]

    datasource_settings: _Settings = settings["datasource"]
    time_resolution: int = datasource_settings["time_resolution"]

    output_series: _Series

    # Sampling rate must be in samples/hour
    new_sampling_rate = analytic_samples // 24

    if sampling_rate < time_resolution or (
        new_sampling_rate == time_resolution and analytic_offset == 0
    ):
        message = (
            "Timeseries is already subsampled!"
            if sampling_rate < time_resolution
            else "No subsampling required!"
        )

        print(message)
        output_series = [time_series.copy() for time_series in input_series]

        begin_offset = params["begin_offset"]
        series_length = params["series_length"]

    else:
        print("Subsampling timeseries...")

        # Sampling rate is in samples/hour
        samples_per_day = int(24 * time_resolution)

        step = samples_per_day // analytic_samples
        begin = analytic_offset
        end: int = params["series_length"] + step

        output_series = [
            time_series[begin:end:step] for time_series in input_series
        ]

        print("Subsampling finished!")

        # Update affected parameters
        begin_offset = params["begin_offset"]
        begin_offset += analytic_offset
        series_length = len(output_series[0])

        params["begin_offset"] = begin_offset
        params["series_length"] = series_length

        sampling_rate = new_sampling_rate

    print_bar()

    params["sampling_rate"] = sampling_rate

    print(f"Sampling rate      : {sampling_rate:>4d} samples/h")
    print(f"Begin offset       : {begin_offset:>4d} data points")
    print(f"Time series lenght : {series_length:>4d} data points")

    print_bar()

    return output_series


def detrend_timeseries(input_series: _Series) -> tuple[_Series, _Series]:
    from goesdl.experimental.sequence import Sequencer

    print_bar()
    print("Detrending timeseries...")

    output_series: _Series = []
    output_tendencies: _Series = []

    for time_series in input_series:
        detrended_time_series = Sequencer.detrend(time_series)
        output_series.append(cast(_Array, detrended_time_series))

        tendency_component = time_series - detrended_time_series
        output_tendencies.append(tendency_component)

    print("Detrending finished!")
    print_bar()

    return output_series, output_tendencies


def calculate_mean_timeseries(
    original_time_series: _Series,
    detrended_time_series: _Series,
    settings: _Settings,
    parameters: _Settings,
) -> dict[str, _Array]:
    from goesdl.experimental.align import SignalAligner
    from goesdl.experimental.sequence import Sequencer

    print_bar()
    print("Computing mean timeseries...")

    algorithm_config: _Settings = settings.get("algorithm", {})
    sampling_rate: int = algorithm_config["sampling_rate"]

    # Calculate the incoherent mean time series
    incoherent_mean_timeseries = Sequencer.average(original_time_series)

    # Calculate the detrended incoherent mean time series
    detrended_mean_timeseries = Sequencer.detrend(incoherent_mean_timeseries)

    # Calculate the coherent mean time series
    event_settings: dict[str, int] = settings["event"]
    reference_series = event_settings["reference_series"]

    filter_order: int = algorithm_config["filter_order"]

    filter_params = None

    if filter_order != 0:
        filter_lowcut: float = parameters["filter_lowcut"]
        filter_highcut: float = parameters["filter_highcut"]

        filter_params = (filter_lowcut, filter_highcut, filter_order)

    aligner = SignalAligner(sampling_rate, filter_params)

    aligner.align(detrended_time_series, reference_series)
    coherent_mean_timeseries = aligner.signal

    mean_timeseries: _Settings = {
        "incoherent_mean_timeseries": incoherent_mean_timeseries,
        "detrended_mean_timeseries": detrended_mean_timeseries,
        "coherent_mean_timeseries": coherent_mean_timeseries,
    }

    print("Mean timeseries computed successfully!")
    print_bar()

    return mean_timeseries


def filter_timeseries(
    detrended_timeseries: _Series,
    mean_timeseries: dict[str, _Array],
    settings: _Settings,
    parameters: _Settings,
) -> tuple[_Series, dict[str, _Array]]:
    from goesdl.experimental.sequence import Sequencer

    algorithm_config: dict[str, int] = settings["algorithm"]
    filter_frequency = algorithm_config["filter_frequency"]

    print_bar()

    mean_series: dict[str, _Array] = {}

    if filter_frequency == 0:
        print("No filtering required!")
        print_bar()
        return detrended_timeseries.copy(), mean_timeseries.copy()

    print("Filtering timeseries...")

    sampling_rate = algorithm_config["sampling_rate"]
    filter_bandwidth = algorithm_config["filter_bandwidth"]
    filter_order = algorithm_config["filter_order"]
    filter_lowcut: float = parameters["filter_lowcut"]
    filter_highcut: float = parameters["filter_highcut"]

    sequencer = Sequencer(sampling_rate)

    output_series: _Series = []

    for time_series in detrended_timeseries:
        filtered_time_series = sequencer.bandpass_filter(
            time_series, filter_lowcut, filter_highcut, order=filter_order
        )
        output_series.append(cast(_Array, filtered_time_series))

    for key, time_series in mean_timeseries.items():
        filtered_time_series = sequencer.bandpass_filter(
            time_series, filter_lowcut, filter_highcut, order=filter_order
        )
        mean_series[key] = cast(_Array, filtered_time_series)

    print("Filtering finished!")
    print_bar()

    print(f"Central frequency : {filter_frequency:>4.1f} c/d")
    print(f"Bandpass width    : {filter_bandwidth:>4.1f} c/d")
    print(f"Butterworth order : {filter_order:>4}th")
    print_bar()

    return output_series, mean_series


# ---------- Spectrum analysis utilities ----------


def analyze_spectra(
    detrended_timeseries: _Series,
    mean_timeseries: dict[str, _Array],
    settings: _Settings,
    parameters: _Settings,
) -> tuple[_Spectra, dict[str, _Spectrum]]:
    from goesdl.experimental.fourier import FourierAnalysis

    print_bar()
    print("Analysing timeseries spectra...")

    algorithm_config: dict[str, Any] = settings["algorithm"]
    sampling_rate: int = algorithm_config["sampling_rate"]
    fft_size: int | None = algorithm_config["fft_size"]
    window_function: str = algorithm_config["window_function"]
    noise: str = algorithm_config["noise_type"]

    series_length: int = parameters["series_length"]

    nperseg, noverlap = _get_welch_params(settings, parameters)

    analysers: _Spectra = []
    mean_analysers: dict[str, _Spectrum] = {}

    actual_fft_size: int | None = None

    # Perform Fourier Analysis
    for time_series in detrended_timeseries:
        analyser = FourierAnalysis(
            sampling_rate=sampling_rate,
            signal_size=series_length,
            fft_size=fft_size,
            window=window_function,
            dewindow_threshold=0.1,
        )

        analyser.apply(time_series, nperseg, noverlap, noise)

        analysers.append(analyser)

        if actual_fft_size is None:
            actual_fft_size = analyser.fft_size

    for key, time_series in mean_timeseries.items():
        analyser = FourierAnalysis(
            sampling_rate=sampling_rate,
            signal_size=series_length,
            fft_size=fft_size,
            window=window_function,
            dewindow_threshold=0.1,
        )

        analyser.apply(time_series, nperseg, noverlap, noise)

        mean_analysers[key] = analyser

    print("Spectra analysis finished!")
    print_bar()

    required_fft_size = f"{fft_size:>4d}" if fft_size else "(automatic)"
    effective_fft_size = (
        f"{actual_fft_size:>4d}" if actual_fft_size else "(unknown)"
    )

    print(f"Required FFT spectrum size  : {required_fft_size}")
    print(f"Effective FFT spectrum size : {effective_fft_size}")

    print_bar()

    return analysers, mean_analysers


def _get_welch_params(
    settings: _Settings, parameters: _Settings
) -> tuple[int | None, int | None]:
    algorithm_config: dict[str, Any] = settings["algorithm"]
    nperseg = algorithm_config["nperseg"]
    noverlap = algorithm_config["noverlap"]
    sampling_rate: int = algorithm_config["sampling_rate"]

    series_length: int = parameters["series_length"]

    def valid_nproportion(x: Any) -> TypeGuard[float]:
        return isinstance(x, float) and 0 < x <= 1.0

    def valid_block(x: Any) -> TypeGuard[int]:
        if not isinstance(x, int):
            return False
        block_size = floor(x * 24 * sampling_rate)
        return 0 < block_size <= series_length

    def valid_oproportion(x: Any) -> TypeGuard[float]:
        return isinstance(x, float) and 0 <= x <= 0.75

    def valid_overlap(x: Any) -> TypeGuard[int]:
        if not isinstance(x, int) or not isinstance(nperseg, int):
            return False
        return 0 <= x < nperseg

    if nperseg is None:
        nperseg = None
    elif valid_nproportion(nperseg):
        nperseg = floor(nperseg * series_length)
    elif valid_block(nperseg):
        nperseg = floor(nperseg * 24 * sampling_rate)
    else:
        raise ValueError("Invalid `nperseg` value")

    if noverlap is None:
        noverlap = None
    elif valid_oproportion(noverlap) and isinstance(nperseg, int):
        noverlap = floor(noverlap * nperseg)
    elif not valid_overlap(noverlap):
        raise ValueError("Invalid `noverlap` value")

    return nperseg, noverlap


def _find_diurnal_cycle(input_analyser: Any) -> _Array:
    from goesdl.experimental.fourier import FourierAnalysis

    analyser = cast(FourierAnalysis, input_analyser)

    if not (diurnal := analyser.find_frequency(1.0 / 24)):
        return zeros((analyser.signal_size,), dtype=float64)

    diurnal_index = diurnal[0]

    time_series = analyser.reconstruct_components(diurnal_index)

    return cast(_Array, time_series)


def find_diurnal_cycle(
    analysers: _Spectra, input_mean_analysers: dict[str, _Spectrum]
) -> tuple[_Series, dict[str, _Array]]:
    diurnal_cycles: _Series = []

    for analyser in analysers:
        diurnal_cycle = _find_diurnal_cycle(analyser)
        diurnal_cycles.append(diurnal_cycle)

    mean_diurnal_cycles: dict[str, _Array] = {}

    for key, analyser in input_mean_analysers.items():
        diurnal_cycle = _find_diurnal_cycle(analyser)
        mean_diurnal_cycles[key] = diurnal_cycle

    return diurnal_cycles, mean_diurnal_cycles


def get_dominant_cycle(
    input_analysers: _Spectra, input_mean_analysers: dict[str, _Spectrum]
) -> tuple[_Series, dict[str, _Array]]:
    from goesdl.experimental.fourier import FourierAnalysis

    analysers = cast(list[FourierAnalysis], input_analysers)
    mean_analysers = cast(dict[str, FourierAnalysis], input_mean_analysers)

    dominant_cycles: _Series = []

    for analyser in analysers:
        dominant_cycle = analyser.reconstruct_components(indices=0)
        dominant_cycles.append(cast(_Array, dominant_cycle))

    mean_dominant_cycles: dict[str, _Array] = {}

    for key, analyser in mean_analysers.items():
        dominant_cycle = analyser.reconstruct_components(indices=0)
        mean_dominant_cycles[key] = cast(_Array, dominant_cycle)

    return dominant_cycles, mean_dominant_cycles


# ---------- Plotting helpers ----------


def get_time_ticks(
    settings: _Settings, parameters: _Settings, tick_interval: int = 6
) -> tuple[_Array, list[int], float]:
    event_config: dict[str, str] = settings.get("event", {})
    time_start = event_config.get("time_start", "N/A")

    format_config: dict[str, str] = settings.get("date_format", {})
    date_format = format_config["input"]

    algorithm_config: dict[str, float] = settings.get("algorithm", {})
    sampling_rate = algorithm_config["sampling_rate"]

    begin_offset: float = parameters["begin_offset"]
    series_length: float = parameters["series_length"]

    dt_start = datetime.strptime(time_start, date_format)
    dt_start += timedelta(hours=begin_offset / sampling_rate)
    dt_end = dt_start + timedelta(hours=series_length / sampling_rate)

    time_hours = (dt_end - dt_start).total_seconds() / 3600
    duration_per_point_hours = 1 / sampling_rate

    start_hour_of_day = dt_start.hour

    first_real_tick_hour_of_day = (
        start_hour_of_day // tick_interval
    ) * tick_interval

    if first_real_tick_hour_of_day < start_hour_of_day:
        first_real_tick_hour_of_day += tick_interval

    first_tick_position_on_x_axis = (
        first_real_tick_hour_of_day - start_hour_of_day
    )

    tick_position = arange(
        first_tick_position_on_x_axis,
        time_hours + duration_per_point_hours,
        tick_interval,
    )

    tick_label = [
        (int(first_real_tick_hour_of_day + i * tick_interval)) % 24
        for i in range(len(tick_position))
    ]

    return tick_position, tick_label, time_hours


def get_date_markers(
    settings: _Settings, parameters: _Settings, label_format: str = "%Y-%m-%d"
) -> tuple[list[float], list[str]]:
    event_config: dict[str, str] = settings.get("event", {})
    time_start = event_config.get("time_start", "N/A")

    format_config: dict[str, str] = settings.get("date_format", {})
    date_format = format_config["input"]

    algorithm_config: dict[str, float] = settings.get("algorithm", {})
    sampling_rate = algorithm_config["sampling_rate"]

    begin_offset: float = parameters["begin_offset"]
    series_length: float = parameters["series_length"]

    dt_start = datetime.strptime(time_start, date_format)
    dt_start_offsetted = dt_start + timedelta(
        hours=begin_offset / sampling_rate
    )
    dt_end = dt_start_offsetted + timedelta(
        hours=series_length / sampling_rate
    )

    time_hours = (dt_end - dt_start_offsetted).total_seconds() / 3600

    hours_since_last_midnight = (
        dt_start_offsetted.hour + dt_start_offsetted.minute / 60.0
    )
    hours_to_next_midnight = (24 - hours_since_last_midnight) % 24

    if (
        hours_to_next_midnight == 0
        and dt_start_offsetted.hour == 0
        and dt_start_offsetted.minute == 0
    ):
        first_midnight_position = 0.0
    else:
        first_midnight_position = hours_to_next_midnight

    midnight_pos = [
        first_midnight_position + (j * 24)
        for j in range(int(ceil(time_hours / 24)) + 2)
    ]

    midnight_pos = [pos for pos in midnight_pos if 0 <= pos <= time_hours]

    date_labels: list[str] = []
    for pos in midnight_pos:
        current_datetime = dt_start_offsetted + timedelta(hours=pos)
        date_labels.append(current_datetime.strftime(label_format))

    return midnight_pos, date_labels


def combine_tick_labels(
    tick_positions: list[float] | _Array,
    tick_labels_hours: list[int],
    midnight_positions: list[float],
    midnight_labels_dates: list[str],
) -> list[str]:
    final_tick_labels: list[str] = []

    midnight_label_index = 0

    for i, pos in enumerate(tick_positions):
        label_hour = tick_labels_hours[i]

        if label_hour == 0 and midnight_label_index < len(midnight_positions):
            if abs(pos - midnight_positions[midnight_label_index]) < 0.1:
                final_tick_labels.append(
                    midnight_labels_dates[midnight_label_index]
                )
                midnight_label_index += 1
            else:
                final_tick_labels.append(f"{label_hour:02d}:00h")
        else:
            final_tick_labels.append(f"{label_hour:02d}:00h")

    return final_tick_labels


def calculate_global_limits(
    input_series: _Series,
) -> tuple[float, float, float, float]:
    max_abs_val = 0.0
    max_std_val = 0.0

    global_min_val = inf
    global_max_val = -inf

    for series in input_series:
        current_series_max_abs = max(abs(series))
        if current_series_max_abs > max_abs_val:
            max_abs_val = float(current_series_max_abs)

        current_series_max_std = std(series)
        if current_series_max_std > max_std_val:
            max_std_val = float(current_series_max_std)

        current_series_min = min(series)
        current_series_max = max(series)

        if current_series_min < global_min_val:
            global_min_val = float(current_series_min)

        if current_series_max > global_max_val:
            global_max_val = float(current_series_max)

    return global_min_val, global_max_val, max_abs_val, max_std_val
