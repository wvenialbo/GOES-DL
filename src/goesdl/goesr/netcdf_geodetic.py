from cartopy.crs import Geostationary, Globe, PlateCarree, Projection
from netCDF4 import Dataset  # pylint: disable=no-name-in-module
from numpy import errstate
from numpy import max as np_max
from numpy import min as np_min
from numpy import nanmax, nanmin, nonzero, where
from numpy.ma import masked_invalid

from ..geodesy import (
    GeostationaryParameters,
    RectangularRegion,
    calculate_pixel_edges,
    geos_to_latlon_grid_goesdl,
)
from ..netcdf import HasStrHelp
from ..protocols.geodetic import IndexRange, RegionDomain
from ..utils.array import ArrayBool, ArrayFloat32, MaskedFloat32
from .netcdf_projection import GOESGeostationaryGrid, GOESImagerProjection

BoxLimits = tuple[int, int, int, int]


class GOESLatLonGrid(HasStrHelp):

    _region: RectangularRegion

    lon: ArrayFloat32
    lat: ArrayFloat32

    mask: ArrayBool

    lon_limits: IndexRange
    lat_limits: IndexRange

    crs: Projection

    geos: Projection

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
            lon_lat, limits = self._slice(record, region, delta, corners)
        # ...or extract the entire field of view
        else:
            lon_lat, limits = self._full_frame(record, corners)
            region = self._extract_region(lon_lat)

        self._region = region

        # Units: latitude in °N (°S < 0), longitude in °E (°W < 0)
        lon, lat = lon_lat

        self.lon, self.lat = lon.data, lat.data
        self.mask = lat.mask | lon.mask

        self.lon_limits, self.lat_limits = limits[:2], limits[2:4]

        # Create the source projection (Geostationary projection on
        # GRS80 ellipsoid)

        proj = GOESImagerProjection(record)

        source_globe = Globe(
            semimajor_axis=proj.semi_major_axis,
            semiminor_axis=proj.semi_major_axis,
            inverse_flattening=proj.inverse_flattening,
        )

        self.geos = Geostationary(
            central_longitude=proj.longitude_of_projection_origin,
            satellite_height=proj.perspective_point_height,
            sweep_axis=proj.sweep_angle_axis,
            globe=source_globe,
        )

        # Create the source projection (Platé-Carrée projection on GOES
        # ellipsoid)

        self.crs = PlateCarree(central_longitude=0.0, globe=source_globe)

    @classmethod
    def _extract(
        cls, record: Dataset, delta: int, limits: BoxLimits | None
    ) -> tuple[MaskedFloat32, MaskedFloat32]:
        return cls._extract_grid(record, delta, limits, False)

    @classmethod
    def _extract_bounds(
        cls, record: Dataset, limits: BoxLimits | None
    ) -> tuple[MaskedFloat32, MaskedFloat32]:
        return cls._extract_grid(record, 1, limits, True)

    @staticmethod
    def _extract_grid(
        record: Dataset, delta: int, limits: BoxLimits | None, bounds: bool
    ) -> tuple[MaskedFloat32, MaskedFloat32]:
        geos_grid = GOESGeostationaryGrid(record, delta, limits)

        if bounds:
            x_rad, y_rad = geos_grid.grid
            x_rad = calculate_pixel_edges(x_rad)
            y_rad = calculate_pixel_edges(y_rad)
            geos_grid.grid = (x_rad, y_rad)

        parameters = GeostationaryParameters(
            geos_grid.geometry, geos_grid.globe, geos_grid.grid
        )

        with errstate(invalid="ignore"):
            lat, lon = geos_to_latlon_grid_goesdl(parameters)

        lat: MaskedFloat32 = masked_invalid(lat)  # type: ignore
        lon: MaskedFloat32 = masked_invalid(lon)  # type: ignore

        return lon, lat

    @staticmethod
    def _extract_region(
        lon_lat: tuple[MaskedFloat32, MaskedFloat32],
    ) -> RectangularRegion:
        lon, lat = lon_lat

        # Create a rectangular region from the lon/lat arrays
        lon_min, lon_max = nanmin(lon), nanmax(lon)
        lat_min, lat_max = nanmin(lat), nanmax(lat)

        domain = (
            (float(lon_min), float(lon_max)),
            (float(lat_min), float(lat_max)),
        )

        return RectangularRegion(domain)

    @staticmethod
    def _find_limits(
        lon_lat: tuple[MaskedFloat32, MaskedFloat32],
        domain: RegionDomain,
        delta: int,
        offset: tuple[int, int],
    ) -> BoxLimits:
        (lon_min, lon_max), (lat_min, lat_max) = domain

        lon, lat = lon_lat

        segmented = where(
            (lon >= lon_min)
            & (lon <= lon_max)
            & (lat >= lat_min)
            & (lat <= lat_max),
            True,
            False,
        )

        y_indices, x_indices = nonzero(segmented)

        if not y_indices.size:
            raise ValueError("Region out of range, empty selection")

        x_min, x_max = np_min(x_indices), np_max(x_indices)
        y_min, y_max = np_min(y_indices), np_max(y_indices)

        x_offset, y_offset = offset

        return (
            int(x_min) * delta + x_offset,
            int(x_max + 1) * delta + x_offset,
            int(y_min) * delta + y_offset,
            int(y_max + 1) * delta + y_offset,
        )

    @classmethod
    def _full_frame(
        cls,
        record: Dataset,
        corners: bool,
    ) -> tuple[tuple[MaskedFloat32, MaskedFloat32], IndexRange, IndexRange]:
        # Extract the entire field of view
        lon_lat = cls._extract_grid(record, 1, None, corners)

        mat_shape = lon_lat[0].shape
        if corners:
            lon_limits = 0, mat_shape[1] - 1
            lat_limits = 0, mat_shape[0] - 1
        else:
            lon_limits = 0, mat_shape[1]
            lat_limits = 0, mat_shape[0]

        return lon_lat, lon_limits, lat_limits

    @classmethod
    def _slice(
        cls,
        record: Dataset,
        region: RectangularRegion,
        delta: int,
        corners: bool,
    ) -> tuple[tuple[MaskedFloat32, MaskedFloat32], BoxLimits]:
        lon_lat = cls._extract(record, delta, None)

        limits = cls._find_limits(lon_lat, region.domain, delta, (0, 0))

        if delta > 1:
            x_size, y_size = (
                record.variables["x"].size,
                record.variables["y"].size,
            )

            x_min, x_max = limits[:2]
            y_min, y_max = limits[2:4]

            x_min = max(x_min - delta, 0)
            y_min = max(y_min - delta, 0)

            x_max = min(x_max + delta, x_size)
            y_max = min(y_max + delta, y_size)

            limits = x_min, x_max, y_min, y_max

            offsets = x_min, y_min

            lon_lat = cls._extract(record, 1, limits)

            limits = cls._find_limits(lon_lat, region.domain, 1, offsets)

        if corners:
            lon_lat = cls._extract_bounds(record, limits)
        else:
            lon_lat = cls._extract(record, 1, limits)

        return lon_lat, limits

    @property
    def globe(self) -> Globe:
        return self.crs.globe

    @property
    def region(self) -> RectangularRegion:
        return self._region
