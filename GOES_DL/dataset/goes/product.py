from dataclasses import dataclass

from ..product_base import ProductBase
from .constants import GOESR_FILE_SUFFIX, GOESR_PRODUCT_DATE_FORMAT


@dataclass(eq=False, frozen=True)
class GOESProduct(ProductBase):

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
