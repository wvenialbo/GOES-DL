from .locator_abi import GOESProductLocatorABI


class GOESProductLocatorABIPM(GOESProductLocatorABI):
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
        if name not in self.AVAILABLE_PRODUCTS:
            supported_products: list[str] = sorted(self.AVAILABLE_PRODUCTS)
            raise ValueError(
                f"Invalid product ID: '{name}'. "
                f"Available product IDs: {supported_products}"
            )

        PRODUCT_LEVEL: str = "L2"

        super(GOESProductLocatorABIPM, self).__init__(
            name=name,
            level=PRODUCT_LEVEL,
            scene=scene,
            channels=[],
            origin=origin,
        )


class GOESProductLocatorMCMIP(GOESProductLocatorABIPM):
    """
    Product locator for GOES-R Series imagery dataset's ABI products.

    Instrument: Advanced Baseline Imager (ABI)
    Product: Cloud and Moisture Imagery Product (CMIP).
    """

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
        PRODUCT_NAME: str = "MCMIP"

        super(GOESProductLocatorMCMIP, self).__init__(
            name=PRODUCT_NAME, scene=scene, origin=origin
        )
