from datetime import datetime
from typing import Protocol

from netCDF4 import Dataset


class CoverageTime(Protocol):

    def __init__(self, dataframe: Dataset) -> None: ...

    @property
    def datetime_start(self) -> datetime: ...

    @property
    def datetime_end(self) -> datetime: ...

    @property
    def datetime_midpoint(self) -> datetime: ...

    @property
    def timestamp_end(self) -> float: ...

    @property
    def timestamp_midpoint(self) -> float: ...

    @property
    def timestamp_start(self) -> float: ...
