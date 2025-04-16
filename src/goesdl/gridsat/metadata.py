from typing import Any

from ..netcdf import HasStrHelp
from ..utils.array import ArrayFloat32

NA = "not available"


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
        self.shape = getattr(metadata, "shape", NA)


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


class MeasurementMetadata(ContentMetadata):
    coordinates: str
    range: ArrayFloat32

    def __init__(self, metadata: Any) -> None:
        super().__init__(metadata)

        self.coordinates = getattr(metadata, "coordinates", NA)
        self.range = getattr(metadata, "range", NA)


class TimeMetadata(CoordinateMetadata):
    calendar: str

    def __init__(self, metadata: Any) -> None:
        super().__init__(metadata)

        self.calendar = getattr(metadata, "calendar", NA)

    MeasurementMetadata