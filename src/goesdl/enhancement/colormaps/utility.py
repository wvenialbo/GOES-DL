from typing import cast

from matplotlib import colormaps
from matplotlib.colors import Colormap, LinearSegmentedColormap, ListedColormap


def make_cmap(
    name: str,
    colors: list[tuple[int, ...]] | list[tuple[float, ...]],
    *,
    discrete: bool = False,
    integers: bool = False,
    ncolors: int = 256,
) -> Colormap:
    """
    Create a Colormap object from a list of colors.

    Parameters
    ----------
    name : str
        The name of the colormap.
    colors : list[tuple[int, ...]] | list[tuple[float, ...]]
        The RGB color values. If `integers` is True, values should be integers
        in 0-255 range; otherwise floats in 0.0-1.0 range.
    discrete : bool
        If True, creates a ListedColormap for discrete color maps.
        By default False.
    integers : bool
        If True, converts color values from 0-255 to 0.0-1.0.
        By default False.

    Returns
    -------
    Colormap
        A ListedColormap if `discrete` is True, otherwise a
        LinearSegmentedColormap.
    """
    if integers:
        colors = to_float(cast(list[tuple[int, ...]], colors))
    if discrete:
        return ListedColormap(colors, name, N=ncolors)
    return LinearSegmentedColormap.from_list(name, colors, N=ncolors)


def register_cmap(
    colormap: Colormap,
    *,
    name: str | None = None,
    raise_if_already: bool = False,
) -> None:
    """
    Register a custom colormap with matplotlib's colormaps.

    Parameters
    ----------
    name : str | None
        The name to register the colormap under.
    colors : list[tuple[int, ...]] | list[tuple[float, ...]]
        The RGB color values. If `integers` is True, values should be integers
        in 0-255 range; otherwise floats in 0.0-1.0 range.
    discrete : bool
        If True, registers a ListedColormap instead of continuous map.
        By default False.
    integers : bool
        If True, converts color values from 0-255 to 0.0-1.0.
        By default False.
    """
    cm_name = name or colormap.name
    if cm_name in colormaps and not raise_if_already:
        return
    colormaps.register(colormap, name=name)


def to_float(colors: list[tuple[int, ...]]) -> list[tuple[float, ...]]:
    """
    Convert color values from integer to float.

    Converts a list of RGB color tuples from integer [0-255] range to
    float [0.0-1.0] range format.

    This function is useful for preparing color data for libraries that
    require normalized RGB values.

    Parameters
    ----------
    colors : list[tuple[int, ...]]
        A list of tuples, where each tuple contains float values
        representing RGB color components in the [0-255] range.

    Returns
    -------
    list[tuple[float, ...]]
        A list of tuples, where each tuple contains integer values in
        the [0.0-1.0] range representing RGB colors components.
    """
    return [tuple(c / 255.0 for c in rgb) for rgb in colors]


def to_integer(colors: list[tuple[float, ...]]) -> list[tuple[int, ...]]:
    """
    Convert color values from float to integer.

    Converts a list of RGB color tuples from float [0.0-1.0] range to
    integer [0-255] range format.

    This function is useful for preparing color data for libraries that
    require integer RGB values.

    Parameters
    ----------
    colors : list[tuple[float, ...]]
        A list of tuples, where each tuple contains float values
        representing RGB color components in the [0.0-1.0] range.

    Returns
    -------
    list[tuple[int, ...]]
        A list of tuples, where each tuple contains integer values in
        the [0-255] range representing RGB colors components.
    """
    return [tuple(round(255 * c) for c in rgb) for rgb in colors]


def generate_colormap(
    name: str, colors: list[tuple[int, ...]], *, discrete: bool = False
) -> str:
    listed_colors = [
        f'({", ".join((f"{c:>3d}" for c in rgb))})' for rgb in colors
    ]

    cm_data = ",\n    ".join(listed_colors)

    extra_param = ", discrete=True" if discrete else ""

    return f"""from .utility import make_cmap, register_cmap, to_float

_{name}_data: list[tuple[int, ...]] = [
    {cm_data},
]

_cm_name = "{name}"
_cm_data = to_float(_{name}_data)

{name} = make_cmap(_cm_name, _cm_data, integers=True, ncolors=256{extra_param})

register_cmap({name}, name=_cm_name)
"""
