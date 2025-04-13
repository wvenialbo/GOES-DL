"""
Provide methods for handling IR brightness temperature color enhancement.

It includes functions to load, parse, process, and save McIDAS and GMT
enhancement color tables, as well as reverse and manipulate color maps.
"""

from .palette import EnhacementPalette as EnhacementPalette
from .stretching import EnhacementStretching as EnhacementStretching
from .table import EnhacementTable as EnhacementTable
from .utility import compress_color_data as compress_color_data
