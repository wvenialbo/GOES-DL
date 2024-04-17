from .locator_multiband import GOESProductLocatorMultiBand


class GOESProductLocatorMCMIP(GOESProductLocatorMultiBand):
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
