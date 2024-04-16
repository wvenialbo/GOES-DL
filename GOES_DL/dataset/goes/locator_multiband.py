from .locator_abi import GOESProductLocatorABI


class GOESProductLocatorMultiBand(GOESProductLocatorABI):
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

        super(GOESProductLocatorMultiBand, self).__init__(
            name=name,
            level=PRODUCT_LEVEL,
            scene=scene,
            channels=[],
            origin=origin,
        )

    def validate_settings(self) -> None:
        """
        Validate the product locator settings after initialization.

        Validate the ABI primary product locator settings after
        initialization to ensure that the settings are consistent with
        the product locator's requirements and specifications.

        Raises
        ------
        AssertionError
            If the instrument or product internal settings are invalid.
            I.e. when the settings do not represent user input and were
            internally set by the class's or a subclass's constructor.
        ValueError
            If an unexpected or unsupported setting is required for an
            instrument that does not support it. I.e. when the setting
            depends on user input and the user provides invalid values.
        """
        # The following checks are assertions that should never fail
        # since they are values internally set by the constructor and
        # they do not represent user input. (I do not use global
        # constants for the assertions here, otherwise these checks
        # might always pass regardless of the actual values.)

        PRODUCT_LEVEL: str = "L2"

        assert self.level == PRODUCT_LEVEL, (
            f"Invalid level '{self.level}' "
            f"for multi-band primary ABI product '{self.name}', "
            f"expected '{PRODUCT_LEVEL}'"
        )

        assert not self.channels, (
            f"Multi-band primary ABI product '{self.name}' "
            "does not support channels."
        )

        super(GOESProductLocatorMultiBand, self).validate_settings()
