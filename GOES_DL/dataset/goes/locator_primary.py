from .locator_abi import GOESProductLocatorABI


class GOESProductLocatorPrimary(GOESProductLocatorABI):
    """
    Product locator for GOES-R Series imagery dataset's ABI products.

    Instrument: Advanced Baseline Imager (ABI)
    Product: All primary ABI products.
    """

    AVAILABLE_CHANNELS: set[str] = {f"C{id:02d}" for id in range(1, 17)}

    AVAILABLE_PRODUCTS: dict[str, str] = {
        "CMIP": "Cloud and Moisture Imagery Product",
        "DMW": "Derived Motion Winds",
        "DMWV": "Derived Motion WV Winds",
        "Rad": "Radiances",
    }

    def __init__(
        self, name: str, scene: str, channel: list[str], origin: str
    ) -> None:
        """
        Initialise a GOES-R Series imagery dataset ABI product locator.

        Constructs a GOES-R Series imagery dataset ABI primary product
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
        channel : list[str]
            The list of channels of the GOES-R Series imagery dataset
            ABI product, e.g. "C08" or "C13".
        origin : str
            The origin of the GOES-R Series imagery dataset ABI product,
            namely a satellite identifier, e.g. "G16". Due to how the
            dataset directories are organised, only a single origin may
            be provided.

        Raises
        ------
        ValueError
            If the provided product name is invalid.
        """
        if unsupported_channel := set(channel) - set(self.AVAILABLE_CHANNELS):
            supported_channels: list[str] = sorted(self.AVAILABLE_CHANNELS)
            raise ValueError(
                f"Unsupported channel: '{sorted(unsupported_channel)}'. "
                f"Supported channels: {supported_channels}"
            )

        if name not in self.AVAILABLE_PRODUCTS:
            supported_products: list[str] = sorted(self.AVAILABLE_PRODUCTS)
            raise ValueError(
                f"Invalid product ID: '{name}'. "
                f"Available product IDs: {supported_products}"
            )

        level: str = "L1b" if name == "Rad" else "L2"

        super(GOESProductLocatorPrimary, self).__init__(
            name=name, level=level, scene=scene, channel=channel, origin=origin
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

        PRODUCT_RAD: str = "Rad"
        LEVEL_RAD: str = "L1b"
        LEVEL_NOT_RAD: str = "L2"

        assert (
            self.name == PRODUCT_RAD
            and self.level == LEVEL_RAD
            or self.scene != PRODUCT_RAD
            and self.level == LEVEL_NOT_RAD
        ), (
            f"Invalid level '{self.level}' "
            f"for primary ABI product '{self.name}'"
        )

        # The following checks depend on user input and an exception
        # should be raised if the user provides invalid values.

        if not self.channel:
            raise ValueError(
                f"Primary ABI product '{self.name}' "
                "does require channel specification"
            )

        super(GOESProductLocatorPrimary, self).validate_settings()
