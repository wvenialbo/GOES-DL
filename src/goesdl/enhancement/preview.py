from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

from .scale import EnhancementScale

DEFAULT_PREVIEW_HEIGHT = 300


class ColormapPlotLayout:

    dpi: int
    figsize: tuple[float, float]
    axes_box: tuple[float, float, float, float]
    cbar_box: tuple[float, float, float, float]

    def __init__(self, figsize: tuple[int, int], dpi: int = 100) -> None:
        # figure size in inches (dpi: dots per inch)
        width, height = (size / dpi for size in figsize)

        self.dpi = dpi
        self.figsize = width, height

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
    measurement: str = "",
    offset: float = 0.0,
    height: int = DEFAULT_PREVIEW_HEIGHT,
    save_path: str | Path = "",
) -> None:
    # Layout definition in pixel size units
    width, height = 486, height
    layout = ColormapPlotLayout((width, height), dpi=100)
    layout.from_margin(
        (32, 12, 134, 24), (222 + height - DEFAULT_PREVIEW_HEIGHT, 12, 53, 24)
    )

    # Scale factor for all measures in points
    pt_scale = 100 / layout.dpi

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

    # Savet the plot if required
    if save_path:
        plt.savefig(save_path, dpi=layout.dpi, bbox_inches=None)

    # Display the plot
    plt.show()
