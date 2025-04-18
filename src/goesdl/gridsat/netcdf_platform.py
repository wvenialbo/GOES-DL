from re import search

from ..netcdf import DatasetView, attribute
from .databook_gc import platform_origin_gridsat_gc


class PlatformMetadata(DatasetView):
    platform_domain: str = attribute("platform")

    @property
    def platform(self) -> str:
        return (
            match[0]
            if (match := search(r"GOES-\d{1,2}", self.platform_domain))
            else ""
        )

    @property
    def origin(self) -> str:
        return platform_origin_gridsat_gc[self.platform]
