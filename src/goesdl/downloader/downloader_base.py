"""
Define the base class for the downloader object.

The downloader object is responsible for downloading files from a
specified location using a datasource and product locator.

Classes
-------
DownloaderBase
    Represent a downloader object.
"""

import os
from dataclasses import dataclass
from datetime import datetime, timedelta

from ..dataset import ProductLocator
from ..datasource import Datasource
from ..utils import FileRepository
from .constants import (
    ISO_TIMESTAMP_FORMAT,
    TIME_TOLERANCE_DEFAULT,
    TIME_TOLERANCE_MAX,
    TIME_TOLERANCE_MIN,
    DownloadStatus,
)


@dataclass(eq=False, frozen=True)
class DownloaderBase:
    """
    Represent a downloader object.

    Methods
    -------
    download_files(start_time: str, end_time: str = "")
        Download files from the datasource into the local repository.
    get_files(start_time: str, end_time: str = "")
        Load a list of files from the datasource or local repository.
    list_files(start_time: str, end_time: str = "")
        List the files that can be retrieved from the datasource.

    Attributes
    ----------
    datasource : Datasource
        A reference to the datasource object.
    locator : ProductLocator
        A reference to the dataset's product locator object.
    repository : FileRepository
        A reference to the local repository object.
    date_format : str
        The date format specification. The default is the full ISO 8601
        timestamp format.
    time_tolerance : int
        The time tolerance in seconds. The default is 60 seconds.
    show_progress : bool
        A flag to show the progress of the download. The default is
        True, to display the progress.
    """

    datasource: Datasource
    locator: ProductLocator
    repository: FileRepository
    date_format: str = ISO_TIMESTAMP_FORMAT
    time_tolerance: int = TIME_TOLERANCE_DEFAULT
    show_progress: bool = True

    def __post_init__(self) -> None:
        """
        Validate the downloader object.

        Raises
        ------
        ValueError
            If the `time_tolerance` is less than the minimum allowed
            value or greater than the maximum allowed value.
        """
        if self.time_tolerance < TIME_TOLERANCE_MIN:
            raise ValueError(
                "time_tolerance must be greater than or equal "
                f"to {TIME_TOLERANCE_MIN} seconds"
            )
        if self.time_tolerance > TIME_TOLERANCE_MAX:
            raise ValueError(
                "time_tolerance must be less than or equal "
                f"to {TIME_TOLERANCE_MAX} seconds"
            )

    def download_files(self, *, start: str, end: str = "") -> list[str]:
        """
        Download files from the datasource into the local repository.

        Download the files that match the timestamps between `start` and
        `end` times, inclusive, from the datasource and save them in the
        local repository. The list is filtered by the timestamps of the
        files; only files in the requested range are downloaded. If the
        file is already in the local repository, it is not downloaded
        again.

        Note that a `start` date must be always provided. If an `end`
        date is not given, it is set equal to `start_time`. An offset of
        `time_tolerance` seconds (60 by default) is subtracted from the
        initial datetime and added to the final datetime to account for
        possible differences in the files' timestamps.

        Parameters
        ----------
        start : str
            The start time in the format specified by the `date_format`
            attribute.
        end : str
            The end time in the format specified by the `date_format`
            attribute. The default is "", in which case `end_time` is
            set equal to `start_time`.

        Returns
        -------
        list[str]
            A list of file path and names with respect to the local
            repository root directory.

        Notes
        -----
        `ValueError` is raised if `start_time` is not provided or if the
        provided timestamp strings and format can't be parsed (which is,
        indeed, a bug!).

        The framework may raise `RuntimeError` if the file cannot be
        retrieved, e.g. if the file does not exist in the datasource or
        an internal error occurred.

        `FileExistsError` might be raised if the file already exists in
        the repository.
        """
        files_in_range = self._get_file_list(start, end)

        self._retrieve_files(files_in_range)

        return files_in_range

    def get_files(self, *, file_paths: list[str]) -> None:
        """
        Load a list of files from the datasource or local repository.

        Load the files in the `file_paths` list from the datasource or
        local repository. If the file is not in the local repository, it
        is retrieved from the datasource and saved in the local
        repository.

        Parameters
        ----------
        file_paths : list[str]
            A list with the file paths.

        Notes
        -----
        The framework may raise `RuntimeError` if the file cannot be
        retrieved, e.g. if the file does not exist in the datasource or
        an internal error occurred.

        `FileExistsError` might be raised if the file already exists in
        the repository.
        """
        self._retrieve_files(file_paths)

    def list_files(self, *, start: str, end: str = "") -> list[str]:
        """
        List the files that can be retrieved from the datasource.

        List the files that match the timestamps between `start` and
        `end` times, inclusive, from the datasource or local repository.
        The list is filtered by the timestamps of the files; only files
        in the requested range are returned. This list can be filtered
        using custom criteria then passed to the `get_files()` method.

        Note that a `start` date must be always provided. If an `end`
        date is not given, it is set equal to `start_time`. An offset of
        `time_tolerance` seconds (60 by default) is subtracted from the
        initial datetime and added to the final datetime to account for
        possible differences in the files' timestamps.

        Parameters
        ----------
        start : str
            The start time in the format specified by the `date_format`
            attribute.
        end : str
            The end time in the format specified by the `date_format`
            attribute. The default is "", in which case `end_time` is
            set equal to `start_time`.

        Returns
        -------
        list[str]
            A list of file path and names with respect to the local
            repository root directory.

        Notes
        -----
        `ValueError` is raised if `start_time` is not provided or if the
        provided timestamp strings and format can't be parsed (which is,
        indeed, a bug!).
        """
        return self._get_file_list(start, end)

    def _add_item(self, file_path: str, file: bytes) -> None:
        if self._has_item(file_path):
            raise FileExistsError(f"File '{file_path}' already in repository.")

        self.repository.save_file(file, file_path)

    def _dowload_file(self, file_path: str) -> DownloadStatus:
        if self._has_item(file_path):
            return DownloadStatus.ALREADY

        content = self.datasource.download_file(file_path)

        self._add_item(file_path, content)

        return DownloadStatus.SUCCESS

    def _filter_directory_content(
        self, datetime_ini: datetime, datetime_fin: datetime, files: list[str]
    ) -> list[str]:
        files_in_range: list[str] = []

        for file in files:
            basename: str = os.path.basename(file)
            if not self.locator.match(basename):
                continue

            ct = self.locator.get_datetime(file)

            if datetime_ini <= ct <= datetime_fin:
                files_in_range.append(file)

        return files_in_range

    def _get_datetimes(
        self, start_time: str, end_time: str
    ) -> tuple[datetime, datetime]:
        if not start_time:
            raise ValueError("start_time must be provided")

        datetime_ini = datetime.strptime(start_time, self.date_format)

        if end_time:
            datetime_fin = datetime.strptime(end_time, self.date_format)
        else:
            datetime_fin = datetime_ini

        # Sometimes the files have a date and time with some seconds
        # sooner or later to the user required times. To overcome this
        # issue, we subtract and add 60 seconds to the initial and final
        # datetimes, respectively.
        datetime_ini -= timedelta(seconds=self.time_tolerance)
        datetime_fin += timedelta(seconds=self.time_tolerance)

        return datetime_ini, datetime_fin

    def _get_file_list(self, start_time: str, end_time: str = "") -> list[str]:
        if self.show_progress:
            print("Retrieving available file list")

        datetime_ini, datetime_fin = self._get_datetimes(start_time, end_time)

        paths = self.locator.get_paths(datetime_ini, datetime_fin)

        files = self._retrieve_directory_content(paths)

        return self._filter_directory_content(
            datetime_ini, datetime_fin, files
        )

    def _has_item(self, file_path: str) -> bool:
        return self.repository.is_file(file_path)

    def _retrieve_directory_content(self, paths: list[str]) -> list[str]:
        files: list[str] = []

        for path in paths:
            files.extend(self.datasource.list_files(path))

        return files

    def _retrieve_files(self, file_paths: list[str]) -> None:
        num_files = len(file_paths)
        num_len = len(f"{num_files}")
        padding = " ".rjust(2 * num_len + 2)

        if self.show_progress:
            print("Downloading files:")

        for i, file_path in enumerate(file_paths):
            if self.show_progress:
                num_item = f"{i + 1}".rjust(num_len)
                print(f"{num_item}/{num_files} {file_path}")

            result = self._dowload_file(file_path)

            if self.show_progress:
                if result == DownloadStatus.SUCCESS:
                    print(f"{padding}... downloaded succesfully")
                else:
                    print(f"{padding}... already downloaded")
