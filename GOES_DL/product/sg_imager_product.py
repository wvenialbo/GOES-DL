from datetime import datetime

from .sg_product import GOES2GProduct


class GOES2GImagerProduct(GOES2GProduct):
    # The only available product is equivalent to GOES-R Series's
    # Multi-band Cloud and Moisture Imagery Product (MCMIP).
    AVAILABLE_PRODUCT: dict[str, str] = {
        "MCMIP": "Multi-band Cloud and Moisture Imagery"
    }

    # Available scenes/domains from the GOES 2nd generation Imager
    # Products:
    #
    # NOTE: In its strictest sense, “contiguous United States” refers
    # to the lower 48 states in North America (including the District of
    # of Columbia), and “continental United States” refers to 49 states
    # (including Alaska and the District of Columbia).
    AVAILABLE_SCENE: dict[str, str] = {
        "F": "Full Disk",
        "C": "CONUS (Contiguous United States)",
    }

    # Available versions of the GOES 2nd generation Imager Products:
    AVAILABLE_VERSION: set[str] = {"v01"}

    # Mapping between scene IDs and scene names:
    SCENE_MAPPING: dict[str, str] = {
        "F": "GOES",
        "C": "CONUS",
    }

    def __init__(
        self, scene_id: str = "F", origin_id: str = "G08", version: str = "v01"
    ) -> None:
        if scene_id not in self.AVAILABLE_SCENE:
            available_scene = sorted(list(self.AVAILABLE_SCENE.keys()))
            raise ValueError(
                f"Invalid scene_id: {scene_id}. "
                f"Available scene IDs: {available_scene}"
            )

        if version not in self.AVAILABLE_VERSION:
            raise ValueError(
                f"Unsupported version: {version}. "
                f"Supported versions: {sorted(self.AVAILABLE_VERSION)}"
            )

        available_product: list[str] = list(self.AVAILABLE_PRODUCT.keys())
        product_id: str = available_product[0]

        super(GOES2GImagerProduct, self).__init__(product_id, origin_id)

        self._scene_id: str = scene_id
        self._version: str = version

    def __format__(self, format_spec: str) -> str:
        if format_spec == "scene":
            return self._scene_id
        if format_spec == "version":
            return self._version
        return super(GOES2GImagerProduct, self).__format__(format_spec)

    @staticmethod
    def _format_spec() -> list[str]:
        return super(
            GOES2GImagerProduct, GOES2GImagerProduct
        )._format_spec() + [
            "scene",
            "version",
        ]

    def _repr_stat(self) -> str:
        return (
            super(GOES2GImagerProduct, self)._repr_stat()
            + f",scene_id='{self._scene_id}',version='{self._version}'"
        )

    def _str_stat(self) -> str:
        return (
            f"{super(GOES2GImagerProduct, self)._str_stat()}\n"
            f"  Scene ID   : '{self._scene_id}'\n"
            f"  Version    : '{self.version}'"
        )

    def get_baseurl(self, timestamp: str) -> str:
        scene: str = self.SCENE_MAPPING[self.scene_id]
        date_obj: datetime = datetime.strptime(timestamp, "%Y%m%d%H%M%S")
        date: str = date_obj.strftime("%Y/%m")
        return (
            "https://www.ncei.noaa.gov/data/"
            f"gridsat-goes/access/{scene.lower()}/{date}"
        )

    def get_filename(self, timestamp: str) -> str:
        scene: str = self.SCENE_MAPPING[self.scene_id]
        origin: str = self.AVAILABLE_ORIGIN[self.origin_id]
        date_obj: datetime = datetime.strptime(timestamp, "%Y%m%d%H%M%S")
        date: str = date_obj.strftime("%Y.%m.%d.%H%M")
        return f"GridSat-{scene}.{origin.lower()}.{date}.{self.version}.nc"

    @property
    def scene_id(self) -> str:
        return self._scene_id

    @property
    def version(self) -> str:
        return self._version
