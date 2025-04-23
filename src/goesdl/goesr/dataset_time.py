from datetime import datetime

from ..netcdf import DatasetView, attribute


class GOESCoverageTime(DatasetView):

    datetime_start: datetime = attribute(
        "time_coverage_start", convert=datetime.fromisoformat
    )
    datetime_end: datetime = attribute(
        "time_coverage_end", convert=datetime.fromisoformat
    )

    @property
    def datetime_midpoint(self) -> datetime:
        delta = self.datetime_end - self.datetime_start
        return self.datetime_start + delta / 2

    @property
    def timestamp_end(self) -> float:
        return self.datetime_end.timestamp()

    @property
    def timestamp_midpoint(self) -> float:
        return self.datetime_midpoint.timestamp()

    @property
    def timestamp_start(self) -> float:
        return self.datetime_start.timestamp()
