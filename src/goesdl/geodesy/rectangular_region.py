from math import degrees, floor
from typing import Literal, cast

from numpy import arange, float32

from ..protocols.geodetic import CoordRange, RegionDomain, RegionExtent
from ..utils.array import ArrayFloat32

CenterType = tuple[float, float]
SizeType = tuple[float, float]
StepType = tuple[float, float]

DEFAULT_STEP: StepType = (2.0, 2.0)


class RectangularRegion:

    domain: RegionDomain

    xticks: ArrayFloat32
    yticks: ArrayFloat32

    def __init__(self, domain: RegionDomain) -> None:
        # Validate domain to ensure increasing order and non-empty ranges
        self.domain = self._validate_domain(domain)

        self.xticks, self.yticks = self._create_grid_ticks(
            domain, DEFAULT_STEP
        )

    @classmethod
    def from_central_point(
        cls,
        size: SizeType,
        centre_deg: CenterType,
        units: Literal["arcsec", "arcmin", "deg", "rad"] = "deg",
    ) -> "RectangularRegion":
        size = cls._validate_size(size)
        size_deg = cls._convert_size_to_deg(size, units)
        centre_deg = cls._validate_centre(centre_deg)

        width_deg, height_deg = size_deg
        lon_cen, lat_cen = centre_deg

        x_half = 0.5 * width_deg
        y_half = 0.5 * height_deg

        lons_deg = (lon_cen - x_half, lon_cen + x_half)
        lats_deg = (lat_cen - y_half, lat_cen + y_half)

        domain = lons_deg, lats_deg

        return cls(domain)

    def set_ticks(
        self,
        domain: RegionDomain | None = None,
        step: StepType | float | int = DEFAULT_STEP,
    ) -> None:
        domain = (
            self.domain if domain is None else self._validate_domain(domain)
        )
        step = self._validate_step(step)
        self.xticks, self.yticks = self._create_grid_ticks(domain, step)

    @staticmethod
    def _convert_size_to_deg(size: SizeType, units: str) -> SizeType:
        # Validate units parameter
        allowed_units = {"arcsec", "arcmin", "deg", "rad"}
        if units not in allowed_units:
            raise ValueError(
                f"Invalid units: '{units}'; "
                f"allowed units are: {', '.join(allowed_units)}"
            )

        size_deg: tuple[float, ...]
        if units == "arcmin":
            size_deg = tuple(value / 60.0 for value in size)
        elif units == "arcsec":
            size_deg = tuple(value / 3600.0 for value in size)
        elif units == "rad":
            size_deg = tuple(degrees(value) for value in size)
        else:
            # units must be "deg" based on the validation
            size_deg = size

        return cast(SizeType, size_deg)

    @staticmethod
    def _create_grid_ticks(
        domain: RegionDomain, step: StepType
    ) -> tuple[ArrayFloat32, ArrayFloat32]:
        (lon_min, lon_max), (lat_min, lat_max) = domain
        lon_step, lat_step = step
        lon_min = lon_step * floor(lon_min / lon_step)
        lon_max = lon_step * floor(lon_max / lon_step) + lon_step
        xticks = arange(lon_min, lon_max, lon_step).astype(float32)

        lat_min = lat_step * floor(lat_min / lat_step)
        lat_max = lat_step * floor(lat_max / lat_step) + lat_step
        yticks = arange(lat_min, lat_max, lat_step).astype(float32)

        return cast(ArrayFloat32, xticks), cast(ArrayFloat32, yticks)

    @staticmethod
    def _validate_centre(centre_deg: CenterType) -> CenterType:
        # Validate 'centre_deg' structure, types, and range

        # Check if centre_deg is a tuple of two elements
        if not (isinstance(centre_deg, tuple) and len(centre_deg) == 2):
            raise TypeError(
                "'centre_deg' must be a tuple of two "
                "numbers (longitude, latitude)"
            )

        # Unpack the central point coordinates
        lon_deg, lat_deg = centre_deg

        # Check if the unpacked elements are numbers (int or float)
        if not (
            isinstance(lon_deg, (int, float))
            and isinstance(lat_deg, (int, float))
        ):
            raise TypeError(
                "Longitude and latitude values in 'centre_deg' must be numbers"
            )

        # Convert to float if they are integers
        try:
            lon_deg, lat_deg = float(lon_deg), float(lat_deg)
        except (ValueError, TypeError) as error:
            raise TypeError(
                "Longitude and latitude values in 'centre_deg' "
                "must be convertible to float"
            ) from error

        # Validate the geographical range for longitude and latitude in degrees
        # Assuming standard geographical ranges for degrees
        if not -180.0 <= lon_deg <= 180.0:
            raise ValueError(
                f"Longitude ({lon_deg}) must be "
                "between -180.0 and 180.0 degrees"
            )

        if not -90.0 <= lat_deg <= 90.0:
            raise ValueError(
                f"Latitude ({lat_deg}) must be "
                "between -90.0 and 90.0 degrees"
            )

        return lon_deg, lat_deg

    @staticmethod
    def _validate_size(size: SizeType) -> SizeType:
        # Validate 'size' structure, types, and range

        # Check if extent is a tuple of two elements
        if not (isinstance(size, tuple) and len(size) == 2):
            raise TypeError(
                "'size' must be a tuple of two numbers (width, height)"
            )

        width, height = size  # Unpack the extent values

        # Check if the unpacked elements are numbers (int or float)
        if not (
            isinstance(width, (int, float))
            and isinstance(height, (int, float))
        ):
            raise TypeError(
                "Width and height values in 'size' must be numbers"
            )

        # Convert to float if they are integers
        try:
            width, height = float(width), float(height)
        except (ValueError, TypeError) as error:
            raise TypeError(
                "Width and height values in 'size' "
                "must be convertible to float"
            ) from error

        # Validate that both values are positive
        if width <= 0 or height <= 0:
            raise ValueError(
                "'size' values must be positive, "
                f"received: ({width}, {height})"
            )

        return width, height

    @staticmethod
    def _validate_domain(domain: RegionDomain) -> RegionDomain:
        # Validate outer tuple structure
        if not (isinstance(domain, tuple) and len(domain) == 2):
            raise TypeError("'domain' must be a tuple of two 'CoordLimits'")

        # Unpack outer tuple (lon_limits, lat_limits)
        lon_limits, lat_limits = domain

        # Validate inner tuple structures and types of their elements
        if not (
            isinstance(lon_limits, tuple)
            and len(lon_limits) == 2
            and isinstance(lon_limits[0], (int, float))
            and isinstance(lon_limits[1], (int, float))
        ):
            raise TypeError(
                "The first element of 'domain' must be a tuple of two "
                "numbers (lon_min, lon_max)"
            )

        if not (
            isinstance(lat_limits, tuple)
            and len(lat_limits) == 2
            and isinstance(lat_limits[0], (int, float))
            and isinstance(lat_limits[1], (int, float))
        ):
            raise TypeError(
                "The second element of 'domain' must be a tuple of two "
                "numbers (lat_min, lat_max)"
            )

        # Unpack inner tuples (now that we know their structure is
        # likely correct)
        lon_min, lon_max = lon_limits
        lat_min, lat_max = lat_limits

        # Ensure values are floats after unpacking (optional, but good
        # practice if float is strictly required). This also handles
        # potential conversion if int was provided.
        try:
            lon_min, lon_max = float(lon_min), float(lon_max)
            lat_min, lat_max = float(lat_min), float(lat_max)
        except (ValueError, TypeError) as error:
            raise TypeError(
                "All 'domain' values must be numbers convertible to float"
            ) from error

        # Validate order
        if lon_min >= lon_max:
            raise ValueError(
                "Longitude values in 'domain' must be in increasing "
                "order (lon_min < lon_max)"
            )

        if lat_min >= lat_max:
            raise ValueError(
                "Latitude values in 'domain' must be in increasing "
                "order (lat_min < lat_max)"
            )

        return (lon_min, lon_max), (lat_min, lat_max)

    @staticmethod
    def _validate_step(step: StepType | float | int) -> StepType:
        # Ensure we have a tuple of values
        if not isinstance(step, tuple):
            step = (step, step)

        # Validate tuple structure and types of their elements
        if not (
            len(step) == 2
            and isinstance(step[0], (int, float))
            and isinstance(step[1], (int, float))
        ):
            raise TypeError(
                "'step' must be a number or a tuple of two "
                "numbers (lon_step, lat_step)"
            )

        # Unpack inner tuples (now that we know their structure is
        # likely correct)
        lon_step, lat_step = step

        # Ensure values are floats after unpacking (optional, but good
        # practice if float is strictly required). This also handles
        # potential conversion if int was provided.
        try:
            lon_step, lat_step = float(lon_step), float(lat_step)
        except (ValueError, TypeError) as error:
            raise TypeError(
                "All 'step' values must be numbers convertible to float"
            ) from error

        # Validate positiveness
        if lon_step <= 0:
            raise ValueError(
                "Longitude increment in 'step' must be a positive number"
            )

        if lat_step <= 0:
            raise ValueError(
                "Latitude increment in 'step' must be a positive number"
            )

        return lon_step, lat_step

    @property
    def extent(self) -> RegionExtent:
        return self.lon_bounds + self.lat_bounds

    @property
    def lat_bounds(self) -> CoordRange:
        return self.domain[1]

    @property
    def lon_bounds(self) -> CoordRange:
        return self.domain[0]
