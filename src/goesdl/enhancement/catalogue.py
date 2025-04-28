from .scale import EnhancementScale


def get_scale(enhancement_name: str) -> EnhancementScale:
    palette_name, stretching_name = (enhancement_name.split("/") + [""])[:2]

    if palette_name not in cmap:
        supported_cmaps = "'".join(cmap.keys())
        raise ValueError(
            f"'{palette_name}' is not a valid colour map name, supported values are: "
            f"'{supported_cmaps}'"
        )

    if stretching_name and stretching_name not in smap:
        supported_smaps = "'".join(smap.keys())
        raise ValueError(
            f"'{stretching_name}' is not a valid stretching table name, supported values are: "
            f"'{supported_smaps}'"
        )
    else:
        stretching_name = stretching_name or "K200-240"

    palette = cmap[palette_name]
    stretching = smap[stretching_name]

    return EnhancementScale(palette, stretching)


def _ircolor() -> EnhancementScale:
    # Define the properties of a stock palette
    key_points = (200.0, 240.0, 320.0)  # (180, 240, 330)
    color_maps = ("jet_r", "gray_r")
    cmap_name = f"IRCOLOR {int(key_points[0])}-{int(key_points[1])}K"

    # Get a stock palette and configure the ticks for the colorbar, for this example
    return EnhancementScale.from_colormap(cmap_name, color_maps, key_points)


# cmap: dict[str, EnhancementScale] = {"IRCOLOR": _ircolor()}

cmap: dict[str, int] = {}
smap: dict[str, int] = {}
