from GOES_DL.dataset.gridsat.constants import (
    B1_PRODUCT_DATE_FORMAT,
    B1_PRODUCT_DATE_PATTERN,
    B1_PRODUCT_LATEST_VERSION,
    B1_PRODUCT_NAME,
    B1_PRODUCT_ORIGIN,
    B1_PRODUCT_PREFIX,
)
from GOES_DL.dataset.gridsat.product import GridSatProduct


class GridSatProductB1(GridSatProduct):
    """
    Represent the GridSat-B1 dataset product filename checker.

    This class implements the interface for the GridSat-B1 dataset
    product filename checker. The checker is responsible for extracting
    the datetime from a dataset product filename and verifying if a
    given filename matches the expected pattern.

    The data in the GridSat-B1 dataset (Geostationary IR Channel
    Brightness Temperature - GridSat B1) products comes from different
    sources, so, the origin's name is not reflected in the product's
    filename but the product's version is. Also, only a global view of
    the Earth is available, so, no domain is implied. The product's
    filename pattern is as follows:

    'GRIDSAT-B1.yyyy.mm.dd.HH.version.nc';

    `version` is the product's version (e.g. 'v02r01'). `yyyy`, `mm`,
    `dd` and `HH` are the year, month, day, hour, respectively, fixed
    length and padded with zeros.

    Input is 3-hourly data from the International Satellite Cloud
    Climatology Project (ISCCP) with gridded 0.07°x0.07° spatial
    resolution that spans from 1980 to the present. Three total
    channels are available:

    - IR: CDR-quality infrared window (IRWIN) channel (near 11 μm);
    - WV: Infrared water vapor (IRWVP) channel (near 6.7 μm);
    - VIS: Visible channel (near 0.6 μm).

    For more information visit the following link and links therein:
    https://www.ncei.noaa.gov/products/gridded-geostationary-brightness-temperature

    Attributes
    ----------
    version : str | list[str], optional
        The version of the GridSat-B1 product; e.g., "v02r01".  The
        version may be a single version or a list of versions. Only
        the latest version is available in the public repository. The
        default is the latest version ("v02r01").

    Methods
    -------
    get_datetime(filename: str) -> datetime:
        Extracts the datetime from a GridSat-B1 product filename.
        (inherited)
    invalid_version(version: list[str]) -> str:
        Check for unsupported versions in a list of versions.
    match(filename: str) -> bool:
        Checks if a given filename matches the GridSat-B1 product
        filename pattern. (inherited)

    Raises
    ------
    ValueError
        If the provided version is not supported or unavailable.
    """

    # Available versions of the B1 dataset Products:
    AVAILABLE_VERSION: set[str] = {"v02r01"}

    def __init__(
        self, version: str | list[str] = B1_PRODUCT_LATEST_VERSION
    ) -> None:
        """
        Initialise a GridSat-B1 dataset product object.

        Constructs a new GridSat-B1 dataset product object.

        Parameters
        ----------
        version : str | list[str], optional
            The version of the GridSat-B1 product; e.g., "v02r01". The
            version may be a single version or a list of versions. Only
            the latest version is available in the public repository.

        Raises
        ------
        ValueError
            If the provided version is not supported or unavailable.
        """
        if isinstance(version, str):
            version = [version]

        if unsupported_version := self.invalid_version(version):
            raise ValueError(
                f"Unsupported version: {unsupported_version}. "
                f"Supported versions: {sorted(self.AVAILABLE_VERSION)}"
            )

        super().__init__(
            name=B1_PRODUCT_NAME,
            origin=B1_PRODUCT_ORIGIN,
            version=version,
            date_format=B1_PRODUCT_DATE_FORMAT,
            date_pattern=B1_PRODUCT_DATE_PATTERN,
            file_prefix=B1_PRODUCT_PREFIX,
        )

    def invalid_version(self, version: list[str]) -> str:
        """
        Check for unsupported or invalid versions.

        Verifies and returns the first unsupported version from a list
        of versions.

        Parameters
        ----------
        version : list[str]
            The list of versions to check for unsupported versions.

        Returns
        -------
        str
            The first unsupported version found in the list of versions.
            An empty string is returned if all versions are supported.
        """
        return next(
            (ver for ver in version if ver not in self.AVAILABLE_VERSION),
            "",
        )


if __name__ == "__main__":
    FILENAME_1: str = "GRIDSAT-B1.1980.01.01.00.v02r01.nc"
    FILENAME_2: str = "GRIDSAT-B1.2023.09.30.21.v02r01.nc"
    product: GridSatProductB1 = GridSatProductB1(version="v02r01")
    print(product)
    print(FILENAME_2.startswith(product.get_prefix()))
    print(FILENAME_2.endswith(product.get_suffix()))
    print(product.match(FILENAME_1))
    print(product.get_datetime(FILENAME_1))
    print(product.get_datetime(FILENAME_2).astimezone())
