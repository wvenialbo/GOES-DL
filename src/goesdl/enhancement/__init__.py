"""
Provide methods for handling IR brightness temperature color enhancement.

It includes functions to load, parse, process, and save McIDAS and GMT
enhancement color tables, as well as reverse and manipulate color maps.
"""

from .catalogue import get_scale
from .generator import ColormapGenerator
from .palette import EnhancementPalette
from .scale import EnhancementScale
from .stretching import EnhancementStretching, get_stmap
from .ticks import ColorbarTicks

__all__ = [
    "ColorbarTicks",
    "ColormapGenerator",
    "EnhancementPalette",
    "EnhancementScale",
    "EnhancementStretching",
    "get_scale",
    "get_stmap",
]
