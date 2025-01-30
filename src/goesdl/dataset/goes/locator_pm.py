"""
Provide locator for GOES-R Series imagery dataset's ABI products.

Classes:
    - GOESProductLocatorABIPM: Multi-band primary ABI products.
    - GOESProductLocatorMCMIP: Multi-band CMIP Product.
"""

from .locator_nso import GOESProductLocatorABINSO


class GOESProductLocatorABIPM(GOESProductLocatorABINSO):
    """
    Product locator for GOES-R Series imagery dataset's ABI products.

    Instrument: Advanced Baseline Imager (ABI)
    Product: Multi-band primary ABI products.
    """

    # Available single-band products from the GOES-R Series's ABI
    # instrument:
    AVAILABLE_PRODUCTS: dict[str, str] = {
        "MCMIP": "Multi-band Cloud and Moisture Imagery Product",
    }

    def __init__(self, name: str, scene: str, origin: str) -> None:
        """
        Initialise a GOES-R Series imagery dataset ABI product locator.

        Constructs a GOES-R Series imagery dataset ABI derived product
        locator object.

        Parameters
        ----------
        name : str
            The name of the GOES-R Series imagery dataset ABI product.
            Due to how the dataset directories are organised, only a
            single product can be provided.
        scene : str
            The scene of the GOES-R Series imagery dataset product, e.g.
            "F" or "C".
        origin : str
            The origin of the GOES-R Series imagery dataset ABI product,
            namely a satellite identifier, e.g. "G16". Due to how the
            dataset directories are organised, only a single origin may
            be provided.
        """
        self._validate_product(name, self.AVAILABLE_PRODUCTS)

        super().__init__(
            name=name,
            scene=scene,
            origin=origin,
        )


class GOESProductLocatorMCMIP(GOESProductLocatorABIPM):
    """
    Product locator for GOES-R Series imagery dataset's ABI products.

    Instrument: Advanced Baseline Imager (ABI)
    Product: Cloud and Moisture Imagery Product (CMIP).
    """

    PRODUCT_NAME: str = "MCMIP"

    def __init__(self, scene: str, origin: str) -> None:
        """
        Initialise a GOES-R Series imagery dataset ABI product locator.

        Constructs a GOES-R Series imagery dataset ABI multi-band
        primary product locator object.

        Parameters
        ----------
        scene : str
            The scene of the GOES-R Series imagery dataset product, e.g.
            "F" or "C".
        origin : str
            The origin of the GOES-R Series imagery dataset ABI product,
            namely a satellite identifier, e.g. "G16". Due to how the
            dataset directories are organised, only a single origin may
            be provided.
        """
        super().__init__(name=self.PRODUCT_NAME, scene=scene, origin=origin)
