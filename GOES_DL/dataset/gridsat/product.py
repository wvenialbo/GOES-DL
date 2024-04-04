from dataclasses import dataclass

from ..base import ProductBaseGG
from .constants import GRIDSAT_FILE_SUFFIX


@dataclass(eq=False, frozen=True)
class GridSatProduct(ProductBaseGG):
    """
    Represent a product utility for GridSat dataset's product consumers.

    This class implements the `Product` interface for a generic GridSat
    dataset product utility by inheriting from the `ProductBaseGG`
    abstract class. The class defines the specifications and naming
    conventions for products in the GridSat dataset, and serves as a
    base class for more specialised product utility classes.

    Also, the class provides the implementation of the abstract
    helper methods defined in the `ProductBaseGG` abstract class. The
    `GridSatProduct` class is the workhorse for all GridSat dataset
    products.

    `GridSatProduct` objects are responsible for verifying if a
    given filename matches the product filename pattern based on the
    dataset's naming conventions and product specifications, via the
    `match(filename)` method, and for extracting the corresponding
    `datetime` information from the product's filename by way of the
    `get_datetime(filename)` method.

    Notes
    -----
    Currently, the 'Geostationary IR Channel Brightness Temperature
    - GridSat B1' and the 'Geostationary Operational Environmental
    Satellites - GOES/CONUS' datasets's products are supported.

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

    Methods
    -------
    get_date_format() -> str:
        Return the date format specification for the GridSat product's
        filename.
    get_prefix() -> str:
        Generate the prefix for the GridSat product's filename.
    get_suffix() -> str:
        Generate the suffix for the GridSat product's filename.
    get_timestamp_pattern() -> str:
        Return the timestamp pattern for the GridSat product's filename.
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

        Generates and returns the date format specification for
        the product's filename based on the GridSat dataset product
        filename's date and time format conventions. The date format
        specification string is used to parse the product's filename
        and extract the `datetime` information.

        Returns
        -------
        str
            The date format specification for the GridSat product's
            filename.
        """
        return self.date_format

    def get_prefix(self) -> str:
        """
        Return the prefix for the product's filename.

        Generates and returns the prefix for the GridSat product's
        filename based on product-specific information like dataset
        and product's name, instrument and origin's identifier, etc.

        Returns
        -------
        str
            The prefix for the GridSat product's filename.
        """
        sorted_origin: list[str] = sorted(self.origin)
        origin: str = f".(?:{'|'.join(sorted_origin)})" if self.origin else ""

        return f"{self.file_prefix}-{self.name}{origin}."

    def get_suffix(self) -> str:
        """
        Return the suffix for the product's filename.

        Generates and returns the suffix for the product's filename
        based on product-specific information like product's version
        origin's identifier, and file suffix (extension).

        Returns
        -------
        str
            The suffix for the GridSat product's filename.
        """
        sorted_version: list[str] = sorted(self.version)

        return f".(?:{'|'.join(sorted_version)}){GRIDSAT_FILE_SUFFIX}"

    def get_timestamp_pattern(self) -> str:
        """
        Return the timestamp regex pattern for the product's filename.

        Generates and returns the timestamp regular expression
        pattern for the product's filename based on the dataset
        product filename's date and time format conventions. The
        timestamp regex pattern is used to extract the substring
        containing the timestamp from the product's filename
        before extracting the `datetime` information.

        Returns
        -------
        str
            The timestamp regex pattern for the GridSat product's
            filename.
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
