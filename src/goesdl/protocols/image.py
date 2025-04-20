from typing import Protocol

from ..protocols.geodetic import GeodeticGrid, GeodeticRegion
from ..utils.array import ArrayBool, ArrayFloat32, MaskedFloat32


class SatImageData(Protocol):
    """
    A protocol for the image data extracted from the satellite dataset.

    Defines the structure of the image data, including the grid data,
    image array, mask array, raster data, and region of interest (ROI).

    Attributes
    ----------
    grid: GeodeticGrid
        The grid data extracted from the satellite dataset.
    image: ArrayFloat32
        A 2D array containing the sliced values of the image data.
    mask: ArrayBool
        A 2D array containing the mask of the image data.
    raster: MaskedFloat32
        A 2D array containing the masked values of the image data
        extracted from the satellite dataset.
    region: GeodeticRegion
        The defined geodetic region of interest (ROI).
    """

    @property
    def grid(self) -> GeodeticGrid:
        """
        The grid data extracted from the satellite dataset.

        See Also
        --------
        GeodeticGrid
            The protocol for geodetic grid data.
        """

    @property
    def image(self) -> ArrayFloat32:
        """
        A 2D array containing the sliced values of the image data.
        """

    @property
    def mask(self) -> ArrayBool:
        """
        A 2D array containing the mask of the image data.
        """

    raster: MaskedFloat32
    """
    A 2D array containing the masked values of the image data extracted
    from the satellite dataset.
    """

    @property
    def region(self) -> GeodeticRegion:
        """
        The defined geodetic region of interest (ROI).

        See Also
        --------
        GeodeticRegion
            The protocol for geodetic region data.
        """
