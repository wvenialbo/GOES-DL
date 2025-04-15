"""
Export the classes for the datasource objects.

The datasource objects are responsible for listing the contents of a
directory in a remote location and for downloading files from that
location.

Classes
-------
Datasource
    Abstract a datasource object.
DatasourceAWS
    A datasource object for an AWS S3 bucket.
DatasourceCache
    A datasource object that caches the files.
DatasourceNCEI
    A datasource object for an HTTP server.
DatasourceLocal
    A datasource object for a local directory.
"""

from .datasource import Datasource
from .datasource_aws import DatasourceAWS
from .datasource_cache import DatasourceCache
from .datasource_local import DatasourceLocal
from .datasource_ncei import DatasourceNCEI

__all__ = [
    "Datasource",
    "DatasourceAWS",
    "DatasourceCache",
    "DatasourceNCEI",
    "DatasourceLocal",
]
