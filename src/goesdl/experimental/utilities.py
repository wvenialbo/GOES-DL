from logging import INFO, WARNING, Logger, StreamHandler, getLogger
from math import ceil, floor
from pathlib import Path
from typing import Any, cast

from numpy import floating, integer
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

_logger_name = ""
_prof_suffix = ".npz"
_sepbar = "=" * 50


def notify(level: int, message: str) -> None:
    if not _logger_name:
        return
    logger = getLogger(_logger_name)
    logger.log(level, message)


def get_algorithm_info(
    settings: _Settings,
) -> tuple[float, float, float, float]:
    algorithm_param: dict[str, float] = settings["algorithm"]
    central_mask = algorithm_param["central_mask"]
    windows_size = algorithm_param["windows_size"]
    radius_min = algorithm_param["radius_min"]
    radius_step = algorithm_param["radius_step"]

    return central_mask, windows_size, radius_min, radius_step


def get_algorithm_extra(
    settings: _Settings,
) -> tuple[float, int, bool, str]:
    algorithm_param: _Settings = settings["algorithm"]
    delta: float = algorithm_param["delta"]
    sampling_rate: int = algorithm_param["sampling_rate"]
    invert_difference: bool = algorithm_param["invert_difference"]
    diff_mode = "reversed" if invert_difference else "direct"

    return delta, sampling_rate, invert_difference, diff_mode


def get_event_info(
    settings: _Settings, flat_time: bool = False
) -> tuple[str, str, str]:
    event_settings: dict[str, str] = settings["event"]
    event_name = event_settings["name"]
    time_start = event_settings["time_start"]
    time_end = event_settings["time_end"]

    if flat_time:
        time_start = time_start.replace("-", "").replace(":", "")
        time_end = time_end.replace("-", "").replace(":", "")

    return event_name, time_start, time_end


def _move_legacy(old_reprojection: Path, reprojection: Path) -> None:
    notify(WARNING, "Renombrando archivos heredados...")
    new_reprojection = old_reprojection.parent / reprojection.name
    old_reprojection.rename(new_reprojection)

    cfg_sfx = ".cfg"

    old_reprojection = old_reprojection.with_suffix(cfg_sfx)
    old_reprojection.rename(new_reprojection.with_suffix(cfg_sfx))


def setup_logging(level: int, name: str = "__laboratory__") -> None:
    global _logger_name
    _logger_name = name

    logger = getLogger(name)
    logger.setLevel(level)

    if not logger.handlers:
        from sys import stdout

        handler = StreamHandler(stdout)
        handler.setLevel(level)
        logger.addHandler(handler)


def set_logger(logger: Logger | str) -> None:
    global _logger_name
    _logger_name = logger.name if isinstance(logger, Logger) else logger


def initialize_data(settings: _Settings) -> None:
    """Extrae el archivo ZIP de perfiles si existe en Google Colab."""
    from zipfile import ZipFile

    if not is_colab():
        notify(INFO, _sepbar)
        return

    notify(INFO, "Inicializando datos en Google Colab...")

    data_archives = ["reprojection", "differences", "profiles"]

    event_name: str = settings["event"]["name"]
    repository_path: Path = settings["repository"]["path"]

    for archive in data_archives:
        zipfile_path = Path(f"./{event_name}_{archive}.zip")
        if zipfile_path.exists():
            notify(
                INFO, f"Detectado archivo ZIP '{zipfile_path}'. Extrayendo..."
            )
            with ZipFile(zipfile_path, "r") as zip_ref:
                zip_ref.extractall(
                    repository_path
                )  # Extraer al repositorio de datos
            notify(
                INFO,
                f"ZIP file '{zipfile_path}' extraído en '{repository_path}'!",
            )

    notify(INFO, "Datos inicializados...")
    notify(INFO, _sepbar)


def initialize_settings(
    default_settings: _Settings, event_settings: _Settings
) -> _Settings:
    settings = default_settings | event_settings

    event_name: str = settings["event"]["name"]
    repo_settings: _Settings = settings["repository"]

    # Set the root path to the data repositories
    root = Path(repo_settings["root"])
    repo_settings["root"] = root

    # Set the path of the datasets repository for the event
    path = root / event_name
    repo_settings["path"] = path

    # Set the path for the difference matrix files
    repo_settings["differences"] = path / "differences"

    # Set the path for the radial profile array files
    repo_settings["profiles"] = path / "profiles"

    # Set the path for the reprojected matrix files
    reprojection = path / "reprojection"
    repo_settings["reprojection"] = reprojection

    old_reprojection = path / "reprojected"
    if not reprojection.exists() and old_reprojection.exists():
        _move_legacy(old_reprojection, reprojection)

    notify(INFO, "Configuración inicializada...")

    return settings


def is_colab() -> bool:
    """Detecta si corremos en el entorno Google Colab."""
    from os import getenv

    return bool(getenv("COLAB_RELEASE_TAG"))


def load_config(filepath: Path | str = "config.yaml") -> _Settings:
    """Carga la configuración desde un archivo YAML."""
    from yaml import YAMLError, safe_load

    try:
        filepath = Path(filepath)
        with open(filepath, "r") as file:
            config = safe_load(file)
        notify(INFO, f"Configuración cargada desde '{filepath.name}'...")
        return cast(_Settings, config)
    except FileNotFoundError as error:
        raise ValueError(
            f"Error: El archivo de configuración '{filepath}' no se encontró"
        ) from error
    except YAMLError as error:
        raise ValueError(
            f"Error al parsear el archivo YAML: {error}"
        ) from error


def setup_environment(logger: Logger | str = "") -> None:
    """Configura el entorno (instalaciones de librerías)."""
    from importlib.util import find_spec

    print(_sepbar)
    print("Configurando entorno...")

    if isinstance(logger, Logger):
        set_logger(logger)

    elif logger:
        setup_logging(INFO, logger)

    if _logger_name:
        print(f"Usando registro de eventos '{_logger_name}'...")

    if find_spec("IPython") is None:
        raise RuntimeError(
            "No está instalado el entorno 'IPython': pip install ipython"
        )

    from IPython.core.getipython import get_ipython

    ipython = get_ipython()  # type: ignore

    if not ipython:
        raise RuntimeError(
            "No hay ninguna instancia de InteractiveShell registrada"
        )

    dependencies = list(_dependencies.keys())

    for dependency in dependencies:
        if find_spec(dependency) is None:
            try:
                ipython.system(f"pip install {_dependencies[dependency]}")
            except NameError as error:
                raise RuntimeError(
                    f"No se pudo instalar '{dependency}', "
                    "asegúrate de ejecutar esto en Jupyter"
                ) from error

    notify(INFO, "Entorno configurado...")


def _load_inventory_gr(
    settings: _Settings,
) -> tuple[list[str], list[float]]:
    # Import the coverage time info, locator, and dataset inventory
    from goesdl.downloader import DatasetInventory
    from goesdl.goesr import GOESCoverageTime, GOESProductLocatorCMIP

    datasource_settings: _Settings = settings["datasource"]
    channel: str = datasource_settings["channel"]
    origin: str = datasource_settings["origin"]
    scene: str = datasource_settings["scene"]

    # Initialize the product locator for GOES-R datasets
    grlocator = GOESProductLocatorCMIP(
        scene=scene, channels=channel, origin=origin
    )

    repo_settings: _Settings = settings["repository"]
    repository_path: Path = repo_settings["path"]
    time_resolution: int = datasource_settings["time_resolution"]
    date_format: str = settings["date_format"]["input"]

    # Initialize the inventory manager
    inventory = DatasetInventory(
        repository=repository_path,
        locator=grlocator,
        coverage=GOESCoverageTime,
        interval=3600 // time_resolution,
        dateformat=date_format,
    )

    notify(INFO, "Loading dataset inventory...\n")

    event_settings: dict[str, str] = settings["event"]
    time_start = event_settings["time_start"]
    time_end = event_settings["time_end"]

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

    datasource_settings: _Settings = settings["datasource"]
    origin: list[str] = datasource_settings["origin"]
    scene: str = datasource_settings["scene"]

    # Initialize the product locator for GridSat datasets
    gslocator = GridSatProductLocatorGC(scene=scene, origins=origin)

    repo_settings: _Settings = settings["repository"]
    repository_path: Path = repo_settings["path"]
    time_resolution: int = datasource_settings["time_resolution"]
    date_format: str = settings["date_format"]["input"]

    # Initialize the inventory manager
    inventory = DatasetInventory(
        repository=repository_path,
        locator=gslocator,
        coverage=GSCoverageTime,
        interval=3600 // time_resolution,
        dateformat=date_format,
    )

    notify(INFO, "Loading dataset inventory...\n")

    event_settings: dict[str, str] = settings["event"]
    time_start = event_settings["time_start"]
    time_end = event_settings["time_end"]

    # Load the dataset inventory within a given date range
    dataset_paths, dataset_times = inventory.get_sequence(
        start=time_start, end=time_end, use_end=True
    )

    return dataset_paths, dataset_times


def _get_inventory_filename(settings: _Settings) -> Path:
    event_name, time_start, time_end = get_event_info(settings, True)

    filename_base = f"s{time_start}_e{time_end}"
    filename = f"{event_name}_inventory_{filename_base}.dat"

    repo_settings: dict[str, Path] = settings["repository"]
    repository_path = repo_settings["path"]

    return repository_path / filename


def load_inventory(settings: _Settings) -> tuple[list[str], list[float]]:
    from goesdl.fileio import load_metadata, save_metadata

    event_name, time_start, time_end = get_event_info(settings)

    notify(INFO, _sepbar)
    notify(INFO, f"Event name              : {event_name}")
    notify(INFO, f"Coverage UTC start time : {time_start}")
    notify(INFO, f"Coverage UTC end time   : {time_end}")
    notify(INFO, _sepbar)

    inventory_filename = _get_inventory_filename(settings)

    datasource_settings: dict[str, str] = settings["datasource"]
    project = datasource_settings["project"]

    # Retrieve the datasets inventory

    inventory_data: tuple[list[str], list[float]]

    if inventory_filename.exists():
        # Just retrieve the preloaded inventory
        notify(INFO, "Retrieving dataset inventory...")

        inventory_data = load_metadata(inventory_filename)
        dataset_paths, _ = inventory_data

    elif project == "GridSat":
        # Load the inventory from local repository
        inventory_data = _load_inventory_gs(settings)
        dataset_paths, _ = inventory_data

        save_metadata(inventory_filename, inventory_data)

    elif project == "GOES-R":
        # Load the inventory from local repository
        inventory_data = _load_inventory_gr(settings)
        dataset_paths, _ = inventory_data

        save_metadata(inventory_filename, inventory_data)

    else:
        raise ValueError(f"Base de datos '{project}' desconocida")

    total_files = len(dataset_paths)
    available_files = sum(path != "" for path in dataset_paths)
    missing_files = total_files - available_files

    FILES_AVAILABLE = available_files > 0

    if FILES_AVAILABLE:
        notify(
            INFO,
            f"Found {available_files} datasets of {total_files}, "
            f"missing {missing_files} datasets",
        )
    else:
        notify(
            INFO,
            "Unable to acquire files: no datasets "
            "found in the specified date range",
        )
    notify(INFO, _sepbar)

    return inventory_data


def _compute_parameters(
    settings: _Settings, dataset_paths: list[str]
) -> _Settings:
    from numpy import inf, load, nanmax, nanmin

    algo_settings: _Settings = settings["algorithm"]
    central_mask: float = algo_settings["central_mask"]
    windows_size: float = algo_settings["windows_size"]
    radius_min: float = algo_settings["radius_min"]
    radius_step: float = algo_settings["radius_step"]
    delta_hours: float = algo_settings["delta"]
    sampling_rate: int = algo_settings["sampling_rate"]
    filter_frequency: float = algo_settings["filter_frequency"]
    filter_bandwidth: float = algo_settings["filter_bandwidth"]

    repo_settings: dict[str, Path] = settings["repository"]

    datasource_settings: _Settings = settings["datasource"]
    spatial_resolution: float = datasource_settings["spatial_resolution"]
    time_resolution: int = datasource_settings["time_resolution"]

    profiles_path: Path = repo_settings["profiles"]

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

        # Create the profile file path
        profile_path = Path(dataset_path)
        profile_path = profile_path.with_suffix(_prof_suffix)
        profile_path = profiles_path / profile_path.name

        # Load the profile data
        profile_data = load(profile_path)

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
    series_lenght = ceil(sequence_length / sequence_step)

    if sampling_interval != sequence_step or sequence_step > time_resolution:
        raise ValueError(
            "`algorithm.sampling_rate` must be an integer "
            "submultiple of `datasource.time_resolution`"
        )

    # Compute the filter cut frequencies in cycles per hour
    filter_highcut = (filter_frequency + 0.5 * filter_bandwidth) / 24
    filter_lowcut = (filter_frequency - 0.5 * filter_bandwidth) / 24

    return {
        "filter_highcut": filter_highcut,
        "filter_lowcut": filter_lowcut,
        "ignore": ignore,
        "radii": radii,
        "radius": radius,
        "sequence_length": sequence_length,
        "sequence_step": sequence_step,
        "series_lenght": series_lenght,
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

    algo_settings: dict[str, float] = settings["algorithm"]
    filter_frequency = algo_settings["filter_frequency"]
    filter_bandwidth = algo_settings["filter_bandwidth"]

    filename_parts = [
        f"s{time_start}_e{time_end}",
        f"r{radius_min:0.0f}-{radius_step:0.0f}",
        f"s{windows_size:0.1f}-{central_mask:0.1f}",
        f"fc{filter_frequency:0.1f}-{filter_bandwidth:0.1f}",
    ]

    filename_base = "_".join(filename_parts)
    filename = f"{event_name}_parameters_{filename_base}.dat"

    repo_settings: dict[str, Path] = settings["repository"]
    repository_path = repo_settings["path"]

    return repository_path / filename


def _report_parameters(settings: _Settings, params: _Settings) -> None:
    vmax: float = params["vmax"]
    vmin: float = params["vmin"]

    notify(INFO, _sepbar)
    notify(INFO, f"Minimum BT           : {vmin:>4.0f} K")
    notify(INFO, f"Maximum BT           : {vmax:>4.0f} K")

    algo_settings: _Settings = settings["algorithm"]
    sampling_rate: int = algo_settings["sampling_rate"]

    datasource_settings: _Settings = settings["datasource"]
    time_resolution: int = datasource_settings["time_resolution"]

    resolution_ratio = f"{sampling_rate:>0.0f}:{time_resolution:>0.0f}"

    sequence_length: int = params["sequence_length"]
    sequence_step: int = params["sequence_step"]
    series_lenght: int = params["series_lenght"]

    notify(INFO, f"Sequence length      : {sequence_length:>4d} data points")
    notify(INFO, f"Sequence interval    : {sequence_step:>4d} data points")
    notify(INFO, f"Time series lenght   : {series_lenght:>4d} data points")
    notify(
        INFO,
        f"Ser./data res. ratio : {resolution_ratio:>4} data points/h",
    )

    spatial_resolution: float = datasource_settings["spatial_resolution"]

    ignore: int = params["ignore"]
    window: int = params["window"]

    x_min: float = params["x_min"]
    x_max: float = params["x_max"]

    notify(
        INFO,
        f"Central mask         : {ignore:>4d} pixels (~{x_min:.0f}-km)",
    )
    notify(
        INFO,
        f"Analysis window      : {window:>4d} pixels (~{x_max:.0f}-km)",
    )

    label, sep = "Analysis radii", ":"

    radii: list[int] = params["radii"]

    for r in radii:
        radius_km = spatial_resolution * r
        notify(
            INFO, f"{label:<21}{sep} {r:>4d}-th pixel (~{radius_km:.0f}-km)"
        )
        label, sep = "", " "


def get_computed_parameters(
    settings: _Settings, dataset_paths: list[str]
) -> _Settings:
    from goesdl.fileio import load_metadata, save_metadata

    notify(INFO, _sepbar)

    # Retrieve or calculate derived parameters
    parameters_filename = _get_parameters_filename(settings)

    parameters_data: _Settings

    if parameters_filename.exists():
        # Just retrieve the precomputed parameters
        notify(INFO, "Retrieving precomputed parameters...")

        parameters_data = load_metadata(parameters_filename)

        notify(INFO, "Precomputed parameters retrieved!")

    else:
        # Compute parameters with values derived from data and other
        # parameters
        parameters_data = _compute_parameters(settings, dataset_paths)

        save_metadata(parameters_filename, parameters_data)

        notify(INFO, "Derived parameters computed!")

    _report_parameters(settings, parameters_data)

    notify(INFO, _sepbar)

    return parameters_data


def trim_timeseries(
    input_series: list[list[float]], params: _Settings
) -> _Series:
    from goesdl.experimental.sequence import Sequencer

    notify(INFO, _sepbar)
    notify(INFO, "Trimming timeseries...")

    begin_offset = None
    series_lenght = 0
    output_series: _Series = []

    for time_series in input_series:
        trimmed_time_series, start, _ = Sequencer.trim(time_series)
        if begin_offset is None:
            begin_offset = start
            series_lenght = len(trimmed_time_series)
        output_series.append(cast(_Array, trimmed_time_series))

    # Update affected parameters
    params["begin_offset"] = begin_offset
    params["series_lenght"] = series_lenght

    notify(INFO, "Trimming finished!")

    if begin_offset:
        notify(INFO, _sepbar)
        sequence_length: int = params["sequence_length"]
        notify(INFO, f"Sequence length    : {sequence_length:>4d} data points")
        notify(INFO, f"Begin offset       : {begin_offset:>4d} data points")
        notify(INFO, f"Time series lenght : {series_lenght:>4d} data points")
    else:
        notify(INFO, "No change in series length")

    notify(INFO, _sepbar)

    return output_series


def fill_timeseries(
    input_series: _Series, settings: _Settings
) -> tuple[_Series, NDArray[integer[Any]]]:
    from goesdl.experimental.imputation import SignalImputator
    from goesdl.experimental.sequence import Sequencer

    notify(INFO, _sepbar)
    notify(INFO, "Imputing timeseries...")

    algo_settings: _Settings = settings["algorithm"]
    control_samples: int = algo_settings["control_samples"]
    sampling_rate: int = algo_settings["sampling_rate"]

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

    notify(INFO, "Imputing finished!")

    if gap_indices.size:
        notify(INFO, _sepbar)
        notify(INFO, f"Imputed values : {gap_indices.size:>4d} data points")
    else:
        notify(INFO, "No change in series content")

    notify(INFO, _sepbar)

    return output_series, gap_indices


def subsample_timeseries(
    input_series: _Series, settings: _Settings, params: _Settings
) -> _Series:
    notify(INFO, _sepbar)

    algo_settings: _Settings = settings["algorithm"]
    analytic_samples: int = algo_settings["analytic_samples"]
    analytic_offset: int = algo_settings["analytic_offset"]
    sampling_rate: int = algo_settings["sampling_rate"]

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

        notify(INFO, message)
        output_series = [time_series.copy() for time_series in input_series]

        begin_offset = params["begin_offset"]
        series_lenght = params["series_lenght"]

    else:
        notify(INFO, "Subsampling timeseries...")

        # Sampling rate is in samples/hour
        samples_per_day = int(24 * time_resolution)

        step = samples_per_day // analytic_samples
        begin = analytic_offset
        end: int = params["series_lenght"] + step

        output_series = [
            time_series[begin:end:step] for time_series in input_series
        ]

        notify(INFO, "Subsampling finished!")

        # Update affected parameters
        begin_offset = params["begin_offset"]
        begin_offset += analytic_offset
        series_lenght = len(output_series[0])

        params["begin_offset"] = begin_offset
        params["series_lenght"] = series_lenght

        sampling_rate = new_sampling_rate

    notify(INFO, _sepbar)

    params["sampling_rate"] = sampling_rate

    notify(INFO, f"Sampling rate      : {sampling_rate:>4d} samples/h")
    notify(INFO, f"Begin offset       : {begin_offset:>4d} data points")
    notify(INFO, f"Time series lenght : {series_lenght:>4d} data points")

    notify(INFO, _sepbar)

    return output_series


def detrend_timeseries(input_series: _Series) -> tuple[_Series, _Series]:
    from goesdl.experimental.sequence import Sequencer

    notify(INFO, _sepbar)
    notify(INFO, "Detrending timeseries...")

    output_series: _Series = []
    output_tendencies: _Series = []

    for time_series in input_series:
        detrended_time_series = Sequencer.detrend(time_series)
        output_series.append(cast(_Array, detrended_time_series))

        tendency_component = time_series - detrended_time_series
        output_tendencies.append(tendency_component)

    notify(INFO, "Detrending finished!")
    notify(INFO, _sepbar)

    return output_series, output_tendencies


def calculate_mean_timeseries(
    original_time_series: _Series,
    detrended_time_series: _Series,
    settings: _Settings,
    parameters: _Settings,
) -> dict[str, _Array]:
    from goesdl.experimental.align import SignalAligner
    from goesdl.experimental.sequence import Sequencer

    notify(INFO, _sepbar)
    notify(INFO, "Computing mean timeseries...")

    algo_settings: _Settings = settings["algorithm"]
    sampling_rate: int = algo_settings["sampling_rate"]

    # Calculate the incoherent mean time series
    incoherent_mean_timeseries = Sequencer.average(original_time_series)

    # Calculate the detrended incoherent mean time series
    detrended_mean_timeseries = Sequencer.detrend(incoherent_mean_timeseries)

    # Calculate the coherent mean time series
    event_settings: dict[str, int] = settings["event"]
    reference_series = event_settings["reference_series"]

    filter_order: int = algo_settings["filter_order"]

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

    notify(INFO, "Mean timeseries computed successfully!")
    notify(INFO, _sepbar)

    return mean_timeseries


def filter_timeseries(
    detrended_timeseries: _Series,
    mean_timeseries: dict[str, _Array],
    settings: _Settings,
    parameters: dict[str, float],
) -> tuple[_Series, dict[str, _Array]]:
    from goesdl.experimental.sequence import Sequencer

    algo_settings: dict[str, int] = settings["algorithm"]
    filter_frequency = algo_settings["filter_frequency"]

    notify(INFO, _sepbar)

    mean_series: dict[str, _Array] = {}

    if filter_frequency == 0:
        notify(INFO, "No filtering required!")
        notify(INFO, _sepbar)
        return detrended_timeseries.copy(), mean_timeseries.copy()

    notify(INFO, "Filtering timeseries...")

    sampling_rate = algo_settings["sampling_rate"]
    filter_bandwidth = algo_settings["filter_bandwidth"]
    filter_order = algo_settings["filter_order"]
    filter_lowcut = parameters["filter_lowcut"]
    filter_highcut = parameters["filter_highcut"]

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

    notify(INFO, "Filtering finished!")
    notify(INFO, _sepbar)

    print(f"Central frequency : {filter_frequency:>4.1f} c/d")
    print(f"Bandpass width    : {filter_bandwidth:>4.1f} c/d")
    print(f"Butterworth order : {filter_order:>4}th")
    notify(INFO, _sepbar)

    return output_series, mean_series


def compute_spectra(
    detrended_timeseries: _Series,
    mean_timeseries: dict[str, _Array],
    settings: _Settings,
    parameters: dict[str, float],
) -> tuple[_Spectra, dict[str, _Spectrum]]:
    from goesdl.experimental.fourier import FourierAnalysis

    analysers: _Spectra = []
    mean_analysers: dict[str, _Spectrum] = {}

    nperseg = None  # None (for periodogram) or min(4 * 24 * SERIES_RESOLUTION, series_lenght)
    noverlap = nperseg // 4 if nperseg else 0

    # Perform Fourier Analysis
    for filtered_time_series in bt_detrended_time_series + [
        aligner.signal,
        aligner_f.signal,
        detrended_reduced_time_series,
    ]:
        analyser = FourierAnalysis(
            sampling_rate=SERIES_RESOLUTION,
            signal_size=series_lenght,
            fft_size=FREQUENCY_SAMPLING_RATE,
            window=WINDOW_FUNCTION,
            dewindow_threshold=0.1,
        )

        analyser.apply(filtered_time_series, nperseg, noverlap)

        analysers.append(analyser)

    return analysers, mean_analysers
