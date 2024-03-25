from .rs_single_band_product import GOESRSSingleBandProduct


class GOESRSCMIProduct(GOESRSSingleBandProduct):

    CMI_PRODUCT_ID = "CMIP"

    def __init__(
        self,
        channel_id: str = "13",
        scene_id: str = "F",
        origin_id: str = "G16",
    ) -> None:

        super(GOESRSCMIProduct, self).__init__(
            channel_id,
            scene_id,
            self.CMI_PRODUCT_ID,
            origin_id,
        )
