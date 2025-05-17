from datetime import datetime
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
    interval: int
    tolerance: int
    dateformat: str
    repository: Path

    def __init__(
        self,
        repository: str | Path,
        *,
        locator: ProductLocator,
        interval: int = 600,
        tolerance: int = 90,
        dateformat: str = ISO_TIMESTAMP_FORMAT,
    ) -> None:
        self.locator = locator
        self.interval = interval
        self.tolerance = tolerance
        self.dateformat = dateformat
        self.repository = Path(repository)

    def get_sequence(
        self,
        coverage_class: type[CoverageTime],
        *,
        start: str,
        end: str = "",
        relative: bool = False,
        use_end: bool = False,
    ) -> tuple[list[str], list[float]]:
        timestamps = self._get_timestamps(start, end)

        sequence = self._build_sequence(
            coverage_class, start, end, timestamps, use_end
        )

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
        coverage_class: type[CoverageTime],
        start: str,
        end: str,
        timestamps: list[float],
        use_end: bool,
    ) -> list[str]:
        available_files = self.locate_files(start=start, end=end)

        sequence: list[str] = []

        i = 0
        for path in available_files:
            with Dataset(path, "r") as dataframe:
                coverage = coverage_class(dataframe)

            timestamp = (
                coverage.timestamp_end if use_end else coverage.timestamp_start
            )

            abs_diff = abs(timestamp - timestamps[i])

            while abs_diff > self.tolerance:
                sequence.append("")
                i += 1
                abs_diff = abs(timestamp - timestamps[i])

            if abs_diff <= self.tolerance:
                sequence.append(str(path))
                i += 1

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
        count = int((end_ts - start_ts) // self.interval)

        timestamps: list[float] = [
            start_ts + i * self.interval for i in range(count + 1)
        ]

        return timestamps
