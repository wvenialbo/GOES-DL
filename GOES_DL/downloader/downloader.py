from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any

from ..dataset import Dataset, Product
from ..datasource import Datasource
from .constants import ISO_TIMESTAMP_FORMAT


@dataclass(eq=False, frozen=True)
class Downloader:
    """
    Represent a downloader object.

    The downloader object is responsible for downloading files from a
    datasource. It receives a `Datasource` object, a `Dataset` object,
    and a date format specification as input and provides methods to
    download files from the datasource that match the timestamps
    between a start and end time.

    The downloader object is agnostic to the datasource, dataset, and
    dataset's product implementations. It only requires that the
    datasource and dataset objects implement the methods specified in
    the `GOES_DL.datasource.Datasource`, `GOES_DL.dataset.Dataset` and
    `GOES_DL.dataset.Product` abstract class interfaces.

    Attributes
    ----------
    data_set : Dataset
        A reference to the dataset object.
    data_source : Datasource
        A reference to the datasource object.
    date_format : str
        The date format specification. The default is the ISO timestamp
        format.

    Methods
    -------
    get_files(start_time: str, end_time: str = "") -> list[Any]
        Get the files from the data source.
    get_file_list(start_time: str, end_time: str = "") -> list[str]
        Get the list of files in the directory.
    retrieve_files(file_paths: list[str]) -> list[Any]
        Retrieve the files from the data source.
    """

    data_set: Dataset
    data_source: Datasource
    date_format: str = ISO_TIMESTAMP_FORMAT

    def get_files(self, start_time: str, end_time: str = "") -> list[Any]:
        """
        Get the files from the data source.

        Get the files from the data source that match the timestamps
        between `start_time` and `end_time`, inclusive. The list is
        filtered by the timestamps of the files; only files in the
        requested range are returned.

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
        list[Any]
            A list with the file objects.

        Raises
        ------
        ValueError
            If the start_time is not provided. The framework raises
            an exception if the provided timestamps do not match the
            expected format or if the timestamp format specification
            is ill-formed (which is, indeed, a bug!).
        RuntimeError
            The framework may raise if the file cannot be retrieved,
            e.g. if the file does not exist in the data source or an
            internal error occurred.
        """
        files_in_range: list[str] = self.get_file_list(start_time, end_time)

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

        paths: list[str] = self.data_set.get_paths(datetime_ini, datetime_fin)

        files: list[str] = self._retrieve_directory_content(paths)

        return self._filter_directory_content(
            datetime_ini, datetime_fin, files
        )

    def retrieve_files(self, file_paths: list[str]) -> list[Any]:
        """
        Retrieve the files from the data source.

        Retrieve the files from the data source using the file paths
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
            e.g. if the file does not exist in the data source or an
            internal error occurred.
        """
        file_objects: list[Any] = []

        for file in file_paths:
            file_object = self.data_source.get_file(file)
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

        product: Product = self.data_set.get_product()

        for file in files:
            ct = product.get_datetime(file)
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

        datetime_ini = datetime.strptime(start_time, self.date_format)

        if end_time:
            datetime_fin = datetime.strptime(end_time, self.date_format)
        else:
            datetime_fin = datetime_ini

        # Sometimes the files have a date and time with some seconds
        # sooner or later to the user required times. To overcome this
        # issue, we subtract and add 60 seconds to the initial and final
        # datetimes, respectively.
        datetime_ini -= timedelta(seconds=60)
        datetime_fin += timedelta(seconds=60)

        return datetime_ini, datetime_fin

    def _retrieve_directory_content(self, paths: list[str]) -> list[str]:
        """
        Retrieve the content of the directories.

        Retrieve the content of the directories specified by the `paths`
        list from the data source.

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
            files.extend(self.data_source.listdir(path))

        return files
