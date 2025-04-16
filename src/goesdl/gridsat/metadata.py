from typing import Any

from ..netcdf import HasStrHelp
from ..utils.array import ArrayFloat32


class VariableMetadata(HasStrHelp):
    long_name: str
    standard_name: str
    units: str
    content_type: str
    shape: tuple[int, ...]

    def __init__(self, metadata: Any) -> None:
        self.long_name = metadata.long_name
        self.standard_name = metadata.standard_name
        self.units = metadata.units
        self.content_type = metadata.content_type
        self.shape = metadata.shape


class CoordinateMetadata(VariableMetadata):
    axis: str

    def __init__(self, metadata: Any) -> None:
        super().__init__(metadata)

        self.axis = metadata.axis


class MeasurementMetadata(VariableMetadata):
    coordinates: str
    actual_range: ArrayFloat32

    def __init__(self, metadata: Any) -> None:
        super().__init__(metadata)

        self.coordinates = metadata.coordinates
        self.actual_range = metadata.actual_range
