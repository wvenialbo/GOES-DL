"""
Define the class for the downloader object.

The downloader object is responsible for downloading files from a
specified location using a datasource and product locator.

Classes
-------
Downloader
    Represent a downloader object.
"""

import os
from dataclasses import dataclass
from datetime import datetime, timedelta

from ..dataset import ProductLocator
from ..datasource import Datasource
from ..datasource.constants import DownloadStatus
from .constants import (
    ISO_TIMESTAMP_FORMAT,
    TIME_TOLERANCE_DEFAULT,
    TIME_TOLERANCE_MAX,
    TIME_TOLERANCE_MIN,
)


@dataclass(eq=False, frozen=True)
class Downloader:
    """
    Represent a downloader object.

    The downloader object is responsible for downloading files from a
    datasource. It receives a `Datasource` object, a `ProductLocator`
    object, and a date format specification string as input, and
    provides methods to download files from the datasource that match
    the timestamps between a start and end time.

    The downloader object is agnostic to the datasource, dataset, and
    dataset's product implementations. It only requires that the
    datasource and product locator objects implement the methods
    specified in the `GOES_DL.datasource.Datasource`,
    `GOES_DL.dataset.ProductLocator` and `GOES_DL.dataset.Product`
    interfaces.

    Attributes
    ----------
    datasource : Datasource
        A reference to the datasource object.
    locator : ProductLocator
        A reference to the dataset's product locator object.
    date_format : str
        The date format specification. The default is the ISO timestamp
        format.
    show_progress : bool
        A flag to show the progress of the download. The default is
        True, to display the progress.
    time_tolerance : int
        The time tolerance in seconds. The default is 60 seconds.

    Methods
    -------
    download_files(start_time: str, end_time: str = "")
        Download files from the datasource into the local repository.
    get_files(start_time: str, end_time: str = "")
        Load a list of files from the datasource or local repository.
    list_files(start_time: str, end_time: str = "")
        List the files that can be retrieved from the datasource.
    """

    datasource: Datasource
    locator: ProductLocator
    date_format: str = ISO_TIMESTAMP_FORMAT
    show_progress: bool = True
    time_tolerance: int = TIME_TOLERANCE_DEFAULT

    def __post_init__(self) -> None:
        """
        Validate the downloader object.
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
        end : str, optional
            The end time in the format specified by the `date_format`
            attribute. The default is "", in which case `end_time` is
            set equal to `start_time`.

        Returns
        -------
        list[str]
            A list of file path and names with respect to the local
            repository root directory.

        Raises
        ------
        ValueError
            If the start_time is not provided. The framework raises an
            exception if the provided timestamps do not match the
            expected format or if the timestamp format specification is
            ill-formed (which is, indeed, a bug!).
        RuntimeError
            The framework may raise if the file cannot be retrieved,
            e.g. if the file does not exist in the datasource or an
            internal error occurred.
        """
        files_in_range: list[str] = self._get_file_list(start, end)

        self._retrieve_files(files_in_range)

        return files_in_range

    def get_files(self, *, file_paths: list[str]) -> list[str]:
        """
        Load a list of files from the datasource or local repository.

        Load the files in the `file_paths` list from the datasource or
        local repository. If the file is not in the local repository, it
        is retrieved from the datasource and saved in the local
        repository.

        Note that `start` must be always provided. An offset of 60
        seconds is added to the initial datetime and subtracted from the
        final datetime to account for possible differences in the files'
        timestamps.

        Parameters
        ----------
        file_paths : list[str]
            A list with the file paths.

        Returns
        -------
        tuple[list[bytes], list[str]]
            A tuple with the list of file objects and the list of file
            path and names with respect to the local repository root
            directory.

        Raises
        ------
        ValueError
            If the start_time is not provided. The framework raises an
            exception if the provided timestamps do not match the
            expected format or if the timestamp format specification is
            ill-formed (which is, indeed, a bug!).
        RuntimeError
            The framework may raise if the file cannot be retrieved,
            e.g. if the file does not exist in the datasource or an
            internal error occurred.
        """
        self._retrieve_files(file_paths)

        return file_paths

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
        end : str, optional
            The end time in the format specified by the `date_format`
            attribute. The default is "", in which case `end_time` is
            set equal to `start_time`.

        Returns
        -------
        list[str]
            A list of file path and names with respect to the local
            repository root directory.

        Raises
        ------
        ValueError
            If the start_time is not provided. The framework raises an
            exception if the provided timestamps do not match the
            expected format or if the timestamp format specification is
            ill-formed (which is, indeed, a bug!).
        RuntimeError
            The framework may raise if the file cannot be retrieved,
            e.g. if the file does not exist in the datasource or an
            internal error occurred.
        """
        return self._get_file_list(start, end)

    def _filter_directory_content(
        self, datetime_ini: datetime, datetime_fin: datetime, files: list[str]
    ) -> list[str]:
        """
        Filter the files in the directory.

        Filter the files in the directory by the timestamps of the
        files. The files are filtered by the timestamps between the
        `datetime_ini` and `datetime_fin`.

        Parameters
        ----------
        datetime_ini : datetime
            The initial datetime.
        datetime_fin : datetime
            The final datetime.
        files : list[str]
            A list with the files in the directory.

        Returns
        -------
        list[str]
            A list with the files in the directory that match the
            timestamps between `datetime_ini` and `datetime_fin`.
        """
        files_in_range: list[str] = []

        for file in files:
            basename: str = os.path.basename(file)
            if not self.locator.match(basename):
                continue

            ct: datetime = self.locator.get_datetime(file)

            if datetime_ini <= ct <= datetime_fin:
                files_in_range.append(file)

        return files_in_range

    def _get_datetimes(
        self, start_time: str, end_time: str
    ) -> tuple[datetime, datetime]:
        """
        Get the datetime objects from the start and end times.

        Get the initial and final datetimes from `start_time` and
        `end_time`. `start_time` must be always provided. An offset of
        60 seconds is added to the initial datetime and subtracted from
        the final datetime to account for possible differences in the
        files' timestamps.

        Parameters
        ----------
        start_time : str
            The start time in the format specified by the date_format
            attribute.
        end_time : str
            The end time in the format specified by the date_format
            attribute. If it is set to "", `end_time` is set equal to
            `start_time`.

        Returns
        -------
        tuple[datetime, datetime]
            A tuple with the initial and final datetimes.

        Raises
        ------
        ValueError
            If `start_time` is not provided. The framework raises
            an exception if the provided timestamps do not match the
            expected format or if the timestamp format specification
            is ill-formed (which is, indeed, a bug!).
        """
        if not start_time:
            raise ValueError("start_time must be provided")

        datetime_ini: datetime = datetime.strptime(
            start_time, self.date_format
        )

        if end_time:
            datetime_fin: datetime = datetime.strptime(
                end_time, self.date_format
            )
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
        """
        Get the list of files in the directory.

        Get the list of files in the directory that match the timestamps
        between `start_time` and `end_time`, inclusive, from the data
        source. The list is filtered by the timestamps of the files;
        only files in the requested range are returned.

        Note that `start_time` must be always provided. An offset of 60
        seconds is added to the initial datetime and subtracted from the
        final datetime to account for possible differences in the files'
        timestamps.

        Parameters
        ----------
        start_time : str
            The start time in the format specified by the date_format
            attribute.
        end_time : str, optional
            The end time in the format specified by the date_format
            attribute. The default is "", in which case `end_time` is
            set equal to `start_time`.

        Returns
        -------
        list[str]
            A list with the files in the directory that match the
            timestamps between `start_time` and `end_time`.

        Raises
        ------
        ValueError
            If `start_time` is not provided. The framework raises
            an exception if the provided timestamps do not match the
            expected format or if the timestamp format specification
            is ill-formed (which is, indeed, a bug!).
        """
        if self.show_progress:
            print("Retrieving available file list")

        datetime_ini: datetime
        datetime_fin: datetime
        datetime_ini, datetime_fin = self._get_datetimes(start_time, end_time)

        paths: list[str] = self.locator.get_paths(datetime_ini, datetime_fin)

        files: list[str] = self._retrieve_directory_content(paths)

        return self._filter_directory_content(
            datetime_ini, datetime_fin, files
        )

    def _retrieve_directory_content(self, paths: list[str]) -> list[str]:
        """
        Retrieve the content of the directories.

        Retrieve the content of the directories specified by the `paths`
        list from the datasource.

        Parameters
        ----------
        paths : list[str]
            A list with the paths to the directories.

        Returns
        -------
        list[str]
            A list with the files in the directories.
        """
        files: list[str] = []

        for path in paths:
            files.extend(self.datasource.listdir(path))

        return files

    def _retrieve_files(self, file_paths: list[str]) -> None:
        """
        Retrieve the files from the datasource.

        Retrieve the files from the datasource using the file paths
        provided in the `file_paths` list.

        Parameters
        ----------
        file_paths : list[str]
            A list with the file paths.

        Raises
        ------
        RuntimeError
            The framework may raise if the file cannot be retrieved,
            e.g. if the file does not exist in the datasource or an
            internal error occurred.
        """
        num_files = len(file_paths)
        num_len = len(f"{num_files}")
        padding = " ".rjust(2 * num_len + 2)

        if self.show_progress:
            print("Downloading files:")

        for i, file in enumerate(file_paths):
            if self.show_progress:
                num_item = f"{i + 1}".rjust(num_len)
                print(f"{num_item}/{num_files} {file}")

            result = self.datasource.download_file(file)

            if self.show_progress:
                if result == DownloadStatus.SUCCESS:
                    print(f"{padding}... downloaded succesfully")
                else:
                    print(f"{padding}... already downloaded")
