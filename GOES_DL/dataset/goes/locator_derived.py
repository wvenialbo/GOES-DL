from .locator_abi import GOESProductLocatorABI


class GOESProductLocatorDerived(GOESProductLocatorABI):
    """
    Product locator for GOES-R Series imagery dataset's ABI products.

    Instrument: Advanced Baseline Imager (ABI)
    Product: Derived ABI products.
    """

    AVAILABLE_PRODUCTS: dict[str, str] = {
        "ACHA": "Cloud Top Height",
        "ACHT": "Cloud Top Temperature",  # !C
        "ACM": "Clear Sky Mask",
        "ACTP": "Cloud Top Phase",
        "ADP": "Aerosol Detection Product",
        "AOD": "Aerosol Optical Depth",  # !M
        "COD": "Cloud Optical Depth",  # !M
        "CPS": "Cloud Particle Size",
        "CTP": "Cloud Top Pressure",  # !M
        "DSR": "Downward Shortwave Radiation",
        "FDC": "Fire (Hot Spot Characterization)",  # !M
        "LST": "Land Surface Temperature",
        "LVMP": "Legacy Vertical Moisture Profile",
        "LVTP": "Legacy Vertical Temperature Profile",
        "MCMIP": "Multi-band Cloud and Moisture Imagery",
        "ACM": "Clear Sky Mask",
        "ACM": "Clear Sky Mask",
        "ACM": "Clear Sky Mask",
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
            available_products: list[str] = sorted(
                self.AVAILABLE_PRODUCTS.keys()
            )
            raise ValueError(
                f"Invalid product ID: '{origin}'. "
                f"Available product IDs: {available_products}"
            )

        super(GOESProductLocatorDerived, self).__init__(
            name=name, level="L2", scene=scene, channel=[], origin=origin
        )

    def validate_settings(self) -> None:
        """
        Validate the product locator settings after initialization.

        Validate the ABI primary product locator settings after
        initialization to ensure that the settings are consistent with
        the product locator's requirements and specifications.

        Returns
        -------
        str
            An error message if the instrument of product settings are
            invalid; otherwise, an empty string.
        """
        # The following checks are assertions that should never fail
        # since they are values internally set by the constructor and
        # they do not represent user input. (I do not use global
        # constants for the assertions here, otherwise these checks
        # might always pass regardless of the actual values.)

        assert self.level == "L2", (
            f"Invalid level '{self.level}' "
            f"for derived ABI product '{self.name}'."
        )

        assert not self.channel, (
            f"Derived ABI product '{self.name}' " "does not support channels."
        )

        super(GOESProductLocatorDerived, self).validate_settings()
