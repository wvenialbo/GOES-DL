"""
Provide methods for handling IR brightness temperature color enhancement.

It includes functions to load, parse, process, and save McIDAS and GMT
enhancement color tables, as well as reverse and manipulate color maps.
"""

from collections.abc import Sequence
from typing import Any, Literal

DomainData = tuple[float, float]


# Colour scale stretching table

StretchingTableRow = tuple[float, float]
StretchingTable = list[StretchingTableRow]


# Keypoint and colour values tabular structure

ValueTableColumn = list[float]
ValueTable = tuple[ValueTableColumn, ...]

# Generic and natively specialised keypoints
GKeypointList = Sequence[float]
KeypointList = ValueTableColumn


# RGB packed colour value

RGBValue = tuple[float, float, float]


# Colour table structure

ColorTableRow = tuple[float, float, float, float]
ColorTable = list[ColorTableRow]


# Listed colours

# Generic discrete colour map list
GColorValue = Sequence[Any]
GListedColors = Sequence[GColorValue]

# Discrete colour map definition list
DiscreteColorList = list[RGBValue]

# Continuous colour gradient definition list and table
ContinuousColorList = DiscreteColorList
ContinuousColorTableRow = tuple[float, RGBValue]
ContinuousColorTable = list[ContinuousColorTableRow]


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
