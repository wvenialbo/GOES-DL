from datetime import UTC, datetime
from glob import glob
from os.path import isfile, join, relpath
from pathlib import Path

from netCDF4 import Dataset

from ..dataset import ProductLocator
from ..datasource import DatasourceLocal
from ..protocols import CoverageTime
from .constants import ISO_TIMESTAMP_FORMAT
from .downloader import Downloader


class DatasetInventory:

    locator: ProductLocator
    coverage: type[CoverageTime] | None
    interval: int
    dateformat: str
    repository: Path

    def __init__(
        self,
        repository: str | Path,
        *,
        locator: ProductLocator,
        coverage: type[CoverageTime] | None = None,
        interval: int = 600,
        dateformat: str = ISO_TIMESTAMP_FORMAT,
    ) -> None:
        self.locator = locator
        self.coverage = coverage
        self.interval = interval
        self.dateformat = dateformat
        self.repository = Path(repository)

    def filter_missing_entries(
        self, paths: list[str], timestamps: list[float]
    ) -> tuple[list[datetime], int]:
        return [
            datetime.fromtimestamp(timestamp, UTC)
            for path, timestamp in zip(paths, timestamps)
            if not path
        ], len(paths)

    def get_missing_entries(
        self,
        *,
        start: str,
        end: str = "",
        relative: bool = False,
        use_end: bool = False,
    ) -> tuple[list[datetime], int]:
        sequence = self.get_sequence(
            start=start, end=end, relative=relative, use_end=use_end
        )
        return self.filter_missing_entries(*sequence)

    def get_sequence(
        self,
        *,
        start: str,
        end: str = "",
        relative: bool = False,
        use_end: bool = False,
    ) -> tuple[list[str], list[float]]:
        timestamps = self._get_timestamps(start, end)

        sequence = self._build_sequence(start, end, timestamps, use_end)

        # Get the relative paths
        if relative:
            for i, path in enumerate(sequence):
                if path:
                    relative_path = relpath(path, self.repository)
                    sequence[i] = relative_path

        return sequence, timestamps

    def locate_files(
        self, *, start: str, end: str = "", relative: bool = False
    ) -> list[Path]:
        # Datasets will be acquired from a local repository
        localfiles = DatasourceLocal(self.repository)

        # Initialize the downloader with the locator and datasource
        downloader = Downloader(
            datasource=localfiles,
            locator=self.locator,
            repository=self.repository,
            date_format=self.dateformat,
            show_progress=False,
        )

        content = downloader.list_files(start=start, end=end)

        if relative:
            return [Path(path) for path in content]

        return [self.repository / path for path in content]

    def search_pattern(
        self, *, pattern: str = "**/*.nc", relative: bool = False
    ) -> list[Path]:
        """
        Return a list of paths matching a pathname pattern.

        Parameters
        ----------
        pattern : str

        Returns
        -------
        list[str]
            A list of file paths matching a pathname pattern within the
            repository directory.
        """
        # Retrieve the list of matching pathnames
        recursive = "**/" in pattern
        pathname = join(self.repository, pattern)

        content = glob(pathname, recursive=recursive)

        # Filtering the directory content to extract only file elements
        content = sorted(filter(isfile, content))

        # Get the relative paths
        if relative:
            content = [relpath(file, self.repository) for file in content]

        return [Path(path) for path in content]

    def _build_sequence(
        self,
        start: str,
        end: str,
        timestamps: list[float],
        use_end: bool,
    ) -> list[str]:
        if self.coverage is None:
            raise ValueError("CoverageTime inspector class is not set")

        coverage_class = self.coverage

        available_files = self.locate_files(start=start, end=end)

        total_expected = len(timestamps)

        sequence: list[str] = [""] * total_expected

        i = 0  # Index for expected timestamps

        for path in available_files:
            # Get the file timestamp
            with Dataset(path, "r") as dataframe:
                coverage = coverage_class(dataframe)

            timestamp = (
                coverage.timestamp_end if use_end else coverage.timestamp_start
            )

            # Advance the index until the correct interval is found
            while i < total_expected and timestamps[i] <= timestamp:
                i += 1

            # This is completely unexpected and should not happen
            if i == 0:
                raise ValueError(
                    f"File '{path}' is before the start time {start}"
                )

            j = -1  # Index for the insertion of the file path

            # Assign the file path to the correct interval lower bound
            if i < total_expected or timestamps[j] + self.interval > timestamp:
                j = i - 1

            # This is completely unexpected and should not happen
            if j < 0:
                raise ValueError(f"File '{path}' is after the end time {end}")

            # Throw and error if a file path is already set
            if sequence[j]:
                raise ValueError(
                    f"File '{path}' is in the same interval as '{sequence[j]}', "
                    "set a smaller interval"
                )

            # Assign the file path to the correct interval lower bound
            sequence[j] = str(path)

        return sequence

    def _get_timestamps(
        self,
        start: str,
        end: str,
    ) -> list[float]:
        start_dt = datetime.strptime(start, self.dateformat)
        end_dt = datetime.strptime(end or start, self.dateformat)

        start_ts = start_dt.timestamp()
        end_ts = end_dt.timestamp()

        ninterval = (end_ts - start_ts) / self.interval

        if not ninterval.is_integer():
            raise ValueError(
                f"Start and end times are not aligned with the interval "
                f"of {self.interval} seconds"
            )

        count = int(ninterval + 1)

        timestamps: list[float] = [
            start_ts + i * self.interval for i in range(count)
        ]

        return timestamps
