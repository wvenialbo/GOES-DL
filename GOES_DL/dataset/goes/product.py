from dataclasses import dataclass

from ..product_gg import ProductBaseGG
from .constants import GOESR_FILE_SUFFIX, GOESR_PRODUCT_DATE_FORMAT


@dataclass(eq=False, frozen=True)
class GOESProduct(ProductBaseGG):
    """
    Represent a product utility for GOES-R dataset's product consumers.

    This class implements the `Product` interface for a generic GOES-R
    dataset product utility by inheriting from the `ProductBaseGG`
    abstract class. The `GOESProduct` class defines the specifications
    and naming conventions for products in the GOES-R dataset, and
    serves as a base class for more specialised product utility classes.

    Instances of this class are responsible for verifying if a given
    filename matches the product filename pattern based on the dataset's
    naming conventions and product specifications, and for extracting
    the corresponding `datetime` information from the product's
    filename.

    Attributes
    ----------
    name : str
        The name of the GOES-R dataset product. Due to how the GOES-R
        dataset is structured, the name is always a single string.
    level : str
        The level of the GOES-R product, e.g. "L1b" or "L2".
    scene : str
        The scene of the GOES-R product, e.g. "F" or "C".
    instrument : str
        The instrument of the GOES-R product, e.g. "ABI" or "GLM".
    mode : list[str]
        The list of modes of the GOES-R product, e.g. "M3" or "M6".
    channel : list[str]
        The list of channels of the GOES-R product, e.g. "C08" or "C13".
    origin : list[str]
        The list of origins of the GOES-R product, namely one or more
        satellite identifier, e.g. "goes08". Multi-origin data may set
        this attribute to an empty list.
    date_pattern : str
        The regex pattern of the date format used in the GOES-R product
        filename.

    Methods
    -------
    get_date_format() -> str:
        Return the date format specification for the GOES-R product's
        filename.
    get_prefix() -> str:
        Generate the prefix for the GOES-R product's filename.
    get_product_prefix() -> str:
        Generate the product prefix for the GOES-R product's filename.
    get_scan_band() -> str:
        Generate the scan mode and channel number identifier part of the
        GOES-R product's filename.
    get_suffix() -> str:
        Generate the suffix for the GOES-R product's filename.
    get_timestamp_pattern() -> str:
        Return the timestamp pattern for the GOES-R product's filename.
    """

    name: str
    level: str
    scene: str
    instrument: str
    mode: list[str]
    channel: list[str]
    origin: str
    date_pattern: str

    def get_date_format(self) -> str:
        """
        Return the date format specification for the product's filename.

        Returns
        -------
        str
            The date format specification for the GOES-R product's
            filename.
        """
        return GOESR_PRODUCT_DATE_FORMAT

    def get_prefix(self) -> str:
        """
        Generate the prefix for the GOES-R product's filename.

        Generates the prefix for the product's filename based on the
        dataset name and origin.

        Returns
        -------
        str
            The generated prefix for the filename.
        """
        product_prefix: str = self.get_product_prefix()
        scan_band: str = self.get_scan_band()
        if scan_band:
            scan_band = f"_{scan_band}"
        origin: str = f"_{self.origin}"

        return f"{product_prefix}{scan_band}{origin}"

    def get_product_prefix(self) -> str:
        """
        Generate the product prefix for the GOES-R product's filename.

        Returns
        -------
        str
            The generated product prefix for the filename.
        """
        product_id: str = f"_{self.level}_{self.name}{self.scene}"

        return f"{self.instrument}{product_id}"

    def get_scan_band(self) -> str:
        """
        Generate the scan band for the GOES-R product's filename.

        Returns
        -------
        str
            The generated scan band for the filename.
        """
        sorted_modes: list[str] = sorted(self.mode)
        mode: str = f"(?:{'|'.join(sorted_modes)})" if self.mode else ""
        sorted_channels: list[str] = sorted(self.channel)
        channel: str = (
            f"(?:{'|'.join(sorted_channels)})" if self.channel else ""
        )

        return f"{mode}{channel}"

    def get_suffix(self) -> str:
        """
        Generate the suffix for the GOES-R product's filename.

        Generates the suffix for the product's filename based on the
        version and file suffix.

        Returns
        -------
        str
            The generated suffix for the filename.
        """
        return GOESR_FILE_SUFFIX

    def get_timestamp_pattern(self) -> str:
        """
        Return the timestamp pattern for the GOES-R product's filename.

        Note: The scan start time that appear in the filename is
        considered as a the date and time of the product.

        Returns
        -------
        str
            The generated timestamp pattern for the filename.
        """
        start_date: str = f"_s({self.date_pattern})"
        end_date: str = f"_e{self.date_pattern}"
        creation_date: str = f"_c{self.date_pattern}"

        return f"{start_date}{end_date}{creation_date}"
