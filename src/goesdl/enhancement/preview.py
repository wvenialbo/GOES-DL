from pathlib import Path

import numpy as np
from matplotlib import pyplot as plt

from .scale import EnhancementScale
from .shared import ColorValueList, DiscreteColorList

REF_DPI = 100

LUMA_COEFFICIENTS = {
    "rec240": (0.212, 0.701, 0.087),  # Adobe
    "rec601": (0.299, 0.587, 0.114),  # Standard for SDTV (NTSC, PAL)
    "rec709": (0.2126, 0.7152, 0.0722),  # Recommended for sRGB/HDTV
    "rec2020": (0.2627, 0.6780, 0.0593),  # Standard for UHDTV/HDR
    "average": (1 / 3, 1 / 3, 1 / 3),
    # You can add other models here if needed
}

LUMA_ALGORITHMS = {
    "rec240": "Rec. 240",  # Adobe
    "rec601": "Rec. 601",  # Standard for SDTV (NTSC, PAL)
    "rec709": "Rec. 709",  # Recommended for sRGB/HDTV
    "rec2020": "Rec. 2020",  # Standard for UHDTV/HDR
    "average": "average",
    # You can add other models here if needed
}


class LabelStyle:

    fontsize: float
    pad: float
    color: str

    pt_scale: float

    def __init__(self, pt_scale: float) -> None:
        self.pt_scale = pt_scale
        self.fontsize = 10.0 * pt_scale
        self.pad = 4.0 * pt_scale
        self.color = "black"

    def style(
        self,
        fontsize: float = 10.0,
        labelpad: float = 4.0,
        color: str = "black",
    ) -> None:
        self.fontsize = fontsize * self.pt_scale
        self.pad = labelpad * self.pt_scale
        self.color = color


class TickStyle:

    label: LabelStyle

    width: float
    length: float
    color: str

    pt_scale: float

    def __init__(self, pt_scale: float) -> None:
        self.pt_scale = pt_scale

        self.width = 0.6 * pt_scale
        self.length = 3.5 * pt_scale
        self.color = "black"

        self.label = LabelStyle(pt_scale)

    def style(
        self,
        width: float = 0.6,
        length: float = 3.5,
        color: str = "black",
    ) -> None:
        self.width = width * self.pt_scale
        self.length = length * self.pt_scale
        self.color = color


class AxesTickStyle:

    x: TickStyle
    y: TickStyle

    def __init__(self, pt_scale: float) -> None:
        self.x = TickStyle(pt_scale)
        self.y = TickStyle(pt_scale)


class AxesLabelStyle:

    x: LabelStyle
    y: LabelStyle

    def __init__(self, pt_scale: float) -> None:
        self.x = LabelStyle(pt_scale)
        self.y = LabelStyle(pt_scale)


class OutlineStyle:

    width: float
    color: str

    pt_scale: float

    def __init__(self, pt_scale: float) -> None:
        self.pt_scale = pt_scale
        self.width = 0.6 * pt_scale
        self.color = "black"

    def style(self, linewidth: float = 0.6, color: str = "black") -> None:
        self.outline_linewidth = linewidth * self.pt_scale
        self.color = color


class PlotStyle:

    dpi: int

    figsize: tuple[float, float]

    box: tuple[float, float, float, float]

    outline: OutlineStyle

    title: LabelStyle

    label: AxesLabelStyle

    tick: AxesTickStyle

    def __init__(self, figsize: tuple[float, float], dpi: int) -> None:
        self.dpi = dpi
        self.figsize = figsize

        pt_scale = REF_DPI / dpi

        self.box = self._get_box((32, 24, 52, 24))

        self.outline = OutlineStyle(pt_scale)

        self.title = LabelStyle(pt_scale)
        self.title.style(12.0, 6.0)

        self.label = AxesLabelStyle(pt_scale)

        self.tick = AxesTickStyle(pt_scale)

    def margins(
        self, top: int = 32, right: int = 24, bottom: int = 52, left: int = 24
    ) -> None:
        self.box = self._get_box((top, right, bottom, left))

    def _get_box(
        self, margins: tuple[int, int, int, int]
    ) -> tuple[float, float, float, float]:
        # figure dimensions in inches
        width, height = self.figsize

        # box margins in inches
        top, right, bottom, left = (size / self.dpi for size in margins)

        # box margins in relative units
        top, bottom = (size / height for size in (top, bottom))
        right, left = (size / width for size in (right, left))

        # box position and dimensions in relative units
        box_px = left
        box_py = bottom
        box_cx = 1.0 - right - left
        box_cy = 1.0 - top - bottom

        return box_px, box_py, box_cx, box_cy


class TitleStyle:

    fontsize: float
    baseline: float
    color: str

    pt_scale: float

    def __init__(self, dpi: int) -> None:
        self.pt_scale = REF_DPI / dpi
        self.fontsize = 12.0 * self.pt_scale
        self.baseline = 0.0
        self.color = "black"

    def style(
        self,
        fontsize: float = 12.0,
        baseline: float = 0.0,
        color: str = "black",
    ) -> None:
        self.fontsize = fontsize * self.pt_scale
        self.baseline = baseline
        self.color = color

    @property
    def position(self) -> float:
        return 0.98 + self.baseline


class FigureLayout:

    dpi: int

    figsize: tuple[float, float]

    title: TitleStyle

    def __init__(
        self, width: int = 486, height: int = 300, dpi: int = REF_DPI
    ) -> None:
        width_in, height_in = (size / dpi for size in (width, height))

        self.dpi = dpi

        self.figsize = width_in, height_in

        self.title = TitleStyle(dpi)


class ColormapPreviewLayout(FigureLayout):

    axes: PlotStyle
    cbar: PlotStyle

    def __init__(
        self, width: int = 486, height: int = 300, dpi: int = REF_DPI
    ) -> None:
        super().__init__(width, height, dpi)

        self.axes = PlotStyle(self.figsize, self.dpi)

        self.cbar = PlotStyle(self.figsize, self.dpi)


def preview_colormap(
    scale: EnhancementScale,
    save_path: str | Path = "",
    measurement: str = "",
    offset: float = 0.0,
) -> None:
    # Plot layout and style definition
    # - figsize and margins in pixel size units
    # - font size and strokes width and length in points
    layout = ColormapPreviewLayout(486, 300, 100)

    layout.title.style(12.0, 0.0)

    layout.axes.margins(32, 24, 134, 24)
    layout.axes.outline.style(0.6)
    layout.axes.label.x.style(10.0, 3.0)
    layout.axes.tick.x.style(0.6, 3.5)
    layout.axes.tick.x.label.style(10.0, 4.5)

    layout.cbar.margins(224, 24, 52, 24)
    layout.cbar.outline.style(0.6)
    layout.cbar.label.x.style(10.0, 4.0)
    layout.cbar.tick.x.style(0.6, 3.5)
    layout.cbar.tick.x.label.style(10.0, 4.0)

    # Example data
    vmin, vmax = scale.domain
    data = np.linspace(vmin, vmax, scale.ncolors)[None, :]

    # Create the figure and the enhancement scale plot box
    fig = plt.figure(figsize=layout.figsize, dpi=layout.dpi)

    ax = fig.add_axes(layout.axes.box)

    # Plot the example data
    im = ax.imshow(data, aspect="auto", cmap=scale.cmap, norm=scale.cnorm)

    # Set the figure title
    fig.suptitle(
        f"Enhancement scale: {scale.name}",
        fontsize=layout.title.fontsize,
        color=layout.title.color,
        y=layout.title.position,
    )

    # Set the plot box ouline format
    for spine in ["top", "bottom", "left", "right"]:
        ax.spines[spine].set_linewidth(layout.axes.outline.width)
        ax.spines[spine].set_color(layout.axes.outline.color)

    # Set the x-axis label
    ax.set_xlabel(
        "Color Index",
        color=layout.axes.label.x.color,
        fontsize=layout.axes.label.x.fontsize,
        labelpad=layout.axes.label.x.pad,
    )

    # Setup the x-axis ticks
    ax.tick_params(
        axis="x",
        color=layout.axes.tick.x.color,
        width=layout.axes.tick.x.width,
        length=layout.axes.tick.x.length,
        labelcolor=layout.axes.tick.x.label.color,
        labelsize=layout.axes.tick.x.label.fontsize,
        pad=layout.axes.tick.x.label.pad,
    )

    # Hide the y-axis ticks since it does not make sense
    ax.tick_params(
        axis="y", which="both", left=False, right=False, labelleft=False
    )

    # Create the colour bar box
    cax = fig.add_axes(layout.cbar.box)

    # Plot the colour bar box with the measurement scale
    cbar = fig.colorbar(im, orientation="horizontal", cax=cax)

    # Set the colour bar box ouline format
    cbar_outline = cbar.ax.spines["outline"]
    cbar_outline.set_linewidth(layout.cbar.outline.width)
    cbar_outline.set_color(layout.cbar.outline.color)

    # Set the colorbar caption
    cbar.set_label(
        label=measurement or "Measurement",
        weight="normal",
        color=layout.cbar.label.x.color,
        fontsize=layout.cbar.label.x.fontsize,
        labelpad=layout.cbar.label.x.pad,
    )

    # Create and setup the colour bar ticks
    cbar.set_ticks(scale.cticks)

    cax.tick_params(
        axis="x",
        color=layout.cbar.tick.x.color,
        width=layout.cbar.tick.x.width,
        length=layout.cbar.tick.x.length,
        labelcolor=layout.cbar.tick.x.label.color,
        labelsize=layout.cbar.tick.x.label.fontsize,
        pad=layout.cbar.tick.x.label.pad,
    )

    cbar.ax.minorticks_off()

    # Add labels to the colour bar ticks
    ticklabels = scale.get_ticklabels(offset, int)

    cbar.set_ticklabels(ticklabels)

    # Save the plot if required
    if save_path:
        plt.savefig(save_path, dpi=layout.dpi, bbox_inches=None)

    # Display the plot
    plt.show()


class BrightnessProfileLayout(FigureLayout):

    grid_linewidth: float = 0.8

    plot_linewidth: float = 1.2

    axis_tick_width: float = 0.6
    axis_tick_length: float = 3.5
    axis_tick_fontsize: float = 10.0
    axis_x_tick_labelpad: float = 3.0
    axis_y_tick_labelpad: float = 3.5

    def __init__(self, figsize: tuple[int, int], dpi: int) -> None:
        # figsize: figure size (width, height) in dot (pixels) units
        # dpi: dots per inch

        # figure size in inches (dpi: dots per inch)
        width, height = (size / dpi for size in figsize)

        self.dpi = dpi
        self.figsize = width, height
        self.pt_scale = REF_DPI / dpi

        self._init_boxes((32, 18, 52, 66))  # (32, 13, 53, 66)

        self._init_sizes()

    def _init_boxes(
        self,
        amargins: tuple[int, int, int, int],
    ) -> None:
        # plot and colour bar boxes margins in inches
        atop, aright, abottom, aleft = (size / self.dpi for size in amargins)

        # figure size in inches
        width, height = self.figsize

        # plot box margins in relative units
        atop, abottom = (size / height for size in (atop, abottom))
        aright, aleft = (size / width for size in (aright, aleft))

        # plot box position and dimensions in relative units
        abox_px = aleft
        abox_py = abottom
        abox_cx = 1.0 - aright - aleft
        abox_cy = 1.0 - atop - abottom

        self.axes_box = abox_px, abox_py, abox_cx, abox_cy

    def _init_sizes(self) -> None:
        # Scale factor for all measures in points
        pt_scale = self.pt_scale

        self.plot_linewidth = 1.2 * pt_scale

        self.title_fontsize = 12.0 * pt_scale
        self.title_labelpad = 6 * pt_scale

        self.axis_outline_linewidth = 0.8 * pt_scale

        self.axis_label_fontsize = 10.0 * pt_scale
        self.axis_label_labelpad = 4.0 * pt_scale

        self.axis_tick_width = 0.6 * pt_scale
        self.axis_tick_length = 3.5 * pt_scale
        self.axis_tick_fontsize = 10.0 * pt_scale
        self.axis_x_tick_labelpad = 3.0 * pt_scale
        self.axis_y_tick_labelpad = 3.5 * pt_scale

        self.grid_linewidth = 0.8 * pt_scale


def plot_brightness_profile(
    scale: EnhancementScale,
    save_path: str | Path = "",
    algorithm: str = "rec709",
) -> None:
    """
    Creates a graphical representation of the perceived brightness (Rec. 709) profile of a color LUT.

    This function visualizes a 256-entry color lookup table (LUT) by plotting
    the perceived brightness (calculated using the Rec. 709 luminance formula)
    for each color in the LUT against its index (0-255). The area beneath the
    resulting curve is shaded with the corresponding color from the LUT for
    each index, providing a direct visual representation of how perceived
    brightness changes across the palette.

    Args:
        lut_colors (np.ndarray or list): A structure (preferably a NumPy array
                                         of shape (256, 3)) containing the 256
                                         color entries of the LUT. Each entry is
                                         expected to be an RGB color with values
                                         typically in the range [0, 255].
        title (str, optional): The title to display on the plot.
                                 Defaults to "Relative Brightness of Color Bars".
        xlabel (str, optional): The label for the X-axis of the plot.
                                Defaults to "Index of Enhancement".
        ylabel (str, optional): The label for the Y-axis of the plot.
                                Defaults to "Brightness (Rec. 709)".
        show_plot (bool, optional): If True, calls `plt.show()` to display
                                     the plot immediately after creation.
                                     Defaults to True.

    Returns:
        tuple: A tuple containing (fig, ax), which are the Matplotlib
               Figure and Axes objects respectively, allowing further
               external customization of the plot.

    Raises:
        ValueError: If `lut_colors` does not contain exactly 256 entries.

    Notes:
        - The Rec. 709 brightness formula used is 0.2126*R + 0.7152*G + 0.0722*B,
          applied to R, G, B values normalized to the range [0, 1].
        - Assumes that input values in `lut_colors` are in the range [0, 255].
          They are normalized internally for brightness calculation.
        - The Y-axis (Brightness) is scaled to the range [0, 255] to match
          the typical range of 8-bit pixel values.

    Example:
        >>> # Example of creating a test LUT (grayscale ramp)
        >>> test_lut_gray = np.zeros((256, 3), dtype=np.uint8)
        >>> for i in range(256):
        ...     test_lut_gray[i, :] = i # Grayscale ramp from 0 to 255
        >>>
        >>> # Plot the brightness profile of the test LUT
        >>> fig, ax = plot_lut_brightness_profile(test_lut_gray, title="Grayscale Ramp Brightness Profile")
        >>> # If show_plot=False, you can add more elements here before plt.show()
        >>> # plt.show()

        >>> # Example with a color LUT loaded from a file (pseudocode)
        >>> # lut_data = load_my_lut_file('my_palette.lut') # Assumes it loads a (256, 3) array
        >>> # fig, ax = plot_lut_brightness_profile(lut_data, title="My Palette Brightness Profile", show_plot=False)
        >>> # ax.grid(True) # Add a grid
        >>> # plt.show()
    """
    # Layout definition in pixel size units
    layout = BrightnessProfileLayout(figsize=(486, 486), dpi=100)

    # Number of color brightness levels
    ncolors: int = 256

    # Create color LUT with 256 entries
    colors_lut = _create_colors_lut(scale, ncolors)

    # Calculate the perceived brightness according to a given model
    brightness = _rgb_to_brightness(colors_lut, ncolors, algorithm)

    # Prepare the plotting data
    x_indices = list(range(ncolors))
    y_brightness = brightness

    # Create the figure and plot box
    fig = plt.figure(figsize=layout.figsize, dpi=layout.dpi)

    ax = fig.add_axes(layout.axes_box)

    # Set the plot title
    ax.set_title(
        "Relative Brightness of Color Bars",
        fontsize=layout.title_fontsize,
        pad=layout.title_labelpad,
    )

    # Set the plot box ouline format
    for spine in ["top", "bottom", "left", "right"]:
        ax.spines[spine].set_linewidth(layout.axis_outline_linewidth)

    # Color the area under the curve using thin bars
    bar_width = 1.0
    pad_offset = -0.3
    for i in x_indices:
        # Draw a bar from y=0 up to the calculated brightness, with the LUT color
        ax.bar(
            x_indices[i] + pad_offset,
            y_brightness[i],
            width=bar_width,
            color=colors_lut[i],
            align="edge",
        )

    # Plot the perceived brightness curve
    ax.plot(
        x_indices, y_brightness, color="black", linewidth=layout.plot_linewidth
    )

    # Configure axes limits
    ax.set_xlim(0, ncolors - 1)
    ax.set_ylim(0, ncolors - 1)

    # Set the axes labels
    ax.set_xlabel(
        f"Index of Enhancement: {scale.name}",
        color="black",
        fontsize=layout.axis_label_fontsize,
        labelpad=layout.axis_label_labelpad,
    )

    ax.set_ylabel(
        f"Brightness ({LUMA_ALGORITHMS[algorithm]})",
        color="black",
        fontsize=layout.axis_label_fontsize,
        labelpad=layout.axis_label_labelpad,
    )

    # Setup the axes ticks
    ax.tick_params(
        axis="x",
        width=layout.axis_tick_width,
        length=layout.axis_tick_length,
        labelsize=layout.axis_tick_fontsize,
        pad=layout.axis_x_tick_labelpad,
    )

    ax.tick_params(
        axis="y",
        width=layout.axis_tick_width,
        length=layout.axis_tick_length,
        labelsize=layout.axis_tick_fontsize,
        pad=layout.axis_y_tick_labelpad,
    )

    # Optional: Improve plot appearance
    plt.grid(True, linestyle="--", alpha=0.6, linewidth=layout.grid_linewidth)

    # Save the plot if required
    if save_path:
        plt.savefig(save_path, dpi=layout.dpi, bbox_inches=None)

    # Display the plot
    plt.show()


def _create_colors_lut(
    scale: EnhancementScale, ncolors: int
) -> DiscreteColorList:
    colors_lut: DiscreteColorList = []
    colors_map = scale.cmap

    for i in range(ncolors):
        rgb_value = colors_map(i / ncolors)[:3]
        colors_lut.append(rgb_value)

    return colors_lut


def _rgb_to_brightness(
    colors_lut: DiscreteColorList, brightness_max: int, algorithm: str
) -> ColorValueList:
    """
    Convert RGB components to grayscale value.

    Calculates the perceived brightness (Luminance/Luma) of an RGB color
    using the Rec. 601/709/2020 formulae.

    Parameters
    ----------
    colors_lut : DiscreteColorList
        Colour look-up table
    algorithm : str
        Name of the conversion algorithm

    Returns
    -------
    float
        The perceived brightness (Luminance/Luma) value in the range [0,
        1].
    """
    try:
        r_weight, g_weight, b_weight = LUMA_COEFFICIENTS[algorithm]
    except KeyError as error:
        valid_algorithms = ", ".join(LUMA_COEFFICIENTS.keys())
        raise ValueError(
            f"Invalid conversion algorithm '{algorithm}'. "
            f"Supported algorithms: {valid_algorithms}"
        ) from error

    brightness: ColorValueList = []

    def rgb_to_grayscale(r: float, g: float, b: float) -> float:
        return r_weight * r + g_weight * g + b_weight * b

    for rgb_value in colors_lut:
        gray_value = rgb_to_grayscale(*rgb_value)
        brightness.append(gray_value * brightness_max)

    return brightness
