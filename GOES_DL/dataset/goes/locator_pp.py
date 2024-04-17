from .locator_primary import GOESProductLocatorPrimary


class GOESProductLocatorRad(GOESProductLocatorPrimary):
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


class GOESProductLocatorCMIP(GOESProductLocatorPrimary):
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


class GOESProductLocatorDMW(GOESProductLocatorPrimary):
    """
    Product locator for GOES-R Series imagery dataset's ABI products.

    Instrument: Advanced Baseline Imager (ABI)
    Product: Derived Motion Winds (DMW).
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
            ABI product, e.g. "C08" or "C14".
        origin : str
            The origin of the GOES-R Series imagery dataset ABI product,
            namely a satellite identifier, e.g. "G16". Due to how the
            dataset directories are organised, only a single origin may
            be provided.
        """
        PRODUCT_NAME: str = "DMW"

        M_CHANNELS: set[str] = {"C02"} | {f"C{id:02d}" for id in range(7, 11)}
        CF_CHANNELS: set[str] = {"C14"} | M_CHANNELS
        CF_SCENES: set[str] = {"C", "F"}

        supported_channels: set[str] = (
            CF_CHANNELS if self.scene in CF_SCENES else M_CHANNELS
        )

        if not set(self.channels).issubset(supported_channels):
            raise ValueError(
                f"Unsupported channels {self.channels} "
                f"for current scene '{self.scene}' of "
                f"primary ABI product '{PRODUCT_NAME}'. "
                f"Supported channels: {sorted(supported_channels)}"
            )

        super(GOESProductLocatorDMW, self).__init__(
            name=PRODUCT_NAME, scene=scene, channels=channels, origin=origin
        )


class GOESProductLocatorDMWV(GOESProductLocatorPrimary):
    """
    Product locator for GOES-R Series imagery dataset's ABI products.

    Instrument: Advanced Baseline Imager (ABI)
    Product: Derived Motion WV Winds (DMWV).
    """

    def __init__(self, scene: str, origin: str) -> None:
        """
        Initialise a GOES-R Series imagery dataset ABI product locator.

        Constructs a GOES-R Series imagery dataset ABI primary product
        locator object.

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
        PRODUCT_NAME: str = "DMWV"
        PRODUCT_CHANNELS: list[str] = ["C08"]

        super(GOESProductLocatorDMWV, self).__init__(
            name=PRODUCT_NAME,
            scene=scene,
            channels=PRODUCT_CHANNELS,
            origin=origin,
        )
