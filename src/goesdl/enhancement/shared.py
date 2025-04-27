"""
Provide methods for handling IR brightness temperature color enhancement.

It includes functions to load, parse, process, and save McIDAS and GMT
enhancement color tables, as well as reverse and manipulate color maps.
"""

from collections.abc import Sequence
from typing import Any, Literal

DomainData = tuple[float, float]

StretchingTable = list[tuple[float, float]]

# Keypoint and colour values structure

ValueTableColumn = list[float]
ValueTables = tuple[ValueTableColumn, ...]

# RGB packed colour value

RGBValue = tuple[float, float, float]

# Colour table structure

ColorTableRow = tuple[float, float, float, float]
ColorTable = list[ColorTableRow]

# Listed colours

# Generic discrete colour map list
GColorValue = Sequence[Any]
GListedColors = Sequence[GColorValue]

# Natively defined discrete colour map list
ListedColors = list[RGBValue]

# Colour segments

# Generic colour segment data
GSegmentEntry = Sequence[Any]
GSegmentData = dict[str, Sequence[GSegmentEntry]]

# Colour segment data as defined in Matplotlib
MColorSegment = tuple[float, ...]
MComponents = Literal["red", "green", "blue", "alpha"]
MSegmentData = dict[MComponents, Sequence[MColorSegment]]

# Natively defined colour segment data
ColorSegment = tuple[float, float, float]
SegmentData = dict[str, list[ColorSegment]]
