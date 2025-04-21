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
    def timestamp_start(self) -> float:
        return self.datetime_start.timestamp()

    @property
    def timestamp_end(self) -> float:
        return self.datetime_end.timestamp()
