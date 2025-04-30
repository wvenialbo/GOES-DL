"""
Provide methods for handling IR brightness temperature color enhancement.

It includes functions to load, parse, process, and save McIDAS and GMT
enhancement color tables, as well as reverse and manipulate color maps.
"""

from .catalogue import get_scale
from .palette import EnhacementPalette
from .preview import plot_brightness_profile, preview_colormap
from .scale import EnhancementScale
from .stretching import EnhacementStretching, get_stmap
from .ticks import ColorbarTicks

__all__ = [
    "ColorbarTicks",
    "EnhacementPalette",
    "EnhancementScale",
    "EnhacementStretching",
    "plot_brightness_profile",
    "preview_colormap",
    "get_scale",
    "get_stmap",
]
