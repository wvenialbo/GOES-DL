from collections.abc import Callable
from typing import Any, cast

from cartopy.crs import Globe, PlateCarree, Projection
from netCDF4 import Dataset  # pylint: disable=no-name-in-module
from numpy import concatenate, flatnonzero, meshgrid

from ..geodesy import RectangularRegion
from ..netcdf import DatasetView, HasStrHelp, variable
from ..protocols.geodetic import IndexRange
from ..utils.array import ArrayFloat32
from .metadata import CoordinateMetadata, VariableMetadata

MetadataType = dict[str, CoordinateMetadata | VariableMetadata]


class _DatasetInfo(DatasetView):

    cdm_data_type: str


class GSLatLonData(HasStrHelp):
    lon: ArrayFloat32
    lat: ArrayFloat32


class GSLatLonGrid(GSLatLonData):

    region: RectangularRegion

    lon: ArrayFloat32
    lat: ArrayFloat32

    lon_limits: IndexRange
    lat_limits: IndexRange

    metadata: MetadataType

    crs: Projection

    def __init__(
        self,
        dataframe: Dataset,
        region: RectangularRegion | None = None,
        delta: int = 5,
        corners: bool = False,
    ) -> None:
        # Validate delta parameter (subsampling increment step)
        if not 1 <= delta <= 10:
            raise ValueError(
                "'delta' must be an integer between 1 and 10, inclusive"
            )

        info = _DatasetInfo(dataframe)

        self._validate_content_type(dataframe, info.cdm_data_type)
        self._validate_dimensions(dataframe)

        # Extract the region of interest...
        if region:
            data, lon_limits, lat_limits = self._slice(
                dataframe, region, delta, corners
            )

        # ...or extract the entire field of view
        else:
            region = self._extract_region(dataframe)
            data, lon_limits, lat_limits = self._full_frame(dataframe, corners)

        self.region = region

        self.lon, self.lat = meshgrid(data.lon, data.lat)

        self.lon_limits, self.lat_limits = lon_limits, lat_limits

        # Create the source projection (Platé-Carrée projection on GRS80
        # ellipsoid)

        source_globe = Globe(ellipse="GRS80")

        self.crs = PlateCarree(central_longitude=0.0, globe=source_globe)

        self.metadata = self._get_metadata(dataframe)

    @staticmethod
    def _extract(
        dataframe: Dataset,
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

        data = _LatLonData(dataframe)

        return cast(GSLatLonData, data)

    @staticmethod
    def _extract_bounds(
        dataframe: Dataset,
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

        data = _LatLonData(dataframe)

        return cast(GSLatLonData, data)

    @staticmethod
    def _extract_bounds_metadata(
        dataframe: Dataset, name: str
    ) -> VariableMetadata:
        coordinate = variable(name)

        class _LatLonMetata(DatasetView):
            long_name: str = coordinate.attribute()
            comment: str = coordinate.attribute()
            units: str = coordinate.attribute()
            shape: tuple[int] = coordinate.attribute()

        metadata = _LatLonMetata(dataframe)

        return VariableMetadata(metadata)

    @staticmethod
    def _extract_metadata(dataframe: Dataset, name: str) -> CoordinateMetadata:
        coordinate = variable(name)

        class _LatLonMetata(DatasetView):
            long_name: str = coordinate.attribute()
            standard_name: str = coordinate.attribute()
            units: str = coordinate.attribute()
            content_type: str = coordinate.attribute("coverage_content_type")
            axis: str = coordinate.attribute()
            shape: tuple[int] = coordinate.attribute()

        metadata = _LatLonMetata(dataframe)

        return CoordinateMetadata(metadata)

    @staticmethod
    def _extract_region(dataframe: Dataset) -> RectangularRegion:
        def subsample(x: Any) -> Any:
            skip = x.shape[0] - 1
            return x[::skip]

        class _LatLonData(DatasetView):
            lon: ArrayFloat32 = variable("lon").data(filter=subsample)
            lat: ArrayFloat32 = variable("lat").data(filter=subsample)

        data = _LatLonData(dataframe)

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
        dataframe: Dataset,
        corners: bool,
    ) -> tuple["GSLatLonData", IndexRange, IndexRange]:
        if corners:
            data = cls._extract_bounds(dataframe, None, None)
            lon_limits = 0, data.lon.size - 1
            lat_limits = 0, data.lat.size - 1
        else:
            data = cls._extract(dataframe, None, None, None)
            lon_limits = 0, data.lon.size
            lat_limits = 0, data.lat.size

        return data, lon_limits, lat_limits

    @classmethod
    def _get_metadata(cls, dataframe: Dataset) -> MetadataType:
        return {
            "lon": cls._extract_metadata(dataframe, "lon"),
            "lat": cls._extract_metadata(dataframe, "lat"),
            "lon_bounds": cls._extract_bounds_metadata(
                dataframe, "lon_bounds"
            ),
            "lat_bounds": cls._extract_bounds_metadata(
                dataframe, "lat_bounds"
            ),
        }

    @classmethod
    def _slice(
        cls,
        dataframe: Dataset,
        region: RectangularRegion,
        delta: int,
        corners: bool,
    ) -> tuple["GSLatLonData", IndexRange, IndexRange]:
        data = cls._extract(dataframe, delta, None, None)

        lon_limits = cls._find_limits(data.lon, region.lon_bounds, delta, 0)
        lat_limits = cls._find_limits(data.lat, region.lat_bounds, delta, 0)

        if delta > 1:
            lon_offset, lat_offset = lon_limits[0], lat_limits[0]

            data = cls._extract(dataframe, None, lon_limits, lat_limits)

            lon_limits = cls._find_limits(
                data.lon, region.lon_bounds, 1, lon_offset
            )
            lat_limits = cls._find_limits(
                data.lat, region.lat_bounds, 1, lat_offset
            )

        if corners:
            data = cls._extract_bounds(dataframe, lon_limits, lat_limits)
        else:
            data = cls._extract(dataframe, None, lon_limits, lat_limits)

        return data, lon_limits, lat_limits

    @staticmethod
    def _validate_content_type(dataframe: Dataset, content_type: str) -> None:
        if content_type != "Grid":
            raise ValueError(
                "Unexpected content type. "
                f"Expected 'Grid', got '{content_type}'"
            )

        for field_id in {"lat", "lon", "lat_bounds", "lon_bounds"}:
            if field_id not in dataframe.variables:
                raise ValueError(
                    f"Dataset does not have the required field '{field_id}'"
                )

    @staticmethod
    def _validate_dimensions(dataframe: Dataset) -> None:
        fields = ("lat", "lon", "lat_bounds", "lon_bounds")
        dims = (("lat",), ("lon",), ("lat", "nv"), ("lon", "nv"))
        for field, dim in zip(fields, dims):
            if dim != dataframe.variables[field].dimensions:
                raise ValueError(
                    f"Field '{field}' does not have "
                    f"the required dimensions ({dim})"
                )

    @property
    def globe(self) -> Globe:
        return self.crs.globe
