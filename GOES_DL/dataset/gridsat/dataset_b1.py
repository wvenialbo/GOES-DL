from datetime import datetime
from typing import Type

from GOES_DL.dataset.gridsat.constants import (
    B1_DATASET_DATE_FORMAT,
    B1_DATASET_PATH_PREFIX,
)
from GOES_DL.dataset.gridsat.dataset import Datasource, GridSatDataset
from GOES_DL.dataset.gridsat.product_b1 import GridSatProductB1
from GOES_DL.datasource import DatasourceAWS, DatasourceHTTP


class GridSatDatasetB1(GridSatDataset):
    """
    Represent the GridSat-B1 dataset.

    This class implements the interface for the GridSat-B1 dataset. The
    dataset is responsible for generating a list of paths based on the
    initial and final datetimes. The paths are going to be generated for
    each year, between the initial and final datetimes. The final time
    is always included in the list.

    The data in the GridSat-B1 dataset (Geostationary IR Channel
    Brightness Temperature - GridSat B1) products comes from different
    sources and only a global view of the Earth is available, so, no
    domain is implied. Neither of them is reflected in the product's
    file path. The dataset is available from various services, for
    Amazon Web Services (AWS) and Google Cloud Platform (GCP), the
    product's file path pattern is as follows:

    'scheme://net-location/data/yyyy',

    where `scheme` identifies the protocol's scheme (e.g. 's3', 'gs'),
    `net-location` is the hostname (e.g. 'noaa-cdr-gridsat-b1-pds' for
    's3', and 'noaa-cdr-gridsat-b1' for 'gs'), and  `yyyy` is the year.

    The files are also hosted on the National Centers for Environmental
    Information (NCEI) servers, the product's file path pattern is as
    follows:

    'https://www.ncei.noaa.gov/data/path/access/yyyy';

    where `path` is the project's data files folder name, i.e.
    'geostationary-ir-channel-brightness-temperature-gridsat-b1',
    and `yyyy` is the year.

    Note: Currently, only the AWS datasource is supported.

    Input is 3-hourly data from the International Satellite Cloud
    Climatology Project (ISCCP) with gridded 0.07°x0.07° spatial
    resolution that spans from 1980 to the present. Three total
    channels are available:

    - IR: CDR-quality infrared window (IRWIN) channel (near 11 μm);
    - WV: Infrared water vapor (IRWVP) channel (near 6.7 μm);
    - VIS: Visible channel (near 0.6 μm).

    For more information visit the following link and links therein:
    https://www.ncei.noaa.gov/products/gridded-geostationary-brightness-temperature

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
    truncate_to_year(time: datetime) -> datetime
        Truncate the datetime to the current year.

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
        start_time = self.truncate_to_year(datetime_ini)
        end_time = self.truncate_to_year(datetime_fin)
        return start_time, end_time

    def truncate_to_year(self, time: datetime) -> datetime:
        """
        Truncate the datetime to the current year.

        The datetime is truncated to the start of the year.

        Parameters
        ----------
        time : datetime
            The datetime to round.

        Returns
        -------
        datetime
            The truncated datetime.
        """
        return time.replace(
            month=1, day=1, hour=0, minute=0, second=0, microsecond=0
        )
