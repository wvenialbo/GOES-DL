from .rs_imager_product import GOESRSImagerProduct


class GOESRSSingleBandProduct(GOESRSImagerProduct):
    # Available single-band products from the GOES-R Series's ABI
    # instrument:
    AVAILABLE_PRODUCT: dict[str, str] = {
        "CMIP": "Cloud and Moisture Imagery",
        "Rad": "Radiance data",
        "DMW": "Derived Motion Winds",
        "DMWV": "Derived Motion WV Winds",
    }

    # Available channels for the ABI instrument:
    AVAILABLE_CHANNEL: set[str] = {f"{cn:02d}" for cn in range(1, 17)}

    # Default scan mode for the ABI instrument:
    DEFAULT_SCAN_MODE: str = "M6"

    DMW_PRODUCTS: set[str] = {"DMW", "DMWV"}
    DMW_CHANNELS: set[str] = {"02", "07", "08", "09", "10", "14"}
    DMWV_CHANNELS: set[str] = {"08"}

    def __init__(
        self,
        channel_id: str,
        scene_id: str,
        product_id: str,
        origin_id: str,
    ) -> None:
        if channel_id not in self.AVAILABLE_CHANNEL:
            available_channel: list[str] = sorted(list(self.AVAILABLE_CHANNEL))
            raise ValueError(
                f"Invalid channel_id: '{channel_id}'. "
                f"Available channel IDs: {available_channel}"
            )

        if product_id not in self.AVAILABLE_PRODUCT:
            available_product: list[str] = list(self.AVAILABLE_PRODUCT.keys())
            raise ValueError(
                f"Invalid product_id: '{product_id}'. "
                f"Available product IDs: {sorted(available_product)}"
            )

        for product, channels in zip(
            list(self.DMW_PRODUCTS),
            [self.DMW_CHANNELS, self.DMWV_CHANNELS],
        ):
            if product_id == product and channel_id not in channels:
                raise ValueError(
                    f"Invalid channel_id: '{channel_id}' "
                    f"for product_id: '{product_id}'. "
                    f"Available channel IDs: {sorted(channels)}"
                )

        level_id: str = "L1b" if product_id == "Rad" else "L2"

        super(GOESRSSingleBandProduct, self).__init__(
            scene_id,
            self.DEFAULT_SCAN_MODE,
            level_id,
            product_id,
            origin_id,
        )

        self._channel_id = channel_id
