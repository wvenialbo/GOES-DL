from datetime import datetime
from typing import Type

from ...datasource import DatasourceAWS, DatasourceHTTP
from .constants import B1_DATASET_DATE_FORMAT, B1_DATASET_PATH_PREFIX
from .dataset import Datasource, GridSatDataset
from .product_b1 import GridSatProductB1


class GridSatDatasetB1(GridSatDataset):
    """
    Represent the GridSat-B1 dataset.

    This class implements the interface for the GridSat-B1 dataset. The
    dataset is responsible for generating a list of paths based on the
    initial and final datetimes. The paths are going to be generated for
    each year, between the initial and final datetimes. The final time
    is always included in the list.

    Parameters
    ----------
    product : GridSatProductB1
        The GridSat-B1 product class.
    datasource : str, optional
        The datasource identifier to use. The available datasources are
        "AWS" and "NOAA". The default is "AWS".

    Methods
    -------
    invalid_datasource(datasource: list[str]) -> str
        Check for unsupported datasources in a list of datasources.
    next_time(current_time: datetime) -> datetime
        Get the next time interval. GridSat-B1 dataset organises the
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
        "AWS": DatasourceAWS,
        "NOAA": DatasourceHTTP,
    }

    BASE_URL: dict[str, str] = {
        "AWS": "s3://noaa-cdr-gridsat-b1-pds/data/",
        "NOAA": "https://www.ncei.noaa.gov/data/geostationary-ir-"
        "channel-brightness-temperature-gridsat-b1/access/",
    }

    def __init__(
        self, product: GridSatProductB1, datasource: str = "AWS"
    ) -> None:
        """
        Initialise the GridSat-B1 dataset.

        Constructs a new GridSat-B1 dataset object.

        Parameters
        ----------
        product : GridSatProductB1
            The GridSat-B1 product class.
        datasource : str, optional
            The datasource identifier to use. The available datasources
            are "AWS" and "NOAA". The default is "AWS".

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

        super(GridSatDatasetB1, self).__init__(
            product=product,
            datasource=d_source,
            date_format=B1_DATASET_DATE_FORMAT,
            path_prefix=B1_DATASET_PATH_PREFIX,
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
        next_year = current_time.year + 1
        return current_time.replace(year=next_year)

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
            month=1, day=1, hour=0, minute=0, second=0, microsecond=0
        )
        end_time = datetime_fin.replace(
            month=1, day=1, hour=0, minute=0, second=0, microsecond=0
        )
        return start_time, end_time
