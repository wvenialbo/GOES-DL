from .rs_product import GOESRSProduct


class GOESRSImagerProduct(GOESRSProduct):
    # Supported instruments for the GOES-R series imager products:
    SUPPORTED_INSTRUMENT: list[str] = ["ABI"]

    # Available scenes/domains (sector/region) from the GOES 2nd
    # generation Imager Products:
    #
    # NOTE: In its strictest sense, “contiguous United States” refers
    # to the lower 48 states in North America (including the District of
    # of Columbia), and “continental United States” refers to 49 states
    # (including Alaska and the District of Columbia).
    AVAILABLE_SCENE: dict[str, str] = {
        "F": "Full Disk",
        "C": "CONUS (Continental United States)",
        "M1": "Mesoscale (Domain 1)",
        "M2": "Mesoscale (Domain 2)",
    }

    # Advanced Baseline Imager (ABI) Scan Modes:
    #
    # See: https://www.star.nesdis.noaa.gov/atmospheric-composition-
    #              training/satellite_data_abi_scan_modes.php
    AVAILABLE_SCAN_MODE: dict[str, str] = {
        "M3": "Mode 3 (Previous Flex Mode)",
        "M6": "Mode 6 (Current Flex Mode)",
    }

    def __init__(
        self,
        scene_id: str,
        scan_mode: str,
        level_id: str,
        product_id: str,
        origin_id: str,
    ) -> None:
        if scene_id not in self.AVAILABLE_SCENE:
            available_scene = list(self.AVAILABLE_SCENE.keys())
            raise ValueError(
                f"Invalid scene_id: {scene_id}. "
                f"Available scene IDs: {sorted(available_scene)}"
            )

        if scan_mode not in self.AVAILABLE_SCAN_MODE:
            available_scan_mode = list(self.AVAILABLE_SCAN_MODE.keys())
            raise ValueError(
                f"Invalid scan_mode: {scan_mode}. "
                f"Available scan modes: {sorted(available_scan_mode)}"
            )

        instrument_id: str = self.SUPPORTED_INSTRUMENT[0]

        super(GOESRSImagerProduct, self).__init__(
            level_id,
            product_id,
            instrument_id,
            origin_id,
        )

        self._scene_id: str = scene_id
        self._scan_mode: str = scan_mode
