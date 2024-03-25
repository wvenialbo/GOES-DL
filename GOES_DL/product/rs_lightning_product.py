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

    def __init__(self, origin_id: str) -> None:
        instrument_id: str = self.SUPPORTED_INSTRUMENT[0]
        available_product: list[str] = list(self.AVAILABLE_PRODUCT.keys())
        product_id: str = available_product[0]
        level_id: str = self.LEVEL_MAPPING[product_id]

        super(GOESRSLightningProduct, self).__init__(
            level_id,
            product_id,
            instrument_id,
            origin_id,
        )
