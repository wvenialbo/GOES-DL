"""
Provide functionality for reading fragments NetCDF datasets.

NetCDF (Network Common Data Form) is a file format and set of software
libraries for storing and sharing scientific data. It's designed to make
it easy to access array-oriented data.

This package provides classes to extract and represent information from
NetCDF data files. The classes dynamically set attributes based on the
annotations defined in the class and the corresponding attributes or
variables present in the provided NetCDF data object.
"""

from . import fields
from .class_help import HasStrHelp
from .fields import (
    attribute,
    computed,
    data,
    dimension,
    field,
    variable,
)
from .view import DatasetView

__all__ = [
    "attribute",
    "computed",
    "data",
    "DatasetView",
    "dimension",
    "field",
    "fields",
    "HasStrHelp",
    "variable",
]
