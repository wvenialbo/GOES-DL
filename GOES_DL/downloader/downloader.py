import os
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any

from ..dataset import ProductLocator
from ..datasource import Datasource
from .constants import ISO_TIMESTAMP_FORMAT


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
    product_locator : ProductLocator
        A reference to the dataset's product locator object.
    date_format : str
        The date format specification. The default is the ISO timestamp
        format.
    time_tolerance : int
        The time tolerance in seconds. The default is 60 seconds.

    Methods
    -------
    get_files(start_time: str, end_time: str = "") -> list[Any]
        Get the files from the datasource.
    get_file_list(start_time: str, end_time: str = "") -> list[str]
        Get the list of files in the directory.
    retrieve_files(file_paths: list[str]) -> list[Any]
        Retrieve the files from the datasource.
    """

    datasource: Datasource
    locator: ProductLocator
    date_format: str = ISO_TIMESTAMP_FORMAT
    time_tolerance: int = 60

    def __post_init__(self) -> None:
        """
        Validate the downloader object.
        """
        assert self.time_tolerance >= 0

    def get_files(self, *, start: str, end: str = "") -> list[Any]:
        """
        Get the files from the datasource.

        Get the files from the datasource that match the timestamps
        between `start` and `end` times, inclusive. The list is filtered
        by the timestamps of the files; only files in the requested
        range are returned.

        Note that `start` must be always provided. An offset of 60
        seconds is added to the initial datetime and subtracted from the
        final datetime to account for possible differences in the files'
        timestamps.

        Parameters
        ----------
        start : str
            The start time in the format specified by the date_format
            attribute.
        end : str, optional
            The end time in the format specified by the date_format
            attribute. The default is "", in which case `end_time` is
            set equal to `start_time`.

        Returns
        -------
        list[Any]
            A list with the file objects.

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
        files_in_range: list[str] = self.get_file_list(start, end)

        return self.retrieve_files(files_in_range)

    def get_file_list(self, start_time: str, end_time: str = "") -> list[str]:
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
        datetime_ini: datetime
        datetime_fin: datetime
        datetime_ini, datetime_fin = self._get_datetimes(start_time, end_time)

        paths: list[str] = self.locator.get_paths(datetime_ini, datetime_fin)

        files: list[str] = self._retrieve_directory_content(paths)

        return self._filter_directory_content(
            datetime_ini, datetime_fin, files
        )

    def retrieve_files(self, file_paths: list[str]) -> list[Any]:
        """
        Retrieve the files from the datasource.

        Retrieve the files from the datasource using the file paths
        provided in the `file_paths` list.

        Parameters
        ----------
        file_paths : list[str]
            A list with the file paths.

        Returns
        -------
        list[Any]
            A list with the file objects.

        Raises
        ------
        RuntimeError
            The framework may raise if the file cannot be retrieved,
            e.g. if the file does not exist in the datasource or an
            internal error occurred.
        """
        file_objects: list[Any] = []

        for file in file_paths:
            file_object: Any = self.datasource.get_file(file)
            file_objects.append(file_object)

        return file_objects

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
