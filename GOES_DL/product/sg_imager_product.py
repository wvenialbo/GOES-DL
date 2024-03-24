from datetime import datetime

from .sg_product import GOES2GProduct


class GOES2GImagerProduct(GOES2GProduct):
    AVAILABLE_SCENE: dict[str, str] = {
        "F": "Full Disk",
        "C": "CONUS (Contiguous U.S.)",
    }
    AVAILABLE_VERSION: list[str] = ["1"]
    SCENE_MAPPING: dict[str, str] = {
        "F": "GOES",
        "C": "CONUS",
    }

    def __init__(
        self, origin_id: str, scene_id: str = "F", version: str = "1"
    ) -> None:
        super(GOES2GImagerProduct, self).__init__(origin_id)

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
            f"  Version    : 'v{int(self.version):02d}'"
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
        version: str = f"v{int(self.version):02d}"
        return f"GridSat-{scene}.{origin.lower()}.{date}.{version}.nc"

    @property
    def scene_id(self) -> str:
        return self._scene_id

    @property
    def version(self) -> str:
        return self._version
