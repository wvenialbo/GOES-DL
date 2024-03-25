from .rs_imager_product import GOESRSImagerProduct


class GOESRSMultiBandProduct(GOESRSImagerProduct):
    # Available single-band products from the GOES-R Series's ABI
    # instrument:
    AVAILABLE_PRODUCT: dict[str, str] = {
        "MCMIP": "Multi-Band Cloud and Moisture Imagery",
        "ACHA2KM": "Cloud Top Height (2 km resolution)",
        "ACHA": "Cloud Top Height",
        "ACHP2KM": "Cloud Top Pressure (2 km resolution)",
        "ACHT": "Cloud Top Temperature",
        "ACM": "Clear Sky Mask",
        "ACTP": "Cloud Top Phase",
        "ADP": "Aerosol Detection",
        "AICE": "Ice Concentration and Extent",
        "AITA": "Ice Age and Thickness",
        "AOD": "Aerosol Optical Depth",
        "BRF": "Land surface Bidirectional Reflectance Factor",
        "CCL": "Cloud Cover Layers",
        "COD2KM": "Cloud Optical Depth (2 km resolution)",
        "COD": "Cloud Optical Depth",
        "CPS": "Cloud Particle Size",
        "CTP": "Cloud Top Pressure",
        "DSI": "Derived Stability Indices",
        "DSR": "Downward Shortwave Radiation",
        "FDC": "Fire (Hot Spot Characterization)",
        "FSC": "Fractional Snow Cover",
        "LSA": "Land Surface Albedo",
        "LST2KM": "Land Surface Temperature (2 km resolution)",
        "LST": "Land Surface Temperature",
        "LVMP": "Legacy Vertical Moisture Profile",
        "LVTP": "Legacy Vertical Temperature Profile",
        "RRQPE": "Rainfall Rate (Quantitative Precipitation Estimate)",
        "RSR": "Reflected Shortwave Radiation (Top-Of-Atmosphere)",
        "SST": "Sea Surface Temperature",
        "TPW": "Total Precipitable Water",
        "VAA": "Volcanic Ash (Detection and Height)",
    }

    # Available channels for the ABI instrument:
    AVAILABLE_CHANNEL: set[str] = {f"{cn:02d}" for cn in range(1, 17)}

    # Default level ID for the ABI instrument:
    DEFAULT_LEVEL_ID: str = "L2"

    # Default scan mode for the ABI instrument:
    DEFAULT_SCAN_MODE: str = "M6"

    ONLY_CF_SCENE: set[str] = {
        "AOD",
        "COD",
        "CTP",
        "RSR",
    }

    ONLY_F_SCENE: set[str] = {
        "AICE",
        "AITA",
        "COD2KM",
        "LST2KM",
        "RRQPE",
        "SST",
        "VAA",
    }

    ONLY_FM_SCENE: set[str] = {
        "ACHT",
    }

    CF_SCENE: set[str] = {"C", "F"}
    F_SCENE: set[str] = {"F"}
    FM_SCENE: set[str] = {"F", "M1", "M2"}

    def __init__(
        self,
        scene_id: str,
        product_id: str,
        origin_id: str,
    ) -> None:
        if product_id not in self.AVAILABLE_PRODUCT:
            available_product: list[str] = sorted(
                self.AVAILABLE_PRODUCT.keys()
            )
            raise ValueError(
                f"Invalid product_id: '{product_id}'. "
                f"Available product IDs: {available_product}"
            )

        for products, scenes in zip(
            [self.ONLY_CF_SCENE, self.ONLY_F_SCENE, self.ONLY_FM_SCENE],
            [self.CF_SCENE, self.F_SCENE, self.FM_SCENE],
        ):
            if product_id in products and scene_id not in scenes:
                raise ValueError(
                    f"Invalid scene_id: '{scene_id}' "
                    f"for product_id: '{product_id}'. "
                    f"Available scene IDs: {sorted(scenes)}"
                )

        super(GOESRSMultiBandProduct, self).__init__(
            scene_id,
            self.DEFAULT_SCAN_MODE,
            self.DEFAULT_LEVEL_ID,
            product_id,
            origin_id,
        )
