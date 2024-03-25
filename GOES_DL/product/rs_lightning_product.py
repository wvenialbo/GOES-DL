from datetime import datetime

from .rs_product import GOESRSProduct


class GOESRSLightningProduct(GOESRSProduct):
    # Supported instruments for this family of products:
    SUPPORTED_INSTRUMENT: list[str] = ["GLM"]

    # Available products from the GOES-R Series's Geostationary
    # Lightning Mapper:
    AVAILABLE_PRODUCT: dict[str, str] = {
        "LCFA": "Lightning Cluster-Filter Algorithm"
    }

    # Mapping between product IDs and level IDs:
    LEVEL_MAPPING: dict[str, str] = {
        "LCFA": "L2",
    }

    def __init__(self, origin_id: str, date_format: str = "") -> None:
        instrument_id: str = self.SUPPORTED_INSTRUMENT[0]
        available_product: list[str] = list(self.AVAILABLE_PRODUCT.keys())
        product_id: str = available_product[0]
        level_id: str = self.LEVEL_MAPPING[product_id]

        super(GOESRSLightningProduct, self).__init__(
            level_id, product_id, instrument_id, origin_id, date_format
        )

    def get_baseurl(self, timestamp: str) -> str:
        DATE_FORMAT: str = "%Y/%j/%H"
        date: datetime = datetime.strptime(timestamp, self._date_format)
        path = f"{self._get_base_id()}/{date.strftime(DATE_FORMAT)}"
        return f"https://noaa-goes16.s3.amazonaws.com/{path}/"

    def get_filename(
        self, time_start: str, time_end: str = "", time_create: str = ""
    ) -> str:
        start: str = self._date_to_timestamp(time_start)
        end: str = self._date_to_timestamp(time_end)
        create: str = self._date_to_timestamp(time_create)
        return f"OR_{self.get_file_id()}_s{start}_e{end}_c{create}.nc"

    def get_file_id(self) -> str:
        return f"{self._get_base_id()}_{self.origin_id}"

    def _get_base_id(self) -> str:
        return f"{self.instrument_id}-{self.level_id}-{self.product_id}"

    def _date_to_timestamp(self, timestamp: str) -> str:
        DATE_FORMAT: str = "%Y%j%H%M%S%f"
        date: datetime = datetime.strptime(timestamp, self._date_format)
        return date.strftime(DATE_FORMAT)[:-5]
