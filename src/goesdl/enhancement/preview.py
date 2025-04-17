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

    tmin, tmax = scale.extent
    im = ax.imshow(data, aspect="auto", cmap=scale.cmap, vmin=tmin, vmax=tmax)

    cbar = fig.colorbar(im, orientation="horizontal")
    cbar_ref = ColorbarTicks(scale.domain, nticks, 0)
    cbar.set_ticks(cbar_ref.cticks)

    ax.tick_params(
        axis="y", which="both", left=False, right=False, labelleft=False
    )

    plt.title(scale.name)

    ax.set_xlabel("Color Index", color="black", labelpad=3.0)

    if not measurement:
        measurement = "Measurement"

    cbar.set_label(label=measurement, color="black", weight="normal")

    # Note: Alternatively `norm=scale.cnorm` can be passed to imshow and
    # `cbar.ax.minorticks_off()` is used to inhibit the minor ticks.

    plt.show()
