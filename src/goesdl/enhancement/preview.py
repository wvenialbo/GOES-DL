import matplotlib.pyplot as plt
import numpy as np

from .scale import EnhancementScale
from .ticks import ColorbarTicks


def show_colormap(scale: EnhancementScale, offset: float = 0.0) -> None:
    # Example data
    vmin, vmax = scale.domain
    vmin, vmax = vmin + offset, vmax + offset
    data = np.linspace(vmin, vmax, scale.ncolors)[None, :]

    # Color scale map preview plot
    fig, ax = plt.subplots()

    plt.title(scale.name)

    im = ax.imshow(data, aspect="auto", cmap=scale.cmap, norm=scale.cnorm)

    cbar = fig.colorbar(im, orientation="horizontal")
    cbar_ref = ColorbarTicks(scale.domain, 14, 0)
    cbar.set_ticks(cbar_ref.cticks)

    plt.show()
