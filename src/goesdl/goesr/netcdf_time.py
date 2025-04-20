from datetime import datetime
from typing import cast

from netCDF4 import Dataset  # pylint: disable=no-name-in-module
from numpy import datetime64

from ..netcdf import HasStrHelp

NOT_A_DATETIME = cast(datetime, datetime64("NaT"))


class GOESCoverageTime(HasStrHelp):

    datetime_start: datetime = NOT_A_DATETIME
    datetime_end: datetime = NOT_A_DATETIME

    def __init__(self, record: Dataset) -> None:
        datetime_start = getattr(record, "time_coverage_start", "")
        datetime_end = getattr(record, "time_coverage_end", "")

        if datetime_start and datetime_end:
            self.datetime_start = datetime.fromisoformat(datetime_start)
            self.datetime_end = datetime.fromisoformat(datetime_end)

    @property
    def timestamp_start(self) -> float:
        return self.datetime_start.timestamp()

    @property
    def timestamp_end(self) -> float:
        return self.datetime_end.timestamp()
