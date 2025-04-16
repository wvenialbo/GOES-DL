from typing import Any

from numpy import empty, float32, int8

from ..netcdf import HasStrHelp
from ..utils.array import ArrayFloat32, ArrayInt8
from .constants import NA


class VariableMetadata(HasStrHelp):
    long_name: str
    standard_name: str
    comment: str
    units: str
    shape: tuple[int, ...]

    def __init__(self, metadata: Any) -> None:
        self.long_name = getattr(metadata, "long_name", NA)
        self.standard_name = getattr(metadata, "standard_name", NA)
        self.comment = getattr(metadata, "comment", NA)
        self.units = getattr(metadata, "units", NA)
        self.shape = getattr(metadata, "shape", (0,))


class ContentMetadata(VariableMetadata):
    content_type: str

    def __init__(self, metadata: Any) -> None:
        super().__init__(metadata)

        self.content_type = getattr(metadata, "content_type", NA)


class CoordinateMetadata(ContentMetadata):
    axis: str

    def __init__(self, metadata: Any) -> None:
        super().__init__(metadata)

        self.axis = getattr(metadata, "axis", NA)


class FramedMetadata(ContentMetadata):
    coordinates: str

    def __init__(self, metadata: Any) -> None:
        super().__init__(metadata)

        self.coordinates = getattr(metadata, "coordinates", NA)


class MeasurementMetadata(FramedMetadata):
    range: ArrayFloat32

    def __init__(self, metadata: Any) -> None:
        super().__init__(metadata)

        self.range = getattr(metadata, "range", empty((0,), dtype=float32))


class TimeMetadata(CoordinateMetadata):
    calendar: str

    def __init__(self, metadata: Any) -> None:
        super().__init__(metadata)

        self.calendar = getattr(metadata, "calendar", NA)


class DeltaTimeMetadata(FramedMetadata):
    range: ArrayInt8

    def __init__(self, metadata: Any) -> None:
        super().__init__(metadata)

        self.range = getattr(metadata, "range", empty((0,), dtype=int8))
