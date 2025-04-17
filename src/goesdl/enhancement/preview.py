import matplotlib.pyplot as plt
import numpy as np

from .scale import EnhancementScale
from .ticks import ColorbarTicks


def show_colormap(
    scale: EnhancementScale,
    measurement: str = "",
    offset: float = 0.0,
    nticks: int = 14,
) -> None:
    # Example data
    vmin, vmax = scale.domain
    vmin, vmax = vmin + offset, vmax + offset
    data = np.linspace(vmin, vmax, scale.ncolors)[None, :]

    # Color scale map preview plot
    fig, ax = plt.subplots()

    # Plot the example data
    tmin, tmax = scale.extent
    tmin, tmax = tmin + offset, tmax + offset
    im = ax.imshow(data, aspect="auto", cmap=scale.cmap, vmin=tmin, vmax=tmax)

    # Create the color bar with the measurement scale
    cbar = fig.colorbar(im, orientation="horizontal")

    cbar_ref = ColorbarTicks((tmin, tmax), nticks, 0)
    cbar.set_ticks(cbar_ref.cticks)

    # Note: Alternatively `norm=scale.cnorm` can be passed to imshow and
    # `cbar.ax.minorticks_off()` is used to inhibit the minor ticks.

    # Hide the y-axis since it does not make sense
    ax.tick_params(
        axis="y", which="both", left=False, right=False, labelleft=False
    )

    # Set the title, x-axis label and the colorbar caption
    plt.title(scale.name)

    ax.set_xlabel("Color Index", color="black", labelpad=3.0)

    if not measurement:
        measurement = "Measurement"

    cbar.set_label(label=measurement, color="black", weight="normal")

    plt.show()
