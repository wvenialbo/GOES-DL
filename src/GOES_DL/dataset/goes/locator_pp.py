from .locator_abi import GOESProductLocatorABI


class GOESProductLocatorABIPP(GOESProductLocatorABI):
    """
    Product locator for GOES-R Series imagery dataset's ABI products.

    Instrument: Advanced Baseline Imager (ABI)
    Product: All primary ABI products.
    """

    AVAILABLE_CHANNELS: set[str] = {f"C{id:02d}" for id in range(1, 17)}

    AVAILABLE_PRODUCTS: dict[str, str] = {
        "CMIP": "Cloud and Moisture Imagery Product",
        "Rad": "Radiance",
    }

    def __init__(
        self, name: str, scene: str, channels: str | list[str], origin: str
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
        channels : list[str]
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
        if isinstance(channels, str):
            channels = [channels]

        if not channels:
            raise ValueError(
                f"Primary ABI product '{name}' "
                "does require channel specification"
            )

        if unsupported_channel := set(channels) - set(self.AVAILABLE_CHANNELS):
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

        PRODUCT_RAD: str = "Rad"
        LEVEL_RAD: str = "L1b"
        LEVEL_NOT_RAD: str = "L2"

        level: str = LEVEL_RAD if name == PRODUCT_RAD else LEVEL_NOT_RAD

        super(GOESProductLocatorABIPP, self).__init__(
            name=name,
            level=level,
            scene=scene,
            channels=channels,
            origin=origin,
        )


class GOESProductLocatorRad(GOESProductLocatorABIPP):
    """
    Product locator for GOES-R Series imagery dataset's ABI products.

    Instrument: Advanced Baseline Imager (ABI)
    Product: Radiance (Rad).
    """

    def __init__(
        self, scene: str, channels: str | list[str], origin: str
    ) -> None:
        """
        Initialise a GOES-R Series imagery dataset ABI product locator.

        Constructs a GOES-R Series imagery dataset ABI primary product
        locator object.

        Parameters
        ----------
        scene : str
            The scene of the GOES-R Series imagery dataset product, e.g.
            "F" or "C".
        channels : list[str]
            The list of channels of the GOES-R Series imagery dataset
            ABI product, e.g. "C08" or "C13".
        origin : str
            The origin of the GOES-R Series imagery dataset ABI product,
            namely a satellite identifier, e.g. "G16". Due to how the
            dataset directories are organised, only a single origin may
            be provided.
        """
        PRODUCT_NAME: str = "Rad"

        super(GOESProductLocatorRad, self).__init__(
            name=PRODUCT_NAME, scene=scene, channels=channels, origin=origin
        )


class GOESProductLocatorCMIP(GOESProductLocatorABIPP):
    """
    Product locator for GOES-R Series imagery dataset's ABI products.

    Instrument: Advanced Baseline Imager (ABI)
    Product: Cloud and Moisture Imagery Product (CMIP).
    """

    def __init__(
        self, scene: str, channels: str | list[str], origin: str
    ) -> None:
        """
        Initialise a GOES-R Series imagery dataset ABI product locator.

        Constructs a GOES-R Series imagery dataset ABI primary product
        locator object.

        Parameters
        ----------
        scene : str
            The scene of the GOES-R Series imagery dataset product, e.g.
            "F" or "C".
        channels : list[str]
            The list of channels of the GOES-R Series imagery dataset
            ABI product, e.g. "C08" or "C13".
        origin : str
            The origin of the GOES-R Series imagery dataset ABI product,
            namely a satellite identifier, e.g. "G16". Due to how the
            dataset directories are organised, only a single origin may
            be provided.
        """
        PRODUCT_NAME: str = "CMIP"

        super(GOESProductLocatorCMIP, self).__init__(
            name=PRODUCT_NAME, scene=scene, channels=channels, origin=origin
        )
