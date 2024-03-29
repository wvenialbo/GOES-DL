from datetime import datetime
from typing import Type

from ...datasource import DatasourceHTTP
from .constants import GOES_DATASET_DATE_FORMAT
from .dataset import Datasource, GridSatDataset
from .product_goes import GridSatProductGOES


class GridSatDatasetGOES(GridSatDataset):
    """
    Represent the GridSat-GOES dataset.

    This class implements the interface for the GridSat-GOES dataset.
    The dataset is responsible for generating a list of paths based on
    the initial and final datetimes. The paths are going to be generated
    for each month, between the initial and final datetimes. The final
    time is always included in the list.

    Parameters
    ----------
    product : GridSatProductGOES
        The GridSat-GOES product class.
    datasource : str, optional
        The datasource identifier to use. The only available datasource
        is "NOAA". The default is "NOAA".

    Methods
    -------
    invalid_datasource(datasource: list[str]) -> str
        Check for unsupported datasources in a list of datasources.
    next_time(current_time: datetime) -> datetime
        Get the next time interval. GridSat-GOES dataset organises the
        data by year.
    normalise_times(datetime_ini: datetime, datetime_fin: datetime)
        -> tuple[datetime, datetime]
        Normalise the initial and final datetimes.

    Raises
    ------
    ValueError
        If the provided datasource is not supported or unavailable.
    """

    AVAILABLE_DATASOURCE: dict[str, Type[Datasource]] = {
        "NOAA": DatasourceHTTP,
    }

    BASE_URL: dict[str, str] = {
        "NOAA": "https://www.ncei.noaa.gov/data/gridsat-goes/access/",
    }

    def __init__(
        self, product: GridSatProductGOES, datasource: str = "NOAA"
    ) -> None:
        """
        Initialise the GridSat-GOES dataset.

        Constructs a new GridSat-GOES dataset object.

        Parameters
        ----------
        product : GridSatProductGOES
            The GridSat-GOES product class.
        datasource : str, optional
            The datasource identifier to use. The only available
            datasource is "NOAA". The default is "NOAA".

        Raises
        ------
        ValueError
            If the provided datasource is not supported or unavailable.
        """
        if unsupported_datasource := self.invalid_datasource([datasource]):
            available_datasource: list[str] = sorted(
                self.AVAILABLE_DATASOURCE.keys()
            )
            raise ValueError(
                f"Unsupported datasource: {unsupported_datasource}. "
                f"Available datasources: {available_datasource}"
            )

        DataSource: Type[Datasource] = self.AVAILABLE_DATASOURCE[datasource]
        datasource_url: str = self.BASE_URL[datasource]
        d_source: Datasource = DataSource(datasource_url)

        GOES_DATASET_PATH_PREFIX = f"{product.name.lower()}/"

        super(GridSatDatasetGOES, self).__init__(
            product=product,
            datasource=d_source,
            date_format=GOES_DATASET_DATE_FORMAT,
            path_prefix=GOES_DATASET_PATH_PREFIX,
        )

    def invalid_datasource(self, datasource: list[str]) -> str:
        """
        Check for unsupported or invalid datasources.

        Verifies and returns the first unsupported datasource from a
        list of datasources.

        Parameters
        ----------
        datasource : list[str]
            The list of datasources to check for unsupported
            datasources.

        Returns
        -------
        str
            The first unsupported datasource found in the list of
            datasources. An empty string is returned if all datasources
            are supported.
        """
        return next(
            (ds for ds in datasource if ds not in self.AVAILABLE_DATASOURCE),
            "",
        )

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
        next_month = current_time.month + 1
        next_year = current_time.year
        if next_month > 12:
            next_month = 1
            next_year += 1
        return current_time.replace(year=next_year, month=next_month)

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
        start_time = datetime_ini.replace(
            day=1, hour=0, minute=0, second=0, microsecond=0
        )
        end_time = datetime_fin.replace(
            day=1, hour=0, minute=0, second=0, microsecond=0
        )
        return start_time, end_time
