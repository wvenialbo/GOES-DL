"""Provide constants for the enhancement utility module."""

from math import nan

BRG_MAX = 255.0
CLR_MAX = 255.0
CMYK_MAX = 100.0
HUE_MAX = 360.0
HSV_MAX = 100.0

CM_BGR = "BGR"
CM_RGB = "RGB"
CM_CMYK = "CMYK"
CM_GRAY = "GRAY"
CM_HSV = "HSV"

UNNAMED_COLORMAP = "UNNAMED"
UNNAMED_TABLE = UNNAMED_COLORMAP

COLOR_COMPONENTS = ["red", "green", "blue"]

CBTICKS_NMAX = 16
CBTICKS_SMIN = 5
CBTICKS_STEP = 0

NO_DATA_RGB = nan, 1.0, 0.0, 1.0
