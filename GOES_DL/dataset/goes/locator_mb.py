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

        PRODUCT_NAME: str = "MCMIP"
        PRODUCT_LEVEL: str = "L2"

        assert (
            self.name == PRODUCT_NAME
        ), f"Invalid product name '{self.name}', expected '{PRODUCT_NAME}'"

        assert self.level == PRODUCT_LEVEL, (
            f"Invalid level '{self.level}' "
            f"for multi-band primary ABI product '{PRODUCT_NAME}', "
            f"expected '{PRODUCT_LEVEL}'"
        )

        super(GOESProductLocatorMCMIP, self).validate_settings()
