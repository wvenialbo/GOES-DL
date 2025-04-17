from .scale import EnhancementScale


def _ircolor() -> EnhancementScale:
    # Define the properties of a stock palette
    key_points = (200.0, 240.0, 320.0)  # (180, 240, 330)
    color_maps = ("jet_r", "gray_r")
    cmap_name = f"IRCOLOR {int(key_points[0])}-{int(key_points[1])}K"

    # Get a stock palette and configure the ticks for the colorbar, for this example
    return EnhancementScale.from_colormap(cmap_name, color_maps, key_points)


cmap: dict[str, EnhancementScale] = {"IRCOLOR": _ircolor()}
