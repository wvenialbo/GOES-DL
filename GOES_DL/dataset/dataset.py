from abc import ABC, abstractmethod
from datetime import datetime

from ..datasource import Datasource
from .product import Product


class Dataset(ABC):
    """
    Abstract a generic dataset.

    This class defines the interface that all datasets. The dataset is
    responsible for generating a list of paths based on the initial and
    final datetimes. The paths are going to be generated for each day,
    hour, or whatever time interval the dataset is based on, between the
    initial and final datetimes. The final time is always included in
    the list.

    Methods
    -------
    get_datasource() -> Datasource:
        Get an instance of a concrete Datasource class.
    get_paths(datetime_ini: datetime, datetime_fin: datetime)
        -> list[str]:
        Generate a list of paths.
    get_product() -> Product:
        Get an instance of a Product class.
    """

    @abstractmethod
    def get_datasource(self) -> Datasource:
        """
        Get an object of a class implementing the Datasource interface.

        The returned instance is going to be used to list the contents
        of a directory in a remote location and to download files from
        that location. A dataset my be based on a local or remote
        location, and the Datasource object is going to abstract the
        access to that location. Also, a dataset may be available from
        different locations, the implementors of this interface should
        provide a way to configure the location of the appropriate
        source.

        Returns
        -------
        Datasource
            An instance of a class implementing the Datasource
            interface.
        """
        ...

    @abstractmethod
    def get_paths(
        self, datetime_ini: datetime, datetime_fin: datetime
    ) -> list[str]:
        """
        Generate a list of paths.

        Generate a list of paths based on the initial and final
        datetimes. The paths are going to be generated for each day,
        hour, or whatever time interval the dataset is based on, between
        the initial and final datetimes. The final time is always
        included in the list.

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
        ...

    @abstractmethod
    def get_product(self) -> Product:
        """
        Get an instance of a class implementing the Product interface.

        The returned instance is going to be used to extract the
        datetime from the dataset product filenames and to verify if a
        given filename matches the expected dataset product filename
        pattern based on the products requested by the user.

        Returns
        -------
        Product
            An instance of a class implementing the Product interface.
        """
        ...
