"""Provide functionality for reading fragments of GOES-R datasets."""

from . import fields
from .datarecord import DataFragment
from .fields import dimension, field, record, variable
from .fragment import netcdf_fragment

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
