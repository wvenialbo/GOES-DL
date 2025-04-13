"""
Provide methods for handling IR brightness temperature color enhancement.

It includes functions to load, parse, process, and save McIDAS and GMT
enhancement color tables, as well as reverse and manipulate color maps.
"""

CMYKValue = tuple[float, float, float, float]
ColorEntry = tuple[float, float, float, float]
DomainData = tuple[float, float]
RGBValue = tuple[float, float, float]
ValueTables = tuple[list[float], ...]

ColorTable = list[RGBValue]
PaletteData = list[ColorEntry]
PaletteItem = tuple[PaletteData, ColorTable]
StretchingTable = list[tuple[float, float]]
