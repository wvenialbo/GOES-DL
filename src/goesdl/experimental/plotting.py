from typing import Any, Literal, cast

from matplotlib import pyplot as plt
from numpy import floating
from numpy.typing import NDArray

_Array = NDArray[floating[Any]]
_Series = list[_Array]
_Settings = dict[str, Any]
_Loc = Literal["left", "center", "right"] | None
_Title = tuple[str, _Loc]


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


def plot_timeseries_item(series: _Series, config: _PlotConfig) -> None:
    xarray: list[_Array] = config["xarray"]
    label: list[str] = config["label"]
    markersize: list[float] = config["markersize"]
    alpha: list[float] = config["alpha"]
    linewidth: list[float] = config["linewidth"]
    linestyle: list[str] = config["linestyle"]
    color: list[str] = config["color"]
    xlim: tuple[float, float] = config.get("xlim")

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

    plt.xlim(*xlim)

    # Set titles
    titles = config.get("title", True)

    for title, loc in titles:
        plt.title(title, loc=loc)

    # Set axis labels
    if xlabel := config.get("xlabel"):
        plt.xlabel(xlabel)

    if ylabel := config.get("ylabel"):
        plt.ylabel(ylabel)

    # Show legend
    if legend := config.get("legend"):
        lgnd_alpha = legend[0]
        lgnd = plt.legend()
        lgnd.get_frame().set_alpha(lgnd_alpha)

    # Show grid
    if grid := config.get("grid"):
        visible, which, axis = grid
        plt.grid(visible, which, axis)


def plot_timeseries(
    groups: list[_Series],
    settings: _Settings,
    parameters: list[_Settings],
    plot_id: str,
) -> None:
    nplots = len(groups)

    plotting_config: _Settings = settings["plotting"]
    config: _Settings = plotting_config[plot_id]

    width: int = config["width"]
    height: list[int] = config["height"]

    figsize = width, height[nplots - 1]

    plt.figure(figsize=figsize)

    if suptitle := config["suptitle"]:
        plt.suptitle(suptitle)

    for i, series in enumerate(groups):
        group_config = _PlotConfig(config, parameters[i], len(series))
        plt.subplot(nplots, 1, i + 1)
        plot_timeseries_item(series, group_config)

    plt.tight_layout()
    plt.show()
