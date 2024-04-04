from dataclasses import dataclass
from datetime import datetime, timezone
from re import Match, findall, fullmatch

from ..product import Product
from .constants import GOESR_FILE_SUFFIX


@dataclass(eq=False, frozen=True)
class GOESProduct(Product):

    name: str
    level: str
    scene: str
    instrument: str
    mode: list[str]
    channel: list[str]
    origin: str
    date_format: str
    date_pattern: str
    file_suffix: str = GOESR_FILE_SUFFIX

    def get_datetime(self, filename: str) -> datetime:
        """
        Extract the `datetime` from the product's filename.

        This method parses the given filename and extracts the
        corresponding `datetime` object from the product's filename
        using the dataset's date/time format conventions.

        Parameters
        ----------
        filename : str
            The filename from which to extract the `datetime`.

        Returns
        -------
        datetime:
            The `datetime` extracted from the filename.

        Raises
        ------
        ValueError
            If the filename does not match the expected pattern.
        """
        pattern: str = self.get_filename_pattern()
        matches: list[str] = findall(pattern, filename)

        if len(matches) != 1:
            raise ValueError(f"Incompatible product filename: '{filename}'")

        return self.timestamp_to_datetime(matches[0])

    def get_filename_pattern(self) -> str:
        """
        Generate a regular expression pattern for the product's filename.

        Generates a filename regex pattern based on the prefix, date
        pattern, and suffix.

        Returns
        -------
        str
            The generated filename pattern.
        """
        prefix: str = self.get_prefix()
        suffix: str = self.get_suffix()
        timestamp_pattern: str = self.get_timestamp_pattern()

        return f"{prefix}{timestamp_pattern}{suffix}"

    def get_prefix(self) -> str:
        """
        Generate the prefix for the product's filename.

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
        Generate the product prefix for the product's filename.

        Returns
        -------
        str
            The generated product prefix for the filename.
        """
        product_id: str = f"_{self.level}_{self.name}{self.scene}"

        return f"{self.instrument}{product_id}"

    def get_scan_band(self) -> str:
        """
        Generate the scan band for the product's filename.

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
        Generate the suffix for the product's filename.

        Generates the suffix for the product's filename based on the
        version and file suffix.

        Returns
        -------
        str
            The generated suffix for the filename.
        """
        return self.file_suffix

    def get_timestamp_pattern(self) -> str:
        """
        Generate the timestamp pattern for the product's filename.

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

    def match(self, filename: str) -> bool:
        """
        Verify the format of a provided filename.

        Checks if the provided filename matches the dataset product
        filename pattern for the dataset product.

        Parameters
        ----------
        filename : str
            The filename to match against the pattern.

        Returns
        -------
        bool
            True if the filename matches the pattern, False otherwise.
        """
        pattern: str = self.get_filename_pattern()
        match: Match[str] | None = fullmatch(pattern, filename)

        return match is not None

    def timestamp_to_datetime(self, timestamp: str) -> datetime:
        """
        Convert a timestamp to a datetime object.

        Converts the provided timestamp string to a datetime object in
        UTC timezone.

        Parameters
        ----------
        timestamp : str
            The timestamp string to convert to a datetime object.

        Returns
        -------
        datetime
            The converted datetime object in UTC timezone.

        Raises
        ------
        ValueError
            The framework raises an exception if the timestamp does not
            match the expected format or if the format specification is
            ill-formed (which is, indeed, a bug!).
        """
        # File dates are always in UTC.
        file_timestamp: str = f"{timestamp}+0000"
        file_date_format: str = f"{self.date_format}%z"
        file_date: datetime = datetime.strptime(
            file_timestamp, file_date_format
        )

        return file_date.astimezone(timezone.utc)
