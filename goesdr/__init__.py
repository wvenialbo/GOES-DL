"""Provide functionality for reading fragments of GOES-R datasets."""

from . import fields
from .datarecord import DataRecord
from .fields import dimension, field, record, variable

__all__ = [
    "DataRecord",
    "dimension",
    "field",
    "fields",
    "record",
    "variable",
]

__package_id__ = "GOES-DR"
__package_name__ = f"{__package_id__} — GOES Satellite Imagery Dataset Reader"
__version__ = "v0.1-rc1"
