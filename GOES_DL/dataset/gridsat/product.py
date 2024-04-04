from dataclasses import dataclass

from ..product_base import ProductBase
from .constants import GRIDSAT_FILE_SUFFIX


@dataclass(eq=False, frozen=True)
class GridSatProduct(ProductBase):
    """
    Represent a product utility for GridSat dataset's product consumers.

    This class implements the `Product` interface for a generic GridSat
    dataset product utility. Instances of this class are responsible
    for verifying if a given filename matches the product filename
    pattern based on the dataset's naming conventions and product
    specifications, and for extracting the corresponding `datetime`
    information from the product's filename.

    Note: Currently, only the 'Geostationary IR Channel Brightness
    Temperature - GridSat B1' and the 'Geostationary Operational
    Environmental Satellites - GOES/CONUS' datasets's products are
    supported.

    Attributes
    ----------
    name : str
        The name of the GridSat dataset product. A dataset can have
        multiple products. E.g. "B1", "GOES". Due to how the GridSat
        dataset is structured, the name is always a single string.
    origin : list[str]
        The list of origins of the GridSat product, namely one or more
        satellite identifier, e.g. "goes08". Multi-origin data may set
        this attribute to an empty list.
    version : list[str]
        The version or list of versions of the GridSat product; e.g.
        "v01r01".
    date_format : str
        The specification of the date format used in the GridSat product
        filename.
    date_pattern : str
        The regex pattern of the date format used in the GridSat product
        filename.
    file_prefix : str
        The prefix for the GridSat product's filenames.
    file_suffix : str
        The suffix for the GridSat product's filenames.

    Methods
    -------
    get_date_format() -> str:
        Generate the date format for the GridSat product's filename.
    get_datetime(filename: str) -> datetime:
        Extracts the datetime from a GridSat product's filename.
        (inherited)
    get_prefix():
        Returns the prefix for the GridSat product's filename.
    get_suffix():
        Returns the suffix for the GridSat product's filename.
    get_timestamp_pattern() -> str:
        Returns the timestamp pattern for the product's filename.
    match(filename: str) -> bool:
        Checks if a given filename matches the GridSat product
        filename pattern. (inherited)
    """

    name: str
    origin: list[str]
    version: list[str]
    date_format: str
    date_pattern: str
    file_prefix: str

    def get_date_format(self) -> str:
        """
        Return the date format specification for the product's filename.

        Returns
        -------
        str
            The date format specification for the GridSat product's
            filename.
        """
        return self.date_format

    def get_prefix(self) -> str:
        """
        Generate the prefix for the GridSat dataset product's filename.

        Generates the prefix for the product's filename based on the
        dataset name and origin.

        Returns
        -------
        str
            The generated prefix for the filename.
        """
        sorted_origin: list[str] = sorted(self.origin)
        origin: str = f".(?:{'|'.join(sorted_origin)})" if self.origin else ""

        return f"{self.file_prefix}-{self.name}{origin}."

    def get_suffix(self) -> str:
        """
        Generate the suffix for the GridSat dataset product's filename.

        Generates the suffix for the product's filename based on the
        version and file suffix.

        Returns
        -------
        str
            The generated suffix for the filename.
        """
        sorted_version: list[str] = sorted(self.version)

        return f".(?:{'|'.join(sorted_version)}){GRIDSAT_FILE_SUFFIX}"

    def get_timestamp_pattern(self) -> str:
        """
        Return the timestamp pattern for the GridSat product's filename.

        Returns
        -------
        str
            The generated timestamp pattern for the filename.
        """
        return f"({self.date_pattern})"


if __name__ == "__main__":
    FILENAME_1: str = "GRIDSAT-B1.1980.01.01.00.v02r01.nc"
    FILENAME_2: str = "GRIDSAT-B1.2023.09.30.21.v02r01.nc"
    product: GridSatProduct = GridSatProduct(
        name="B1",
        origin=[],
        version=["v02r01"],
        file_prefix="GRIDSAT",
        date_format="%Y.%m.%d.%H",
        date_pattern=r"\d{4}\.\d{2}\.\d{2}\.\d{2}",
    )
    print(product)
    print(product.match(FILENAME_1))
    print(product.get_datetime(FILENAME_1))
    print(product.match(FILENAME_2))
    print(product.get_datetime(FILENAME_2).astimezone())
