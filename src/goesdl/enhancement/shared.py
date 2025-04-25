"""
Provide methods for handling IR brightness temperature color enhancement.

It includes functions to load, parse, process, and save McIDAS and GMT
enhancement color tables, as well as reverse and manipulate color maps.
"""

from collections.abc import Sequence
from typing import Any, Literal

ColorEntry = tuple[float, float, float, float]
DomainData = tuple[float, float]

CMYKValue = ColorEntry
RGBValue = tuple[float, float, float]

ColorTable = list[RGBValue]
PaletteData = list[ColorEntry]
PaletteItem = tuple[PaletteData, ColorTable]
StretchingTable = list[tuple[float, float]]
ValueTables = tuple[list[float], ...]

# Listed colours

GColorValue = Sequence[Any]
GListedColors = Sequence[GColorValue]

ListedColors = list[RGBValue]

# Colour segments

GSegmentEntry = Sequence[Any]
GSegmentData = dict[str, Sequence[GSegmentEntry]]

MColorSegment = tuple[float, ...]
MComponents = Literal["red", "green", "blue", "alpha"]
MSegmentData = dict[MComponents, Sequence[MColorSegment]]

SegmentEntry = tuple[float, float, float]
SegmentData = dict[str, list[SegmentEntry]]
