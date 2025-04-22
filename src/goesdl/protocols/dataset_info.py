from datetime import datetime
from typing import Protocol


class DatasetInfo(Protocol):

    @property
    def database_name(self) -> str:
        """
        The database name.
        """

    @property
    def product_name(self) -> str:
        """
        The product name.
        """

    @property
    def dataset_name(self) -> str:
        """
        The dataset name.
        """

    @property
    def content_type(self) -> str:
        """
        The dataset content type.
        """

    @property
    def plaform_id(self) -> str:
        """
        The platform (satellite) identifier.
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
    def scene_id(self) -> str:
        """
        The scene identifier.
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
    def datetime_start(self) -> datetime:
        """
        The coverage start time.
        """

    @property
    def datetime_end(self) -> datetime:
        """
        The coverage start time.
        """

    @property
    def actual_time(self) -> datetime:
        """
        The image actual time.
        """

    @property
    def band_id(self) -> int:
        """
        The band identifier.
        """

    @property
    def band_wavelength(self) -> float:
        """
        The band central wavelength.
        """

    @property
    def spatial_resolution(self) -> float:
        """
        The spatial resolution in metres.
        """

    @property
    def radiometric_resolution(self) -> float:
        """
        The radiometric resolution in bits.
        """
