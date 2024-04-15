from .locator_abi import GOESProductLocatorABI


class GOESProductLocatorABIPrimary(GOESProductLocatorABI):
    """
    Product locator for GOES-R Series imagery dataset's ABI products.

    Instrument: Advanced Baseline Imager (ABI)
    Product: Primary ABI products.
    """

    AVAILABLE_CHANNELS: set[str] = {f"C{id:02d}" for id in range(1, 17)}

    AVAILABLE_PRODUCTS: dict[str, str] = {
        "CMIP": "Cloud and Moisture Imagery Product",
        "DMW": "Derived Motion Winds",
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
        if unsupported_channel := self.invalid_channel(channel):
            supported_versions: list[str] = sorted(self.AVAILABLE_CHANNELS)
            raise ValueError(
                f"Unsupported version: '{unsupported_channel}'. "
                f"Supported versions: {supported_versions}"
            )

        if name not in self.AVAILABLE_PRODUCTS:
            available_products: list[str] = sorted(
                self.AVAILABLE_PRODUCTS.keys()
            )
            raise ValueError(
                f"Invalid product ID: '{origin}'. "
                f"Available product IDs: {available_products}"
            )

        level: str = "L1b" if name == "Rad" else "L2"

        super(GOESProductLocatorABIPrimary, self).__init__(
            name=name, level=level, scene=scene, channel=channel, origin=origin
        )

    def invalid_channel(self, channel: list[str]) -> str:
        """
        Check for unsupported or invalid versions.

        Verifies and returns the first unsupported version from a list
        of versions.

        Parameters
        ----------
        version : list[str]
            The list of versions to check for unsupported versions.

        Returns
        -------
        str
            The first unsupported version found in the list of versions.
            An empty string is returned if all versions are supported.
        """
        return next(
            (chn for chn in channel if chn not in self.AVAILABLE_CHANNELS),
            "",
        )


class GOESProductLocatorCMIP(GOESProductLocatorABIPrimary):
    """
    Product locator for GOES-R Series imagery dataset's ABI products.

    Instrument: Advanced Baseline Imager (ABI)
    Product: Cloud and Moisture Imagery Product (CMIP).
    """

    def __init__(self, scene: str, channel: list[str], origin: str) -> None:
        """
        Initialise a GOES-R Series imagery dataset ABI product locator.

        Constructs a GOES-R Series imagery dataset ABI primary product
        locator object.

        Parameters
        ----------
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
        """
        super(GOESProductLocatorCMIP, self).__init__(
            name="CMIP", scene=scene, channel=channel, origin=origin
        )


class GOESProductLocatorDMW(GOESProductLocatorABIPrimary):
    """
    Product locator for GOES-R Series imagery dataset's ABI products.

    Instrument: Advanced Baseline Imager (ABI)
    Product: Derived Motion Winds (DMW).
    """

    def __init__(self, scene: str, channel: list[str], origin: str) -> None:
        """
        Initialise a GOES-R Series imagery dataset ABI product locator.

        Constructs a GOES-R Series imagery dataset ABI primary product
        locator object.

        Parameters
        ----------
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
        """
        super(GOESProductLocatorDMW, self).__init__(
            name="DMW", scene=scene, channel=channel, origin=origin
        )


class GOESProductLocatorRad(GOESProductLocatorABIPrimary):
    """
    Product locator for GOES-R Series imagery dataset's ABI products.

    Instrument: Advanced Baseline Imager (ABI)
    Product: Radiances (Rad).
    """

    def __init__(self, scene: str, channel: list[str], origin: str) -> None:
        """
        Initialise a GOES-R Series imagery dataset ABI product locator.

        Constructs a GOES-R Series imagery dataset ABI primary product
        locator object.

        Parameters
        ----------
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
        """
        super(GOESProductLocatorRad, self).__init__(
            name="Rad", scene=scene, channel=channel, origin=origin
        )
