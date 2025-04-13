"""
Provide methods for handling IR brightness temperature color enhancement.

It includes functions to load, parse, process, and save McIDAS and GMT
enhancement color tables, as well as reverse and manipulate color maps.
"""

from .table import ColorSegment


def compress_color_data(
    color_data: list[ColorSegment],
) -> list[ColorSegment]:
    """
    Compress color data by removing duplicate entries.

    Parameters
    ----------
    color_data : list of tuple of float
        List of color segments.

    Returns
    -------
    list of tuple of float
        Compressed color table.
    """
    compressed: list[ColorSegment] = [color_data[0]]

    for x2, c2, d2 in color_data[1:]:
        x1, c1, _ = compressed[-1]
        if x1 == x2:
            compressed[-1] = (x1, c1, d2)
        else:
            compressed.append((x2, c2, d2))

    return compressed
