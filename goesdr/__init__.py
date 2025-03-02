"""
Provide functionality for reading fragments of GOES-R datasets.

This package provides classes to extract and represent information from
GOES satellite netCDF data files. The classes dynamically set attributes
based on the annotations defined in the class and the corresponding
attributes or variables present in the provided netCDF data object.
"""

from . import fields
from .fields import dimension, field, record, variable
from .fragment import DataFragment, netcdf_fragment

__all__ = [
    "DataFragment",
    "dimension",
    "field",
    "fields",
    "netcdf_fragment",
    "record",
    "variable",
]

__package_id__ = "GOES-DR"
__package_name__ = f"{__package_id__} — GOES Satellite Imagery Dataset Reader"
__version__ = "v0.1-rc1"
