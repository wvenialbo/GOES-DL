import matplotlib.pyplot as plt


def plot_difference(
    matrices,
    filename=None,
    captions=None,
    cmap="viridis",
    figsize=(8, 8),
    figdpi=200,
    imgdpi=200,
    title=None,
    subtitle=None,
    show=True,
):
    """
    Plots four matrices (interpreted as images) in two rows.
    
    Args:
        titles: An optional list of three strings, specifying the titles for each plot.
            Defaults to None (no titles).
        cmap: The colormap to use for displaying the matrices. Defaults to 'viridis'.
            See matplotlib documentation for available colormaps.
    """
    if isinstance(cmap, tuple):
        cmap = list(cmap)

    if isinstance(cmap, str):
        cmap = [cmap] * 4
    elif len(cmap) == 1:
        cmap = cmap * 4
    elif len(cmap) == 2:
        cmap = [cmap[0]] * 3 + [cmap[1]] * 2
    elif len(cmap) == 3:
        cmap = [cmap[0]] * 2 + cmap[1:]

    fig, axes = plt.subplots(2, 2, figsize=figsize, dpi=figdpi)

    if captions is None:
        captions = []
    elif isinstance(captions, str):
        captions = [captions]

    title_size = 7
    subtitle_size = 4.5
    caption_size = 4.5
    label_size = 4
    tick_size = 3.5
    axis_size = 4
    y_title = 0.93

    if subtitle:
        y_title = 0.95
        fig.text(0.5, 0.903, subtitle, ha='center', va='bottom', fontsize=subtitle_size)

    if title:
        fig.suptitle(title, fontsize=title_size, y=y_title)

    if len(captions) == 1:
        fig.text(0.5, 0.92, captions[0], ha='center', va='bottom', fontsize=caption_size)
    elif len(captions) == 2:
        fig.text(0.5, 0.92, captions[0], ha='center', va='bottom', fontsize=caption_size)
        fig.text(0.5, 0.50, captions[1], ha='center', va='bottom', fontsize=caption_size)
    elif len(captions) == 3:
        fig.text(0.5, 0.92, captions[0], ha='center', va='bottom', fontsize=caption_size)
        axes[1, 0].set_title(captions[1], fontsize=caption_size)
        axes[1, 1].set_title(captions[2], fontsize=caption_size)
    elif len(captions) == 4:
        axes[0, 0].set_title(captions[0], fontsize=caption_size)
        axes[0, 1].set_title(captions[1], fontsize=caption_size)
        axes[1, 0].set_title(captions[2], fontsize=caption_size)
        axes[1, 1].set_title(captions[3], fontsize=caption_size)

    plt.subplots_adjust(right=0.85, hspace=0.3, wspace=1.0)

    vmin = (200, 200, -90, 0)
    vmax = (300, 300, +90, 1)

    # Plot the matrices
    for i in range(2):
        for j in range(2):
            k = i * 2 + j
            ax = axes[i, j]
            im = ax.imshow(matrices[k], cmap=cmap[k], vmin=vmin[k], vmax=vmax[k])

            ax.tick_params(
                left=True,
                right=False,
                bottom=True,
                top=False,
                labelleft=True,
                labelright=False,
                labelbottom=True,
                labeltop=False,
                length=1.1,
                width=0.3,
                labelsize=tick_size,
                pad=1.1,
                labelcolor="black",
            )
            ax.set_xlabel("Pixel indices", color="black", fontsize=axis_size, labelpad=1.0)
            ax.set_ylabel("Pixel indices", color="black", fontsize=axis_size, labelpad=0.5)

            [x.set_linewidth(0.3) for x in ax.spines.values()]

            cb_width = 0.05
            cb_left = 1.07
            cb_bottom = 0
            cb_height = 1.0

            # Crear un nuevo eje para la barra de color
            cax = ax.inset_axes([cb_left, cb_bottom, cb_width, cb_height])

            # Añadir la barra de color al nuevo eje
            cb = fig.colorbar(im, cax=cax)
            cax.tick_params(
                length=1.1,
                width=0.3,
                labelsize=label_size,
            )
            # cb.set_label(label="K", size=label_size, color="black", weight="normal")
            
            [x.set_linewidth(0.3) for x in cax.spines.values()]

    # Adjust layout to prevent overlapping titles
    plt.tight_layout()
    
    # Show the media file
    if filename:
        plt.savefig(filename, dpi=imgdpi, bbox_inches='tight')
    
    # Show the plot
    if show:
        plt.show()
    else:
        plt.close(fig)
