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

from .fields import (
    computed,
    dimension,
    field,
    indexed,
    make_variable,
    record,
    scalar,
    variable,
)
from .fragment import DataFragment, netcdf_fragment

__all__ = [
    "computed",
    "DataFragment",
    "dimension",
    "field",
    "fields",
    "indexed",
    "make_variable",
    "netcdf_fragment",
    "record",
    "scalar",
    "variable",
]
