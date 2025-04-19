from collections.abc import Callable
from typing import Any, cast

from cartopy.crs import Globe, PlateCarree, Projection
from netCDF4 import Dataset  # pylint: disable=no-name-in-module
from numpy import concatenate, flatnonzero, float32, meshgrid

from ..geodesy import RectangularRegion
from ..netcdf import DatasetView, HasStrHelp, attribute, variable
from ..protocols.geodetic import IndexRange
from ..utils.array import ArrayFloat32
from .metadata import CoordinateMetadata, VariableMetadata

MetadataType = dict[str, CoordinateMetadata | VariableMetadata]


class GSLatLonData(HasStrHelp):
    lon: ArrayFloat32
    lat: ArrayFloat32


class GeodeticSummary(DatasetView):

    geospatial_lat_min: float32 = attribute()
    geospatial_lat_max: float32 = attribute()
    geospatial_lat_units: str = attribute()
    geospatial_lat_resolution: float32 = attribute()
    geospatial_lon_min: float32 = attribute()
    geospatial_lon_max: float32 = attribute()
    geospatial_lon_units: str = attribute()
    geospatial_lon_resolution: float32 = attribute()


class GSLatLonGrid(GSLatLonData):

    _region: RectangularRegion

    lon: ArrayFloat32
    lat: ArrayFloat32

    lon_limits: IndexRange
    lat_limits: IndexRange

    metadata: MetadataType

    crs: Projection

    summary: GeodeticSummary

    def __init__(
        self,
        record: Dataset,
        region: RectangularRegion | None = None,
        delta: int = 5,
        corners: bool = False,
    ) -> None:
        # Validate delta parameter (subsampling increment step)
        if not 1 <= delta <= 10:
            raise ValueError(
                "'delta' must be an integer between 1 and 10, inclusive"
            )

        # Extract the region of interest...
        if region:
            data, lon_limits, lat_limits = self._slice(
                record, region, delta, corners
            )

        # ...or extract the entire field of view
        else:
            region = self._extract_region(record)
            data, lon_limits, lat_limits = self._full_frame(record, corners)

        self._region = region

        self.lon, self.lat = meshgrid(data.lon, data.lat)

        self.lon_limits, self.lat_limits = lon_limits, lat_limits

        # Create the source projection (Platé-Carrée projection on GRS80
        # ellipsoid)

        source_globe = Globe(ellipse="GRS80")

        self.crs = PlateCarree(central_longitude=0.0, globe=source_globe)

        self.metadata = self._get_metadata(record)

        self.summary = GeodeticSummary(record)

    @staticmethod
    def _extract(
        record: Dataset,
        step: int | None,
        lon_limits: IndexRange | None,
        lat_limits: IndexRange | None,
    ) -> "GSLatLonData":
        def subsample(limits: IndexRange | None) -> Callable[[Any], Any]:
            def closure(x: Any) -> Any:
                begin, end = limits or (None, None)
                skip = step or None
                return x[begin:end:skip]

            return closure

        class _LatLonData(DatasetView):
            lon: ArrayFloat32 = variable("lon").data(
                filter=subsample(lon_limits)
            )
            lat: ArrayFloat32 = variable("lat").data(
                filter=subsample(lat_limits)
            )

        data = _LatLonData(record)

        return cast(GSLatLonData, data)

    @staticmethod
    def _extract_bounds(
        record: Dataset,
        lon_limits: IndexRange | None,
        lat_limits: IndexRange | None,
    ) -> "GSLatLonData":
        def subsample(limits: IndexRange | None) -> Callable[[Any], Any]:
            def closure(x: Any) -> Any:
                begin, end = limits or (None, None)
                coord = x[begin:end]
                return concatenate((coord[:, 0], coord[-1:, -1]))

            return closure

        class _LatLonData(DatasetView):
            lon: ArrayFloat32 = variable("lon_bounds").data(
                filter=subsample(lon_limits)
            )
            lat: ArrayFloat32 = variable("lat_bounds").data(
                filter=subsample(lat_limits)
            )

        data = _LatLonData(record)

        return cast(GSLatLonData, data)

    @staticmethod
    def _extract_bounds_metadata(
        record: Dataset, name: str
    ) -> VariableMetadata:
        coordinate = variable(name)

        class _LatLonMetata(DatasetView):
            long_name: str = coordinate.attribute()
            comment: str = coordinate.attribute()
            units: str = coordinate.attribute()
            shape: tuple[int] = coordinate.attribute()

        metadata = _LatLonMetata(record)

        return VariableMetadata(metadata)

    @staticmethod
    def _extract_metadata(record: Dataset, name: str) -> CoordinateMetadata:
        coordinate = variable(name)

        class _LatLonMetata(DatasetView):
            long_name: str = coordinate.attribute()
            standard_name: str = coordinate.attribute()
            units: str = coordinate.attribute()
            content_type: str = coordinate.attribute("coverage_content_type")
            axis: str = coordinate.attribute()
            shape: tuple[int] = coordinate.attribute()

        metadata = _LatLonMetata(record)

        return CoordinateMetadata(metadata)

    @staticmethod
    def _extract_region(record: Dataset) -> RectangularRegion:
        def subsample(x: Any) -> Any:
            skip = x.shape[0] - 1
            return x[::skip]

        class _LatLonData(DatasetView):
            lon: ArrayFloat32 = variable("lon").data(filter=subsample)
            lat: ArrayFloat32 = variable("lat").data(filter=subsample)

        data = _LatLonData(record)

        domain = (
            (float(data.lon[0]), float(data.lon[-1])),
            (float(data.lat[0]), float(data.lat[-1])),
        )

        return RectangularRegion(domain)

    @staticmethod
    def _find_limits(
        coord: ArrayFloat32,
        min_max: tuple[float, float],
        delta: int,
        offset: int,
    ) -> IndexRange:
        min_value, max_value = min_max

        if min_value > coord[-1] or max_value < coord[0]:
            raise ValueError(
                "Region out of range, empty selection: "
                f"[{min_value}, {max_value}] not in [{coord[0]}, {coord[-1]}]"
            )

        min_indices = flatnonzero(coord < min_value)
        min_bound = min_indices[-1] if min_indices.size > 0 else 0

        max_indices = flatnonzero(coord > max_value)
        max_bound = max_indices[0] if max_indices.size > 0 else -1
        max_bound = max_bound if max_bound >= 0 else coord.size

        return int(min_bound * delta + offset), int(max_bound * delta + offset)

    @classmethod
    def _full_frame(
        cls,
        record: Dataset,
        corners: bool,
    ) -> tuple["GSLatLonData", IndexRange, IndexRange]:
        if corners:
            data = cls._extract_bounds(record, None, None)
            lon_limits = 0, data.lon.size - 1
            lat_limits = 0, data.lat.size - 1
        else:
            data = cls._extract(record, None, None, None)
            lon_limits = 0, data.lon.size
            lat_limits = 0, data.lat.size

        return data, lon_limits, lat_limits

    @classmethod
    def _get_metadata(cls, record: Dataset) -> MetadataType:
        return {
            "lon": cls._extract_metadata(record, "lon"),
            "lat": cls._extract_metadata(record, "lat"),
            "lon_bounds": cls._extract_bounds_metadata(record, "lon_bounds"),
            "lat_bounds": cls._extract_bounds_metadata(record, "lat_bounds"),
        }

    @classmethod
    def _slice(
        cls,
        record: Dataset,
        region: RectangularRegion,
        delta: int,
        corners: bool,
    ) -> tuple["GSLatLonData", IndexRange, IndexRange]:
        data = cls._extract(record, delta, None, None)

        lon_limits = cls._find_limits(data.lon, region.lon_bounds, delta, 0)
        lat_limits = cls._find_limits(data.lat, region.lat_bounds, delta, 0)

        if delta > 1:
            lon_offset, lat_offset = lon_limits[0], lat_limits[0]

            data = cls._extract(record, None, lon_limits, lat_limits)

            lon_limits = cls._find_limits(
                data.lon, region.lon_bounds, 1, lon_offset
            )
            lat_limits = cls._find_limits(
                data.lat, region.lat_bounds, 1, lat_offset
            )

        if corners:
            data = cls._extract_bounds(record, lon_limits, lat_limits)
        else:
            data = cls._extract(record, None, lon_limits, lat_limits)

        return data, lon_limits, lat_limits

    @property
    def globe(self) -> Globe:
        return self.crs.globe

    @property
    def region(self) -> RectangularRegion:
        return self._region
