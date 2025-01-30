"""
Provide locator for GOES-R Series imagery dataset's GLM products.

Classes:
    - GOESProductLocatorLCFA: GLM Lightning Cluster-Filter Algorithm
      (LCFA).
"""

from .locator_glm import GOESProductLocatorGLM


class GOESProductLocatorLCFA(GOESProductLocatorGLM):
    """
    Product locator for GOES-R Series imagery dataset's GLM products.

    Instrument: Geostationary Lightning Mapper (GLM).
    Product: Lightning Cluster-Filter Algorithm (LCFA).
    """

    PRODUCT_NAME: str = "LCFA"

    def __init__(self, origin: str) -> None:
        """
        Initialise a GOES-R Series imagery dataset LCFA product locator.

        Constructs a GOES-R Series imagery dataset LCFA product locator
        object.

        Parameters
        ----------
        origin : str
            The origin of the GOES-R Series dataset LCFA product, namely
            a satellite identifier, e.g. "G16". Due to how the dataset
            directories are organised, only a single origin may be
            provided.
        """
        super().__init__(name=self.PRODUCT_NAME, origin=origin)
