from abc import abstractmethod
from dataclasses import dataclass
from datetime import datetime

from ..dataset import Dataset, Datasource, Product
from .product import GridSatProduct


@dataclass(eq=False, frozen=True)
class GridSatDataset(Dataset):
    """
    Abstract a GridSat generic dataset.

    This class implements the interface for a GridSat generic dataset.
    The dataset is responsible for generating a list of paths based on
    the initial and final datetimes. The paths are going to be generated
    for each day, hour, or whatever time interval the dataset is based
    on, between the initial and final datetimes. The final time is
    always included in the list.

    The class also provides access to the product class that is going to
    be used to extract the datetime from the dataset product filenames and
    to verify if a given filename matches the expected dataset product
    filename pattern based on the products requested by the user.

    Attributes
    ----------
    product : GridSatProduct
        The GridSat product class.
    datasource : Datasource
        The datasource class.
    date_format : str
        The date format used in the dataset.
    path_prefix : str
        The path prefix to the dataset directories.

    Methods
    -------
    get_datasource() -> Datasource:
        Get an instance of a concrete Datasource class.
    get_paths(datetime_ini: datetime, datetime_fin: datetime)
        -> list[str]:
        Generate a list of paths.
    get_product() -> Product:
        Get an instance of a GridSatProduct class.
    next_time(current_time: datetime) -> datetime
        Get the next time interval.
    normalize_times(datetime_ini: datetime, datetime_fin: datetime)
        -> tuple[datetime, datetime]
        Normalise the initial and final datetimes.
    """

    product: GridSatProduct
    datasource: Datasource
    date_format: str
    path_prefix: str

    def get_datasource(self) -> Datasource:
        """
        Get an instance of a concrete Datasource class.

        The returned instance is going to be used to list the contents
        of a directory in a remote location and to download files from
        that location.

        Returns
        -------
        Datasource
            An instance of a Datasource class.
        """
        return self.datasource

    def get_paths(
        self, datetime_ini: datetime, datetime_fin: datetime
    ) -> list[str]:
        """
        Generate a list of paths.

        Generate a list of paths based on the initial and final
        datetimes. The paths are going to be generated for each day,
        hour, or whatever time interval the dataset is based on,
        between the initial and final datetimes. The final time is
        always included in the list.

        Parameters
        ----------
        datetime_ini : datetime
            The initial datetime.
        datetime_fin : datetime
            The final datetime.

        Returns
        -------
        list[str]
            A list of paths to dataset directories containing the
            product files for the given time interval.
        """
        current_time: datetime
        end_time: datetime
        current_time, end_time = self.normalize_times(
            datetime_ini, datetime_fin
        )

        folder_paths: list[str] = []

        while current_time <= end_time:
            folder_path = current_time.strftime(self.date_format)
            folder_paths.append(f"{self.path_prefix}{folder_path}/")

            current_time = self.next_time(current_time)

        return folder_paths

    def get_product(self) -> Product:
        """
        Get an instance of a GridSatProduct class.

        The returned instance is going to be used to extract the
        datetime from the dataset product filenames and to verify if a
        given filename matches the expected dataset product filename
        pattern based on the products requested by the user.

        Returns
        -------
        Product
            An instance of a GridSatProduct class.
        """
        return self.product

    @abstractmethod
    def next_time(self, current_time: datetime) -> datetime:
        """
        Get the next time interval.

        Get the next time interval based on the current time interval.

        Parameters
        ----------
        current_time : datetime
            The current time interval.

        Returns
        -------
        datetime
            The next time interval.
        """
        ...

    @abstractmethod
    def normalize_times(
        self, datetime_ini: datetime, datetime_fin: datetime
    ) -> tuple[datetime, datetime]:
        """
        Normalise the initial and final datetimes.

        Normalise the initial and final datetimes to the nearest
        time interval based on the dataset. The initial datetime is
        normalised to the start of the time interval and the final
        datetime is normalised to the end of the time interval.

        Parameters
        ----------
        datetime_ini : datetime
            The initial datetime.
        datetime_fin : datetime
            The final datetime.

        Returns
        -------
        tuple[datetime, datetime]
            A tuple containing the normalised initial and final
            datetimes.
        """
        ...
