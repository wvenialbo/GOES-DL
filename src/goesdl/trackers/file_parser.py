from typing import TextIO


def read_lines(file: TextIO, nlines: int) -> list[str]:
    """
    Read a specified number of lines from a file.

    Parameters
    ----------
    file : TextIO
        The file object to read from.
    nlines : int
        The number of lines to read.

    Returns
    -------
    list[str]
        A list of lines read from the file.
    """
    data_lines: list[str] = []
    for _ in range(nlines):
        try:
            data_lines.append(next(file))
        except StopIteration:
            break
    return data_lines


def skip_lines(file: TextIO, nlines: int) -> None:
    """
    Skip a specified number of lines in a file.

    Parameters
    ----------
    file : TextIO
        The file object to skip lines in.
    nlines : int
        The number of lines to skip.
    """
    for _ in range(nlines):
        try:
            next(file)
        except StopIteration:
            break
