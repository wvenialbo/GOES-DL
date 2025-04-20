from ..netcdf import DatasetView, attribute
from .databook import origin_platform_goesr


class PlatformMetadata(DatasetView):
    platformID: str = attribute()

    @property
    def platform(self) -> str:
        return origin_platform_goesr[self.platformID]

    @property
    def origin(self) -> str:
        return self.platformID
