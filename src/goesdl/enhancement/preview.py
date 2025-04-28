import matplotlib.pyplot as plt
import numpy as np

from .scale import EnhancementScale


def show_colormap(
    scale: EnhancementScale, measurement: str = "", offset: float = 0.0
) -> None:
    # Example data
    vmin, vmax = scale.domain
    data = np.linspace(vmin, vmax, scale.ncolors)[None, :]

    # Color scale map preview plot
    fig, ax = plt.subplots()

    # Plot the example data
    im = ax.imshow(data, aspect="auto", cmap=scale.cmap, norm=scale.cnorm)

    # Create the color bar with the measurement scale
    cbar = fig.colorbar(im, orientation="horizontal")

    cbar.set_ticks(scale.cticks)
    ticklabels = scale.get_ticklabels(offset, int)
    cbar.set_ticklabels(ticklabels)

    # Note: Alternatively `norm=scale.cnorm` can be passed to imshow and
    # `cbar.ax.minorticks_off()` is used to inhibit the minor ticks.

    # Hide the y-axis since it does not make sense
    ax.tick_params(
        axis="y", which="both", left=False, right=False, labelleft=False
    )

    # Set the title, x-axis label and the colorbar caption
    plt.title(f"Enhancement scale: {scale.name}")

    ax.set_xlabel("Color Index", color="black", labelpad=3.0)

    if not measurement:
        measurement = "Measurement"

    cbar.set_label(label=measurement, color="black", weight="normal")

    plt.show()
