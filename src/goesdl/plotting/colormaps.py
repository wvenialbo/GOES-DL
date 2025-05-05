from pathlib import Path

import numpy as np
from matplotlib import pyplot as plt
from matplotlib.cm import ScalarMappable
from matplotlib.colors import Normalize
from matplotlib.spines import Spine

from ..enhancement.clr_utility import clr_utility
from ..enhancement.scale import EnhancementScale
from ..enhancement.shared import ColorValueList, DiscreteColorList
from .helpers import Rect, Size

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

ALL_CHANNELS = {"red", "green", "blue"}

COLOR_INDEX = "Color Index"


def preview_colormap(
    scale: EnhancementScale,
    save_path: str | Path = "",
    measurement: str = "",
    show: bool = True,
) -> None:
    # Referece rectangle
    # - units in pixel per dimension
    rect = Rect(486, 300, 100)
    size = Size(rect.dpi)

    # Create the figure and the enhancement scale plot box
    fig = plt.figure(figsize=rect.figsize, dpi=rect.dpi)

    ax = fig.add_axes(rect.margins(24, 134, 24, 32))

    # Set the figure title
    fig.suptitle(
        f"Enhancement scale: {scale.name}",
        fontsize=size.pt(12.0),
        color="black",
        alpha=1.0,
        y=rect.y_pos(294),
    )

    # Set the plot box ouline style
    for spine in ["top", "bottom", "left", "right"]:
        axes_outline = ax.spines[spine]
        _set_outline(axes_outline, size.pt(0.6))

    # Set the x-axis label
    ax.set_xlabel(
        COLOR_INDEX,
        color="black",
        alpha=1.0,
        fontsize=size.pt(10.0),
        labelpad=size.pt(3.0),
    )

    # Setup the x-axis ticks
    ax.tick_params(
        axis="x",
        color=("black", 1.0),
        width=size.pt(0.6),
        length=size.pt(3.5),
        labelcolor=("black", 1.0),
        labelsize=size.pt(10.0),
        pad=size.pt(4.5),
    )

    # Hide the y-axis ticks since it does not make sense
    ax.tick_params(
        axis="y", which="both", left=False, right=False, labelleft=False
    )

    # Hide the minor ticks
    ax.minorticks_off()

    # Generate example data
    data = np.linspace(0, 1, scale.ncolors, endpoint=True)[None, :]

    # Plot the example data
    im = ax.imshow(data, aspect="auto", cmap=scale.cmap)

    # Create the colour bar box
    cax = fig.add_axes(rect.margins(24, 52, 24, 224))

    # Plot the colour bar box with the measurement scale
    cbar = fig.colorbar(im, orientation="horizontal", cax=cax)

    # Set the colour bar box ouline style
    cbar_outline: Spine = cbar.ax.spines["outline"]
    _set_outline(cbar_outline, size.pt(0.6))

    # Set the colorbar caption
    cbar.set_label(
        label=measurement or "Measurement",
        weight="normal",
        color="black",
        alpha=1.0,
        fontsize=size.pt(10.0),
        labelpad=size.pt(4.0),
    )

    # Create and setup the colour bar ticks
    cbar.ax.tick_params(
        axis="x",
        color=("black", 1.0),
        width=size.pt(0.6),
        length=size.pt(3.5),
        labelcolor=("black", 1.0),
        labelsize=size.pt(10.0),
        pad=size.pt(4.0),
    )

    # Hide the y-axis ticks since it does not make sense
    cbar.ax.tick_params(
        axis="y", which="both", left=False, right=False, labelleft=False
    )

    # Hide the minor ticks
    cbar.ax.minorticks_off()

    # Add the colour bar ticks and labels
    def _to_int_str(x: float) -> str:
        return str(round(x))

    ticker = scale.ticker

    tickmarks = [float(scale.cnorm(v)) for v in ticker.get_ticks()]
    ticklabels = ticker.get_labels(_to_int_str)

    cbar.set_ticks(tickmarks, labels=ticklabels)

    # Save the plot if required
    if save_path:
        plt.savefig(save_path, dpi=rect.dpi, bbox_inches=None)

    # Display the plot
    if show:
        plt.show()
    else:
        plt.close()


def preview_stretching(
    scale: EnhancementScale,
    save_path: str | Path = "",
    measurement: str = "",
    show: bool = True,
) -> None:
    # Referece rectangle
    # - units in pixel per dimension
    rect = Rect(486, 568, 100)
    size = Size(rect.dpi)

    # Create the figure and the enhancement scale plot box
    fig = plt.figure(figsize=rect.figsize, dpi=rect.dpi)

    ax = fig.add_axes(rect.margins(66, 134, 18, 32))

    # Set the figure title
    fig.suptitle(
        f"Stretching scale: {scale.name}",
        fontsize=size.pt(12.0),
        color="black",
        alpha=1.0,
        y=rect.y_pos(557),
    )

    # Set the plot box ouline style
    for spine in ["top", "bottom", "left", "right"]:
        axes_outline = ax.spines[spine]
        _set_outline(axes_outline, size.pt(0.8))

    measurement = measurement or "Measurement"

    # Set the x-axis label
    ax.set_xlabel(
        f"{measurement} (input)",
        color="black",
        alpha=1.0,
        fontsize=size.pt(10.0),
        labelpad=size.pt(4.0),
    )

    # Set the y-axis label
    ax.set_ylabel(
        "Color Index (output)",
        color="black",
        alpha=1.0,
        fontsize=size.pt(10.0),
        labelpad=size.pt(4.0),
    )

    # Setup the x-axis ticks
    ax.tick_params(
        axis="x",
        color=("black", 1.0),
        width=size.pt(0.6),
        length=size.pt(3.5),
        labelcolor=("black", 1.0),
        labelsize=size.pt(10.0),
        pad=size.pt(3.0),
    )

    # Setup the y-axis ticks
    ax.tick_params(
        axis="y",
        color=("black", 1.0),
        width=size.pt(0.6),
        length=size.pt(3.5),
        labelcolor=("black", 1.0),
        labelsize=size.pt(10.0),
        pad=size.pt(3.5),
    )

    # Hide the minor ticks
    ax.minorticks_off()

    # Configure axes limits
    xmin, xmax = scale.stretching.domain
    ymin, ymax = scale.stretching.range
    ax.set_xlim(xmin - 5, xmax + 5)
    ax.set_ylim(ymin - 5, ymax + 5)

    # Number of color brightness levels
    ncolors: int = 256

    # Prepare the plotting data
    x_indices = np.linspace(xmin, xmax, ncolors, endpoint=True)
    y_output = scale.cnorm(x_indices)
    y_indices = (ymax - ymin) * y_output

    # Color the area under the curve using thin bars
    bar_width = (xmax - xmin) / (ncolors - 1)
    pad_offset = -0.3 * bar_width
    for i in range(ncolors):
        ax.bar(
            x_indices[i] + pad_offset,
            y_indices[i],
            width=bar_width,
            color=scale.cmap(y_output[i]),
            align="edge",
        )

    # Plot the stretching curve
    input_indices: tuple[float, ...]
    output_indices: tuple[float, ...]
    input_indices, output_indices = tuple(zip(*scale.stretching.table))

    ax.plot(
        input_indices,
        output_indices,
        color="black",
        alpha=1.0,
        linewidth=size.pt(1.2),
    )

    # Add grid lines
    plt.grid(True, linestyle="--", alpha=0.6, linewidth=size.pt(0.8))

    # Create the colour bar box
    cax = fig.add_axes(rect.margins(74, 52, 25, 492))

    # Createa a mappable colour scale
    cnorm = Normalize(vmin=0, vmax=ncolors - 1)

    smap = ScalarMappable(cmap=scale.cmap, norm=cnorm)

    # Plot the colour bar box with the measurement scale
    cbar = fig.colorbar(smap, orientation="horizontal", cax=cax)

    # Set the colour bar box ouline style
    cbar_outline: Spine = cbar.ax.spines["outline"]
    _set_outline(cbar_outline, size.pt(0.6))

    # Set the colorbar caption
    cbar.set_label(
        label=COLOR_INDEX,
        weight="normal",
        color="black",
        alpha=1.0,
        fontsize=size.pt(10.0),
        labelpad=size.pt(4.0),
    )

    # Create and setup the colour bar ticks
    cticks = list(range(0, ncolors, 50))

    cbar.set_ticks(cticks)

    cbar.ax.tick_params(
        axis="x",
        color=("black", 1.0),
        width=size.pt(0.6),
        length=size.pt(3.5),
        labelcolor=("black", 1.0),
        labelsize=size.pt(10.0),
        pad=size.pt(4.0),
    )

    # Hide the y-axis ticks since it does not make sense
    cbar.ax.tick_params(
        axis="y", which="both", left=False, right=False, labelleft=False
    )

    # Hide the minor ticks
    cbar.ax.minorticks_off()

    # Add labels to the colour bar ticks
    ticklabels = [str(i) for i in cticks]

    cbar.set_ticklabels(ticklabels)

    # Save the plot if required
    if save_path:
        plt.savefig(save_path, dpi=rect.dpi, bbox_inches=None)

    # Display the plot
    if show:
        plt.show()
    else:
        plt.close()


def plot_brightness_profile(
    scale: EnhancementScale,
    save_path: str | Path = "",
    algorithm: str = "rec709",
    show: bool = True,
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
    # Referece rectangle
    # - units in pixel per dimension
    rect = Rect(486, 486, 100)
    size = Size(rect.dpi)

    # Create the figure and plot box
    fig = plt.figure(figsize=rect.figsize, dpi=rect.dpi)

    ax = fig.add_axes(rect.margins(66, 52, 18, 32))

    # Set the figure title
    fig.suptitle(
        "Relative Brightness of Color Scale",
        fontsize=size.pt(12.0),
        color="black",
        alpha=1.0,
        y=rect.y_pos(476),
    )

    # Set the plot box ouline style
    for spine in ["top", "bottom", "left", "right"]:
        axes_outline = ax.spines[spine]
        _set_outline(axes_outline, size.pt(0.8))

    # Set the x-axis label
    ax.set_xlabel(
        f"Index of Enhancement: {scale.name}",
        color="black",
        alpha=1.0,
        fontsize=size.pt(10.0),
        labelpad=size.pt(4.0),
    )

    # Set the y-axis label
    ax.set_ylabel(
        f"Brightness ({LUMA_ALGORITHMS[algorithm]})",
        color="black",
        alpha=1.0,
        fontsize=size.pt(10.0),
        labelpad=size.pt(4.0),
    )

    # Setup the x-axis ticks
    ax.tick_params(
        axis="x",
        color=("black", 1.0),
        width=size.pt(0.6),
        length=size.pt(3.5),
        labelcolor=("black", 1.0),
        labelsize=size.pt(10.0),
        pad=size.pt(3.0),
    )

    # Setup the y-axis ticks
    ax.tick_params(
        axis="y",
        color=("black", 1.0),
        width=size.pt(0.6),
        length=size.pt(3.5),
        labelcolor=("black", 1.0),
        labelsize=size.pt(10.0),
        pad=size.pt(3.5),
    )

    # Hide the minor ticks
    ax.minorticks_off()

    # Number of color brightness levels
    ncolors: int = 256

    # Configure axes limits
    ax.set_xlim(-5, ncolors + 4)
    ax.set_ylim(-5, ncolors + 4)

    # Create color LUT with 256 entries
    colors_lut = _create_colors_lut(scale, ncolors)

    # Calculate the perceived brightness according to a given model
    brightness = _rgb_to_brightness(colors_lut, ncolors, algorithm)

    # Prepare the plotting data
    x_indices = list(range(ncolors))
    y_brightness = brightness

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
    ax.plot(x_indices, y_brightness, color="black", linewidth=size.pt(1.2))

    # Add grid lines
    plt.grid(True, linestyle="--", alpha=0.6, linewidth=size.pt(0.8))

    # Save the plot if required
    if save_path:
        plt.savefig(save_path, dpi=rect.dpi, bbox_inches=None)

    # Display the plot
    if show:
        plt.show()
    else:
        plt.close()


def plot_color_profile(
    scale: EnhancementScale,
    save_path: str | Path = "",
    channels: str | set[str] = "all",
    show: bool = True,
) -> None:
    if isinstance(channels, str):
        channels = ALL_CHANNELS if channels == "all" else {channels}
    elif not channels:
        raise ValueError("'channels' can not be empty")
    if invalid := channels - ALL_CHANNELS:
        allowed_channels = "', '".join(ALL_CHANNELS)
        invalid_channels = "', '".join(invalid)
        raise ValueError(
            f"'channels' contains invalid values: '{invalid_channels}', "
            f"allowed values are: '{allowed_channels}'"
        )

    # Referece rectangle
    # - units in pixel per dimension
    rect = Rect(486, 568, 100)
    size = Size(rect.dpi)

    # Create the figure and the enhancement scale plot box
    fig = plt.figure(figsize=rect.figsize, dpi=rect.dpi)

    ax = fig.add_axes(rect.margins(66, 134, 18, 32))

    # Set the figure title
    fig.suptitle(
        "Color Component Intensities",
        fontsize=size.pt(12.0),
        color="black",
        alpha=1.0,
        y=rect.y_pos(557),
    )

    # Set the plot box ouline style
    for spine in ["top", "bottom", "left", "right"]:
        axes_outline = ax.spines[spine]
        _set_outline(axes_outline, size.pt(0.8))

    # Set the x-axis label
    ax.set_xlabel(
        f"Index of Enhancement: {scale.name}",
        color="black",
        alpha=1.0,
        fontsize=size.pt(10.0),
        labelpad=size.pt(4.0),
    )

    # Set the y-axis label
    ax.set_ylabel(
        "Primary component intensity",
        color="black",
        alpha=1.0,
        fontsize=size.pt(10.0),
        labelpad=size.pt(4.0),
    )

    # Setup the x-axis ticks
    ax.tick_params(
        axis="x",
        color=("black", 1.0),
        width=size.pt(0.6),
        length=size.pt(3.5),
        labelcolor=("black", 1.0),
        labelsize=size.pt(10.0),
        pad=size.pt(3.0),
    )

    # Setup the y-axis ticks
    ax.tick_params(
        axis="y",
        color=("black", 1.0),
        width=size.pt(0.6),
        length=size.pt(3.5),
        labelcolor=("black", 1.0),
        labelsize=size.pt(10.0),
        pad=size.pt(3.5),
    )

    # Hide the minor ticks
    ax.minorticks_off()

    # Number of color brightness levels
    ncolors: int = 256

    # Configure axes limits
    ax.set_xlim(-5, ncolors + 4)
    ax.set_ylim(-5, ncolors + 4)

    # Create color LUT with 256 entries
    colors_lut = _create_colors_lut(scale, ncolors)

    # Extract colour components
    components = map(list, zip(*colors_lut))

    # Compute colour component intensity
    intensities = [
        clr_utility._scale_color_values(component) for component in components
    ]

    # Prepare the plotting data
    x_indices = list(range(ncolors))
    y_intensities = list(reversed(intensities))

    # Plot the colours intensity curves
    for i, color_name in enumerate(["blue", "green", "red"]):
        if color_name not in channels:
            continue
        y_intensity = y_intensities[i]
        ax.plot(
            x_indices,
            y_intensity,
            color=color_name,
            alpha=1.0,
            label=color_name,
            linewidth=size.pt(1.2),
        )

    # Display a legend
    ax.legend()

    # Add grid lines
    plt.grid(True, linestyle="--", alpha=0.6, linewidth=size.pt(0.8))

    # Create the colour bar box
    cax = fig.add_axes(rect.margins(74, 52, 25, 492))

    # Createa a mappable colour scale
    cnorm = Normalize(vmin=0, vmax=ncolors - 1)

    smap = ScalarMappable(cmap=scale.cmap, norm=cnorm)

    # Plot the colour bar box with the measurement scale
    cbar = fig.colorbar(smap, orientation="horizontal", cax=cax)

    # Set the colour bar box ouline style
    cbar_outline: Spine = cbar.ax.spines["outline"]
    _set_outline(cbar_outline, size.pt(0.6))

    # Set the colorbar caption
    cbar.set_label(
        label=COLOR_INDEX,
        weight="normal",
        color="black",
        alpha=1.0,
        fontsize=size.pt(10.0),
        labelpad=size.pt(4.0),
    )

    # Create and setup the colour bar ticks
    cticks = list(range(0, ncolors, 50))

    cbar.set_ticks(cticks)

    cbar.ax.tick_params(
        axis="x",
        color=("black", 1.0),
        width=size.pt(0.6),
        length=size.pt(3.5),
        labelcolor=("black", 1.0),
        labelsize=size.pt(10.0),
        pad=size.pt(4.0),
    )

    # Hide the y-axis ticks since it does not make sense
    cbar.ax.tick_params(
        axis="y", which="both", left=False, right=False, labelleft=False
    )

    # Hide the minor ticks
    cbar.ax.minorticks_off()

    # Add labels to the colour bar ticks
    ticklabels = [str(i) for i in cticks]

    cbar.set_ticklabels(ticklabels)

    # Save the plot if required
    if save_path:
        plt.savefig(save_path, dpi=rect.dpi, bbox_inches=None)

    # Display the plot
    if show:
        plt.show()
    else:
        plt.close()


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


def _set_outline(outline: Spine, linewidth: float) -> None:
    outline.set_linewidth(linewidth)
    outline.set_color("black")
    outline.set_alpha(1.0)
