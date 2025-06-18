from collections.abc import Callable
from typing import Any, Literal, cast

from matplotlib import pyplot as plt
from numpy import floating, ndarray
from numpy.typing import NDArray

_Array = NDArray[floating[Any]]
_Series = list[_Array]
_Settings = dict[str, Any]
_Loc = Literal["left", "center", "right"] | None

_Spectrum = Any
_Spectra = list[_Spectrum]


class _PlotConfig:
    config: _Settings
    params: _Settings
    ncount: int

    def __init__(
        self, config: _Settings, params: _Settings, ncount: int
    ) -> None:
        self.config = config
        self.params = params
        self.ncount = ncount

    def __getitem__(self, name: str) -> list[Any]:
        if name in self.params:
            value = self.params[name]
        elif name in self.config:
            value = self.config[name]
        else:
            value = None
        if isinstance(value, list):
            return cast(list[Any], value)  # type: ignore
        return [value for _ in range(self.ncount)]

    def get(self, name: str, all: bool = False) -> Any:
        if all:
            return self.get_all(name)
        if name in self.params:
            return self.params[name]
        return self.config[name] if name in self.config else None

    def get_all(self, name: str) -> Any:
        from_config: list[Any] = (
            self.config[name] if name in self.config else []
        )
        from_params: list[Any] = (
            self.params[name] if name in self.params else []
        )
        return from_config + from_params


def _kwarg(value: Any) -> dict[str, Any]:
    return cast(dict[str, Any], value)


def _lsarg(value: Any) -> list[Any]:
    return cast(list[dict[str, Any]], value)


def _tparg(value: Any) -> tuple[Any, ...]:
    return cast(tuple[Any, ...], value)


def _set_property(name: str, gsetter: Any, config: _PlotConfig) -> None:
    if (value := config.get(name)) is not None:
        _set_value(gsetter, value)


def _set_title(name: str, gsetter: Any, config: _PlotConfig) -> None:
    if not (titles := config.get(name, True)):
        return
    if isinstance(titles, tuple):
        titles = _tparg(titles)
        locs: tuple[Any | None, ...]
        if len(titles) == 3:
            locs = ("left", "center", "right")
        elif len(titles) == 2:
            locs = ("left", "right")
        elif len(titles) == 1:
            locs = (None,)
        else:
            raise ValueError("Invalid title tuple")
        setter = cast(Callable[..., Any], gsetter)
        for title, loc in zip(titles, locs):
            setter(title, loc=cast(Any, loc))
    else:
        _set_value(gsetter, titles)


def _set_value(gsetter: Any, values: Any) -> None:
    setter = cast(Callable[..., Any], gsetter)
    if isinstance(values, (str, int, float, bool, ndarray)):
        setter(values)
    elif isinstance(values, dict):
        setter(**_kwarg(values))
    elif isinstance(values, list):
        for value in _lsarg(values):
            if isinstance(value, dict):
                setter(**value)
            else:
                setter(value)
    elif isinstance(values, tuple):
        setter(*_tparg(values))
    elif values is not None:
        raise ValueError("Invalid parameter type")


def _plotter(gsetter: Any) -> Any:
    setter = cast(Callable[..., Any], gsetter)

    def _set_plot(
        x: Any | None = None, y: Any | None = None, **kwargs: Any
    ) -> None:
        if x is not None and y is not None:
            setter(x, y, **kwargs)
        elif x is not None:
            setter(x, **kwargs)
        else:
            raise ValueError("Empty plotting argument")

    return _set_plot


def _plot_timeseries_item(series: _Series, config: _PlotConfig) -> None:
    xarray: list[_Array] = config["xarray"]
    label: list[str] = config["label"]
    markersize: list[float] = config["markersize"]
    alpha: list[float] = config["alpha"]
    linewidth: list[float] = config["linewidth"]
    linestyle: list[str] = config["linestyle"]
    color: list[str] = config["color"]

    # Set titles
    if titles := config.get("title", True):
        for title, loc in titles:
            plt.title(title, loc=loc)

    # Set limits
    if xlim := config.get("xlim"):
        plt.xlim(*xlim)

    if ylim := config.get("ylim"):
        plt.ylim(*ylim)

    # Set axis labels
    if xlabel := config.get("xlabel"):
        plt.xlabel(xlabel)

    if ylabel := config.get("ylabel"):
        plt.ylabel(ylabel)

    # Show grid
    if grid := config.get("grid"):
        visible, which, axis = grid
        plt.grid(visible, which, axis)

    # Configure ticks
    if (xticks := config.get("xticks")) is not None:
        plt.gca().set_xticks(xticks)

    if xticklabels := config.get("xticklabels"):
        plt.gca().set_xticklabels(**xticklabels)

    if (yticks := config.get("yticks")) is not None:
        plt.gca().set_yticks(yticks)

    if yticklabels := config.get("yticklabels"):
        plt.gca().set_yticklabels(yticklabels)

    # Add markers
    if xmarkers := config.get("xmarkers"):
        for xmarker in xmarkers:
            plt.axvline(**xmarker)

    if ymarkers := config.get("ymarkers"):
        for ymarker in ymarkers:
            plt.axvline(**ymarker)

    for i, yarray in enumerate(series):
        plt.plot(
            xarray[i],
            yarray,
            linestyle[i],
            color=color[i],
            alpha=alpha[i],
            label=label[i],
            markersize=markersize[i],
            linewidth=linewidth[i],
        )

    # Show legend
    if legend := config.get("legend"):
        lg_loc = legend[0]
        lg_alpha = legend[1]
        lgnd = plt.legend(loc=lg_loc)
        lgnd.get_frame().set_alpha(lg_alpha)


def plot_timeseries(
    groups: list[_Series],
    settings: _Settings,
    parameters: list[_Settings],
    template_id: str,
) -> None:
    nplots = len(groups)

    plotting_config: _Settings = settings.get("plotting", {})
    config: _Settings = plotting_config.get(template_id, {})

    width: int = config["width"]
    height: list[int] = config["height"]

    figsize = width, height[nplots - 1]

    plt.figure(figsize=figsize)

    if suptitle := config.get("suptitle", None):
        plt.suptitle(suptitle)

    for i, series in enumerate(groups):
        group_config = _PlotConfig(config, parameters[i], len(series))
        plt.subplot(nplots, 1, i + 1)
        _plot_timeseries_item(series, group_config)

    plt.tight_layout()
    plt.show()


def plot_p_values(input_spectrum: _Spectrum, config: _PlotConfig) -> None:
    from goesdl.experimental.fourier import FourierAnalysis

    spectrum = cast(list[FourierAnalysis], input_spectrum)


def _titling(gsetter: Any) -> Any:
    setter = cast(Callable[..., Any], gsetter)

    def _set_title(*args: Any, **kwargs: Any) -> None:
        if not args:
            if "text" in kwargs:
                setter(kwargs.pop("text"), **kwargs)
            elif "label" in kwargs:
                setter(**kwargs)
            else:
                raise ValueError("No title text provided.")
            return
        locs: tuple[Any | None, ...]
        if len(args) == 1:
            locs = (None,)
        elif len(args) == 2:
            locs = ("left", "right")
        elif len(args) == 3:
            locs = ("left", "center", "right")
        else:
            raise ValueError(
                "Invalid title tuple length, expected up to 3 titles."
            )
        for title, loc in zip(args, locs):
            setter(title, loc=cast(Any, loc))

    return _set_title


def plot_periodogram(input_spectrum: _Spectrum, config: _PlotConfig) -> None:
    from goesdl.experimental.fourier import FourierAnalysis

    # _set_title("title", plt.title, config)
    _set_property("title", _titling(plt.title), config)
    _set_property("xlim", plt.xlim, config)
    _set_property("ylim", plt.ylim, config)
    _set_property("xlabel", plt.xlabel, config)
    _set_property("ylabel", plt.ylabel, config)
    _set_property("xticks", plt.gca().set_xticks, config)
    _set_property("yticks", plt.gca().set_yticks, config)
    _set_property("xticklabels", plt.gca().set_xticklabels, config)
    _set_property("yticklabels", plt.gca().set_yticklabels, config)
    _set_property("grid", plt.grid, config)

    _set_property("plot", _plotter(plt.plot), config)

    _set_property("axvline", plt.axvline, config)
    _set_property("axhline", plt.axhline, config)

    _set_property("legend", plt.legend, config)

    spectrum = cast(list[FourierAnalysis], input_spectrum)


def plot_spectrum(
    spectrum: _Spectrum,
    settings: _Settings,
    parameters: _Settings,
    template_id: str,
) -> None:
    plotting_config: _Settings = settings.get("plotting", {})
    current_config: _Settings = plotting_config.get(template_id, {})
    config = _PlotConfig(current_config, parameters, 1)

    which: str = config.get("which")

    nplots = 2 if which == "both" else 1

    width: int = current_config["width"]
    height: list[int] = current_config["height"]

    figsize = width, height[nplots - 1]

    plt.figure(figsize=figsize)

    if suptitle := current_config.get("suptitle", None):
        plt.suptitle(suptitle)

    if which in {"periodogram", "both"}:
        plot_periodogram(spectrum, config)

    if which in {"p_values", "both"}:
        plot_p_values(spectrum, config)

    plt.tight_layout()
    plt.show()
