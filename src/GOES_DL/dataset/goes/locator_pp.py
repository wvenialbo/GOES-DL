"""
Provide locator for GOES-R Series imagery dataset's ABI products.

Classes:
    - GOESProductLocatorABIPP: All primary ABI products.
    - GOESProductLocatorCMIP: ABI Cloud and Moisture Imagery Product
      (CMIP).
    - GOESProductLocatorRad: ABI Radiance Product (Rad).
"""

from .locator_abi import GOESProductLocatorABI


class GOESProductLocatorABIPP(GOESProductLocatorABI):
    """
    Product locator for GOES-R Series imagery dataset's ABI products.

    Instrument: Advanced Baseline Imager (ABI)
    Product: All primary ABI products.
    """

    AVAILABLE_CHANNELS: set[str] = {f"C{idn:02d}" for idn in range(1, 17)}

    AVAILABLE_PRODUCTS: dict[str, str] = {
        "CMIP": "Cloud and Moisture Imagery Product",
        "Rad": "Radiance",
    }

    PRODUCT_RAD: str = "Rad"

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
        if isinstance(channels, str):
            channels = [channels]

        if not channels:
            raise ValueError(
                f"Primary ABI product '{name}' "
                "does require channel specification"
            )

        self._validate_channels(channels, self.AVAILABLE_CHANNELS)

        self._validate_product(name, self.AVAILABLE_PRODUCTS)

        level: str = (
            self.LEVEL_RAD if name == self.PRODUCT_RAD else self.LEVEL_NOT_RAD
        )

        super().__init__(
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

    PRODUCT_NAME_RAD: str = GOESProductLocatorABIPP.PRODUCT_RAD

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
            ABI product, e.g. "C08" or "C13".
        origin : str
            The origin of the GOES-R Series imagery dataset ABI product,
            namely a satellite identifier, e.g. "G16". Due to how the
            dataset directories are organised, only a single origin may
            be provided.
        """
        super().__init__(
            name=self.PRODUCT_NAME_RAD,
            scene=scene,
            channels=channels,
            origin=origin,
        )


class GOESProductLocatorCMIP(GOESProductLocatorABIPP):
    """
    Product locator for GOES-R Series imagery dataset's ABI products.

    Instrument: Advanced Baseline Imager (ABI)
    Product: Cloud and Moisture Imagery Product (CMIP).
    """

    PRODUCT_NAME_CMIP: str = "CMIP"

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
            ABI product, e.g. "C08" or "C13".
        origin : str
            The origin of the GOES-R Series imagery dataset ABI product,
            namely a satellite identifier, e.g. "G16". Due to how the
            dataset directories are organised, only a single origin may
            be provided.
        """
        super().__init__(
            name=self.PRODUCT_NAME_CMIP,
            scene=scene,
            channels=channels,
            origin=origin,
        )
