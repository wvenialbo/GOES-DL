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


class ColormapPreviewLayout:

    dpi: int
    figsize: tuple[float, float]
    axes_box: tuple[float, float, float, float]
    cbar_box: tuple[float, float, float, float]

    def __init__(self, figsize: tuple[int, int], dpi: int = 100) -> None:
        # figsize: figure size (width, height) in dot (pixels) units
        # dpi: dots per inch

        # figure size in inches (dpi: dots per inch)
        width, height = (size / dpi for size in figsize)

        self.dpi = dpi
        self.figsize = width, height

        self.from_margin((32, 12, 134, 24), (222, 12, 53, 24))

    def from_box(
        self,
        abox: tuple[int, int, int, int],
        cbox: tuple[int, int, int, int],
    ) -> None:
        # plot and colour bar boxes position and dimensions in inches
        aleft, abottom, awidth, aheight = (size / self.dpi for size in abox)
        cleft, cbottom, cwidth, cheight = (size / self.dpi for size in cbox)

        # figure size in inches
        width, height = self.figsize

        # plot box position and dimensions in relative units
        abottom, aheight = (size / height for size in (abottom, aheight))
        aleft, awidth = (size / width for size in (aleft, awidth))
        self.axes_box = aleft, abottom, awidth, aheight

        # colour bar box position and dimensions in relative units
        cbottom, cheight = (size / height for size in (cbottom, cheight))
        cleft, cwidth = (size / width for size in (cleft, cwidth))
        self.cbar_box = cleft, cbottom, cwidth, cheight

    def from_margin(
        self,
        amargins: tuple[int, int, int, int],
        cmargins: tuple[int, int, int, int],
    ) -> None:
        # plot and colour bar boxes margins in inches
        atop, aright, abottom, aleft = (size / self.dpi for size in amargins)
        ctop, cright, cbottom, cleft = (size / self.dpi for size in cmargins)

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

        # colour bar box margins in relative units
        ctop, cbottom = (size / height for size in (ctop, cbottom))
        cright, cleft = (size / width for size in (cright, cleft))

        # colour bar box position and dimensions in relative units
        cbox_px = cleft
        cbox_py = cbottom
        cbox_cx = 1.0 - cright - cleft
        cbox_cy = 1.0 - ctop - cbottom

        self.cbar_box = cbox_px, cbox_py, cbox_cx, cbox_cy


def preview_colormap(
    scale: EnhancementScale,
    save_path: str | Path = "",
    measurement: str = "",
    offset: float = 0.0,
) -> None:
    # Layout definition in pixel size units
    layout = ColormapPreviewLayout(figsize=(486, 300), dpi=100)

    # Scale factor for all measures in points
    pt_scale = REF_DPI / layout.dpi

    # Example data
    vmin, vmax = scale.domain
    data = np.linspace(vmin, vmax, scale.ncolors)[None, :]

    # Create the figure and the enhancement scale plot box
    fig = plt.figure(figsize=layout.figsize, dpi=layout.dpi)

    ax = fig.add_axes(layout.axes_box)

    # Plot the example data
    im = ax.imshow(data, aspect="auto", cmap=scale.cmap, norm=scale.cnorm)

    # Set the plot title
    ax.set_title(
        f"Enhancement scale: {scale.name}",
        fontsize=12 * pt_scale,
        pad=6 * pt_scale,
    )

    # Set the plot box ouline format
    for spine in ["top", "bottom", "left", "right"]:
        ax.spines[spine].set_linewidth(0.6 * pt_scale)

    # Setup the x-axis ticks
    ax.tick_params(
        axis="x",
        labelsize=10 * pt_scale,
        width=0.6 * pt_scale,
        length=3.5 * pt_scale,
        pad=4.5 * pt_scale,
    )

    # Hide the y-axis ticks since it does not make sense
    ax.tick_params(
        axis="y", which="both", left=False, right=False, labelleft=False
    )

    # Set the x-axis label
    ax.set_xlabel(
        "Color Index",
        color="black",
        labelpad=3 * pt_scale,
        fontsize=10 * pt_scale,
    )

    # Create the colour bar box
    cax = fig.add_axes(layout.cbar_box)

    # Plot the colour bar box with the measurement scale
    cbar = fig.colorbar(im, orientation="horizontal", cax=cax)

    # Set the colour bar box ouline format
    cbar.outline.set_linewidth(0.6 * pt_scale)  # type: ignore

    # Set the colorbar caption
    cbar.set_label(
        label=measurement or "Measurement",
        color="black",
        weight="normal",
        fontsize=10 * pt_scale,
        labelpad=4 * pt_scale,
    )

    # Create and setup the colour bar ticks
    cbar.set_ticks(scale.cticks)

    cax.tick_params(
        axis="x",
        labelsize=10 * pt_scale,
        width=0.6 * pt_scale,
        length=3.5 * pt_scale,
        pad=4 * pt_scale,
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


def create_colors_lut(
    scale: EnhancementScale, ncolors: int
) -> DiscreteColorList:
    colors_lut: DiscreteColorList = []
    colors_map = scale.cmap

    for i in range(ncolors):
        rgb_value = colors_map(i / ncolors)[:3]
        colors_lut.append(rgb_value)

    return colors_lut


def rgb_to_brightness(
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
    # Number of color brightness levels
    ncolors: int = 256

    # Create color LUT with 256 entries
    colors_lut = create_colors_lut(scale, ncolors)

    # Calculate the perceived brightness according to a given model
    brightness = rgb_to_brightness(colors_lut, ncolors, algorithm)

    # Prepare the plotting data
    x_indices = list(range(ncolors))
    y_brightness = brightness

    # Create and color the plot
    fig, ax = plt.subplots(figsize=(6, 6))

    # Plot the perceived brightness curve
    ax.plot(x_indices, y_brightness, color="black", linewidth=1.5)

    # Color the area under the curve using thin bars
    bar_width = 1.0
    pad_offset = -0.6
    for i in x_indices:
        # Draw a bar from y=0 up to the calculated brightness, with the LUT color
        ax.bar(
            x_indices[i] + pad_offset,
            y_brightness[i],
            width=bar_width,
            color=colors_lut[i],
            align="edge",
        )

    # Configure axis limits
    ax.set_xlim(0, ncolors - 1)
    ax.set_ylim(0, ncolors - 1)

    # Optional: Improve plot appearance
    plt.grid(True, linestyle="--", alpha=0.6)

    # Configure labels and title
    ax.set_xlabel(f"Index of Enhancement: {scale.name}")
    ax.set_ylabel(f"Brightness ({LUMA_ALGORITHMS[algorithm]})")
    ax.set_title("Relative Brightness of Color Bars")

    # Save the plot if required
    if save_path:
        plt.savefig(save_path, dpi=100, bbox_inches=None)

    # Adjust layout to prevent overlaps
    plt.tight_layout()

    # Display the plot
    plt.show()
