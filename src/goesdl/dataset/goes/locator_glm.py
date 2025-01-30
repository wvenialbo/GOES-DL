"""
Provide locator for GOES-R Series imagery dataset's GLM products.

Classes:
    - GOESProductLocatorGLM: All Geostationary Lightning Mapper (GLM)
      products.
"""

from .locator import GOESProductLocator


class GOESProductLocatorGLM(GOESProductLocator):
    """
    Product locator for GOES-R Series imagery dataset's GLM products.

    Instrument: Geostationary Lightning Mapper (GLM).
    Product: All GLM products.
    """

    AVAILABLE_PRODUCTS: dict[str, str] = {
        "LCFA": "Lightning Cluster-Filter Algorithm"
    }

    INSTRUMENT_NAME: str = "GLM"
    PRODUCT_LEVEL: str = "L2"

    def __init__(self, name: str, origin: str) -> None:
        """
        Initialise a GOES-R Series imagery dataset GLM product locator.

        Constructs a GOES-R Series imagery dataset GLM product locator
        object.

        Parameters
        ----------
        name : str
            The name of the GOES-R Series imagery dataset GLM product.
            Due to how the dataset directories are organised, only a
            single product can be provided.
        origin : str
            The origin of the GOES-R Series imagery dataset GLM product,
            namely a satellite identifier, e.g. "G16". Due to how the
            dataset directories are organised, only a single origin may
            be provided.

        Notes
        -----
        ValueError is raised if the provided product name is invalid.
        """
        self._validate_product(name, self.AVAILABLE_PRODUCTS)

        super().__init__(
            name=name,
            level=self.PRODUCT_LEVEL,
            scene="",
            instrument=self.INSTRUMENT_NAME,
            modes=[],
            channels=[],
            origin=origin,
        )
