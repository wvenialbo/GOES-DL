"""
Provide locator for GOES-R Series imagery dataset's ABI products.

Classes:
    - GOESProductLocatorABIDC: All derived ABI products supporting
      channels.
    - GOESProductLocatorDMW: ABI Derived Motion Winds (DMW).
    - GOESProductLocatorDMWV: ABI Derived Motion WV Winds (DMWV).
"""

from .locator_abi import GOESProductLocatorABI


class GOESProductLocatorABIDC(GOESProductLocatorABI):
    """
    Product locator for GOES-R Series imagery dataset's ABI products.

    Instrument: Advanced Baseline Imager (ABI)
    Product: All derived ABI products supporting channels.
    """

    DMW_PRODUCT: str = "DMW"
    DMWV_PRODUCT: str = "DMWV"

    AVAILABLE_PRODUCTS: dict[str, str] = {
        DMW_PRODUCT: "Derived Motion Winds",
        DMWV_PRODUCT: "Derived Motion WV Winds",
    }

    M_CHANNELS: set[str] = {"C02", "C07", "C08", "C09", "C10"}
    CF_CHANNELS: set[str] = {"C14"} | M_CHANNELS
    CF_SCENES: set[str] = {"C", "F"}
    WV_CHANNELS: set[str] = {"C08"}

    available_channels: set[str]

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
        channels : str | list[str]
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
        self._validate_product(name, self.AVAILABLE_PRODUCTS)

        if isinstance(channels, str):
            channels = [channels]

        if not channels:
            raise ValueError(
                f"Derived ABI product '{name}' "
                "does require channel specification"
            )

        self._validate_channels(channels, self.available_channels)

        super().__init__(
            name=name,
            level=self.DEFAULT_PRODUCT_LEVEL,
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

    PRODUCT_NAME_DMW: str = GOESProductLocatorABIDC.DMW_PRODUCT

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
        channels : str | list[str]
            The list of channels of the GOES-R Series imagery dataset
            ABI product, e.g. "C08" or "C14".
        origin : str
            The origin of the GOES-R Series imagery dataset ABI product,
            namely a satellite identifier, e.g. "G16". Due to how the
            dataset directories are organised, only a single origin may
            be provided.
        """
        self.available_channels = (
            self.CF_CHANNELS if scene in self.CF_SCENES else self.M_CHANNELS
        )

        super().__init__(
            name=self.PRODUCT_NAME_DMW,
            scene=scene,
            channels=channels,
            origin=origin,
        )


class GOESProductLocatorDMWV(GOESProductLocatorABIDC):
    """
    Product locator for GOES-R Series imagery dataset's ABI products.

    Instrument: Advanced Baseline Imager (ABI)
    Product: Derived Motion WV Winds (DMWV).
    """

    PRODUCT_NAME_DMWV: str = GOESProductLocatorABIDC.DMWV_PRODUCT

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
        self.available_channels = self.WV_CHANNELS

        super().__init__(
            name=self.PRODUCT_NAME_DMWV,
            scene=scene,
            channels=list(self.WV_CHANNELS),
            origin=origin,
        )
