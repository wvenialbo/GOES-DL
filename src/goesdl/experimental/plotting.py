from collections.abc import Callable
from copy import deepcopy
from math import nan
from typing import Any, cast

from matplotlib import pyplot as plt
from numpy import floating, ndarray
from numpy.typing import NDArray

_Array = NDArray[floating[Any]]
_Series = list[_Array]
_Settings = dict[str, Any]
_NSettings = dict[str, _Settings]
_LSettings = list[_Settings]

_allowed_box_units = ["in", "cm", "mm", "pt", "px"]
_default_box_unit = "in"

_upi = {
    "in": 1.0,
    "cm": 2.54,
    "mm": 25.4,
    "pt": 72.0,
    "px": nan,
}


class Scaler:
    """
    Point an pixel scaler

    Standardize dimensions (like lengths, widths, or spacing) in a
    drawing or visualization system, likely for a plotting library such
    as Matplotlib, so they appear consistent regardless of the current
    figure's dots per inch (DPI).

    The primary goal is to convert dimensions specified in "points" (pt)
    or "pixels" (px) at the default figure's DPI of 100 to an equivalent
    dimension in "points" as if the figure were rendered at a current
    DPI. This ensures that elements like text size, line thickness, and
    spacing maintain their intended visual appearance even when the
    output resolution (DPI) changes.

    Attributes
    ----------
    default_dpi: float
        This is the reference DPI. The class aims to convert all
        dimensions to be equivalent to what they would be at this DPI.
    points_per_inch: float
        This is a standard conversion factor, indicating that there are
        72 points in one inch.
    pt_to_pt_scale: float
        This variable stores the scaling factor for converting "points"
        from the current DPI to "points" at the `default_dpi`.
    px_to_pt_scale: float
        This variable stores the scaling factor for converting "pixels"
        from the current DPI to "points" at the `default_dpi`.
    """

    default_dpi: float = 100
    points_per_inch: float = 72

    pt_to_pt_scale: float
    px_to_pt_scale: float

    def __init__(self, dpi: int) -> None:
        self.pt_to_pt_scale = self.default_dpi / dpi
        self.px_to_pt_scale = self.default_dpi * self.points_per_inch / dpi**2

    def pt(self, x: float) -> float:
        """
        Convert a size specified in points in DPI of 100.

        This method takes a value x which is assumed to be in "points"
        at the default figure's DPI of 100 and converts it to a value
        that is the equivalent in "points" in the current figure's DPI.
        """
        return x * self.pt_to_pt_scale

    def px(self, x: float) -> float:
        """
        Convert a size specified in pixels in a DPI of 100.

        This method takes a value x which is assumed to be in "pixels"
        at the default figure's DPI of 100 and converts it to a value
        that is the equivalent in "points" in the current figure's DPI.
        """
        return x * self.px_to_pt_scale


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


def get_template(settings: _Settings, template_id: str) -> _Settings:
    plotting_config: _Settings = settings.get("plotting", {})
    template: _Settings = plotting_config.get(template_id, {})
    return deepcopy(template)


def render_template(
    specs: _Settings, save_path: str = "", show: bool = True
) -> None:
    from matplotlib import pyplot as plt

    # Setup figure
    _figure_artist(specs)

    # Get subplots information
    subplots_: _LSettings | _NSettings = specs.get("subplots", [])

    if isinstance(subplots_, dict):
        subplots = list(subplots_.values())
    else:
        subplots = subplots_

    if len(subplots) == 0:
        raise ValueError(
            "No subplots defined. At least one subplot must be provided."
        )

    nrows: int = specs.get("nrows", 1)
    ncols: int = specs.get("ncols", 1)

    # Process each subplot
    for i, subplot in enumerate(subplots):
        plt.subplot(nrows, ncols, i + 1)
        _subplot_artist(subplot or {})

    # Terminate plotting
    _set_property("tight_layout", plt.tight_layout, specs)

    # Save the media file
    if save_path:
        savefig_args = specs.get("savefig", {})
        plt.savefig(save_path, **savefig_args)

    # Show the plot
    if show:
        show_args = specs.get("show", {})
        plt.show(**show_args)
    else:
        close_args = specs.get("close", {})
        plt.close(**close_args)


def _figure_artist(specs: _Settings) -> None:
    from matplotlib import pyplot as plt

    box_unit: str = specs.get("box_unit", _default_box_unit)

    if box_unit not in _allowed_box_units:
        raise ValueError(
            f"Invalid 'box_unit' specified: '{box_unit}'. Valid units "
            f"are {', '.join(_allowed_box_units)}."
        )

    _width: float | None = specs.get("width", None)
    _height: float | None = specs.get("height", None)

    if _width is None and _height is None:
        _width = 6.4
        _height = 4.8
        box_unit = _default_box_unit
    elif _width is None or _height is None:
        raise ValueError(
            "Both 'width' and 'height' must be provided "
            "or both must be 'None'."
        )

    dpi: int = specs.get("dpi", 100)
    _upi["px"] = dpi

    width = _width / _upi[box_unit]
    height = _height / _upi[box_unit]

    figsize = width, height

    plt.figure(figsize=figsize, dpi=dpi)

    _set_property("title", plt.suptitle, specs)


def _subplot_artist(specs: _Settings) -> None:
    from matplotlib import pyplot as plt

    _set_property("title", _title(plt.title), specs)

    _set_property("xlim", plt.xlim, specs)
    _set_property("ylim", plt.ylim, specs)

    _set_property("xscale", plt.xscale, specs)
    _set_property("yscale", plt.yscale, specs)

    _set_property("xlabel", plt.xlabel, specs)
    _set_property("ylabel", plt.ylabel, specs)

    _set_property("xticks", plt.gca().set_xticks, specs)
    _set_property("yticks", plt.gca().set_yticks, specs)

    _set_property("xticklabels", plt.gca().set_xticklabels, specs)
    _set_property("yticklabels", plt.gca().set_yticklabels, specs)

    _set_property("grid", plt.grid, specs)

    _set_property("plot", _plot(plt.plot), specs)

    _set_property("axvline", plt.axvline, specs)
    _set_property("axhline", plt.axhline, specs)

    _set_property("fill_between", plt.fill_between, specs)

    _set_property("text", _text(plt.text), specs)

    _set_property("legend", _legend(plt.legend), specs)


def _legend(gsetter: Any) -> Any:
    from matplotlib.legend import Legend

    setter = cast(Callable[..., Any], gsetter)

    def _set_legend(
        show: bool = True, alpha: float | None = None, **kwargs: Any
    ) -> None:
        if not show:
            return

        legend: Legend = setter(**kwargs)

        if alpha is not None:
            legend.get_frame().set_alpha(alpha)

    return _set_legend


def _plot(gsetter: Any) -> Any:
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


def _text(gsetter: Any) -> Any:
    from matplotlib.text import Text

    setter = cast(Callable[..., Any], gsetter)

    def _set_text(**kwargs: Any) -> None:
        ax = plt.gca()

        text_artist: Text = setter(**kwargs)

        ax.figure.canvas.draw()

        bbox_display = text_artist.get_window_extent(
            renderer=ax.figure.canvas.renderer  # type: ignore
        )
        bbox_data = bbox_display.transformed(ax.transData.inverted())

        x_bbox_min = bbox_data.x0
        y_bbox_min = bbox_data.y0
        x_bbox_max = bbox_data.x1
        y_bbox_max = bbox_data.y1

        x_min_data, x_max_data = ax.get_xlim()
        y_min_data, y_max_data = ax.get_ylim()

        if (
            x_bbox_min < x_min_data
            or x_bbox_max > x_max_data
            or y_bbox_min < y_min_data
            or y_bbox_max > y_max_data
        ):
            text_artist.remove()

    return _set_text


def _title(gsetter: Any) -> Any:
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


def _kwarg(value: Any) -> dict[str, Any]:
    return cast(dict[str, Any], value)


def _lsarg(value: Any) -> list[Any]:
    return cast(list[dict[str, Any]], value)


def _tparg(value: Any) -> tuple[Any, ...]:
    return cast(tuple[Any, ...], value)


def _set_property(name: str, gsetter: Any, specs: _Settings) -> None:
    if (value := specs.get(name, None)) is not None:
        _set_value(gsetter, value)


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
