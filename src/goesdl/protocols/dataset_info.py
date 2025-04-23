from datetime import datetime
from typing import Protocol


class DatasetInfo(Protocol):

    @property
    def database_name(self) -> str:
        """
        The database name.
        """

    @property
    def abstract(self) -> str:
        """
        The database abstract.
        """

    @property
    def product_name(self) -> str:
        """
        The product name.
        """

    @property
    def product_version(self) -> str:
        """
        The product version.
        """

    @property
    def summary(self) -> str:
        """
        The product summary.
        """

    @property
    def keywords(self) -> str:
        """
        The product keywords.
        """

    @property
    def dataset_name(self) -> str:
        """
        The dataset name.
        """

    @property
    def comment(self) -> str:
        """
        The dataset comment.
        """

    @property
    def content_type(self) -> str:
        """
        The dataset content type.
        """

    @property
    def plaform_name(self) -> str:
        """
        The platform (satellite) name.
        """

    @property
    def orbital_slot(self) -> str:
        """
        The orbital slot identifier.
        """

    @property
    def instrument_name(self) -> str:
        """
        The instrument name.
        """

    @property
    def scene_name(self) -> str:
        """
        The scene name.
        """

    @property
    def coverage_start(self) -> datetime:
        """
        The coverage start time.
        """

    @property
    def coverage_end(self) -> datetime:
        """
        The coverage start time.
        """

    @property
    def coverage_midpoint(self) -> datetime:
        """
        The mid-point between the start and end image scan.
        """

    @property
    def band_id(self) -> int:
        """
        The band identifier.
        """

    @property
    def band_description(self) -> str:
        """
        The band description.
        """

    @property
    def band_wavelength(self) -> float:
        """
        The band central wavelength.
        """

    @property
    def wavelength_units(self) -> str:
        """
        The wavelength units.
        """

    @property
    def spatial_resolution(self) -> float:
        """
        The spatial resolution in kilometres per pixel at nadir.
        """

    @property
    def radiometric_resolution(self) -> float:
        """
        The radiometric resolution in bits.
        """

    @property
    def standard_name(self) -> str:
        """
        The measurement field standard name.
        """

    @property
    def measurement_name(self) -> str:
        """
        The measurement field name.
        """

    @property
    def units(self) -> str:
        """
        The measurement field units.
        """

    @property
    def remarks(self) -> str:
        """
        Remarks about the measurement.
        """

    @property
    def valid_range(self) -> tuple[float, float]:
        """
        The valid range for the measurements.
        """

    @property
    def shape(self) -> tuple[int, ...]:
        """
        The dimesions of the image.
        """
