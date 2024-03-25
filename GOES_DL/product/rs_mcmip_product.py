from .rs_multi_band_product import GOESRSMultiBandProduct


class GOESRSMCMIProduct(GOESRSMultiBandProduct):

    MCMI_PRODUCT_ID = "MCMIP"

    def __init__(
        self,
        scene_id: str = "F",
        origin_id: str = "G16",
    ) -> None:

        super(GOESRSMCMIProduct, self).__init__(
            scene_id,
            self.MCMI_PRODUCT_ID,
            origin_id,
        )
