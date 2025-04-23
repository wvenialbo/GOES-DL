from collections.abc import Sequence
from datetime import datetime


def str_to_float(value_strings: Sequence[str]) -> list[float]:
    """
    Convert a sequence of strings to a list of floats.

    Parameters
    ----------
    value_strings : Sequence[str]
        A sequence of strings representing numeric values.

    Returns
    -------
    list[float]
        A list of floats converted from the input strings.
    """
    return [float(value) for value in value_strings]


def iso_to_timestamp(iso_strings: Sequence[str]) -> list[float]:
    """
    Convert a sequence of ISO date strings to a list of timestamps.

    Each ISO date string is expected to be in the format
    'YYYY-MM-DDTHH[:MM[:SS]]Z'.

    Parameters
    ----------
    iso_strings : Sequence[str]
        A sequence of ISO date strings.

    Returns
    -------
    list[float]
        A list of timestamps in seconds since the epoch.
    """
    # Convertir fechas ISO a timestamps en segundos desde la época
    return [
        datetime.fromisoformat(iso_string).timestamp()
        for iso_string in iso_strings
    ]
