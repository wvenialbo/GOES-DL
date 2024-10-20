from .locator_abi import GOESProductLocatorABI


class GOESProductLocatorABIDC(GOESProductLocatorABI):
    """
    Product locator for GOES-R Series imagery dataset's ABI products.

    Instrument: Advanced Baseline Imager (ABI)
    Product: All derived ABI products supporting channels.
    """

    AVAILABLE_PRODUCTS: dict[str, str] = {
        "DMW": "Derived Motion Winds",
        "DMWV": "Derived Motion WV Winds",
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
        if name not in self.AVAILABLE_PRODUCTS:
            supported_products: list[str] = sorted(self.AVAILABLE_PRODUCTS)
            raise ValueError(
                f"Invalid product ID: '{name}'. "
                f"Available product IDs: {supported_products}"
            )

        if isinstance(channels, str):
            channels = [channels]

        if not channels:
            raise ValueError(
                f"Derived ABI product '{name}' "
                "does require channel specification"
            )

        if name == "DMW":
            M_CHANNELS: set[str] = {"C02", "C07", "C08", "C09", "C10"}
            CF_CHANNELS: set[str] = {"C14"} | M_CHANNELS
            CF_SCENES: set[str] = {"C", "F"}

            supported_channels: set[str] = (
                CF_CHANNELS if scene in CF_SCENES else M_CHANNELS
            )

        else:
            supported_channels: set[str] = {"C08"}

        if unsupported_channels := set(channels) - supported_channels:
            raise ValueError(
                f"Unsupported channels {sorted(unsupported_channels)} "
                f"for current scene '{scene}' "
                f"of derived ABI product '{name}'. "
                f"Supported channels: {sorted(supported_channels)}"
            )

        PRODUCT_LEVEL: str = "L2"

        super(GOESProductLocatorABIDC, self).__init__(
            name=name,
            level=PRODUCT_LEVEL,
            scene=scene,
            channels=channels,
            origin=origin,
        )


class GOESProductLocatorDMW(GOESProductLocatorABIDC):
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

        M_CHANNELS: set[str] = {"C02", "C07", "C08", "C09", "C10"}
        CF_CHANNELS: set[str] = {"C14"} | M_CHANNELS
        CF_SCENES: set[str] = {"C", "F"}

        supported_channels: set[str] = (
            CF_CHANNELS if self.scene in CF_SCENES else M_CHANNELS
        )

        if not set(self.channels).issubset(supported_channels):
            raise ValueError(
                f"Unsupported channels {self.channels} "
                f"for current scene '{self.scene}' "
                f"of primary ABI product '{PRODUCT_NAME}'. "
                f"Supported channels: {sorted(supported_channels)}"
            )

        super(GOESProductLocatorDMW, self).__init__(
            name=PRODUCT_NAME, scene=scene, channels=channels, origin=origin
        )


class GOESProductLocatorDMWV(GOESProductLocatorABIDC):
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
