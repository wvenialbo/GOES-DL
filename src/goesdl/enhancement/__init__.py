"""
Provide methods for handling IR brightness temperature color enhancement.

It includes functions to load, parse, process, and save McIDAS and GMT
enhancement color tables, as well as reverse and manipulate color maps.
"""

from .catalogue import cmap
from .colormap import EnhancementColormap
from .palette import EnhacementPalette
from .preview import show_colormap
from .scale import EnhancementScale
from .stretching import EnhacementStretching
from .table import EnhacementTable

__all__ = [
    "EnhancementColormap",
    "EnhacementPalette",
    "EnhancementScale",
    "EnhacementStretching",
    "EnhacementTable",
    "show_colormap",
    "cmap",
]
