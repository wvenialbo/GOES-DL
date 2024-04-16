from .locator_primary import GOESProductLocatorPrimary


class GOESProductLocatorRad(GOESProductLocatorPrimary):
    """
    Product locator for GOES-R Series imagery dataset's ABI products.

    Instrument: Advanced Baseline Imager (ABI)
    Product: Radiances (Rad).
    """

    def __init__(
        self, scene: str, channel: str | list[str], origin: str
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
        channel : list[str]
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
            name=PRODUCT_NAME, scene=scene, channel=channel, origin=origin
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

        PRODUCT_NAME: str = "Rad"
        PRODUCT_LEVEL: str = "L1b"

        assert (
            self.name == PRODUCT_NAME
        ), f"Invalid product name '{self.name}', expected '{PRODUCT_NAME}'"

        assert self.level == PRODUCT_LEVEL, (
            f"Invalid level '{self.level}' "
            f"for primary ABI product '{PRODUCT_NAME}', "
            f"expected '{PRODUCT_LEVEL}'"
        )

        super(GOESProductLocatorRad, self).validate_settings()


class GOESProductLocatorCMIP(GOESProductLocatorPrimary):
    """
    Product locator for GOES-R Series imagery dataset's ABI products.

    Instrument: Advanced Baseline Imager (ABI)
    Product: Cloud and Moisture Imagery Product (CMIP).
    """

    def __init__(
        self, scene: str, channel: str | list[str], origin: str
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
        channel : list[str]
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
            name=PRODUCT_NAME, scene=scene, channel=channel, origin=origin
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

        PRODUCT_NAME: str = "CMIP"
        PRODUCT_LEVEL: str = "L2"

        assert (
            self.name == PRODUCT_NAME
        ), f"Invalid product name '{self.name}', expected '{PRODUCT_NAME}'"

        assert self.level == PRODUCT_LEVEL, (
            f"Invalid level '{self.level}' "
            f"for primary ABI product '{PRODUCT_NAME}', "
            f"expected '{PRODUCT_LEVEL}'"
        )

        super(GOESProductLocatorCMIP, self).validate_settings()


class GOESProductLocatorDMW(GOESProductLocatorPrimary):
    """
    Product locator for GOES-R Series imagery dataset's ABI products.

    Instrument: Advanced Baseline Imager (ABI)
    Product: Derived Motion Winds (DMW).
    """

    def __init__(
        self, scene: str, channel: str | list[str], origin: str
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
        channel : list[str]
            The list of channels of the GOES-R Series imagery dataset
            ABI product, e.g. "C08" or "C14".
        origin : str
            The origin of the GOES-R Series imagery dataset ABI product,
            namely a satellite identifier, e.g. "G16". Due to how the
            dataset directories are organised, only a single origin may
            be provided.
        """
        PRODUCT_NAME: str = "DMW"

        super(GOESProductLocatorDMW, self).__init__(
            name=PRODUCT_NAME, scene=scene, channel=channel, origin=origin
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

        PRODUCT_NAME: str = "DMW"
        PRODUCT_LEVEL: str = "L2"

        assert (
            self.name == PRODUCT_NAME
        ), f"Invalid product name '{self.name}', expected '{PRODUCT_NAME}'"

        assert self.level == PRODUCT_LEVEL, (
            f"Invalid level '{self.level}' "
            f"for primary ABI product '{PRODUCT_NAME}', "
            f"expected '{PRODUCT_LEVEL}'"
        )

        # The following checks depend on user input and an exception
        # should be raised if the user provides invalid values.

        M_CHANNELS: set[str] = {"C02"} | {f"C{id:02d}" for id in range(7, 11)}
        CF_CHANNELS: set[str] = {"C14"} | M_CHANNELS
        CF_SCENES: set[str] = {"C", "F"}

        supported_channels: set[str] = (
            CF_CHANNELS if self.scene in CF_SCENES else M_CHANNELS
        )

        if not set(self.channel).issubset(supported_channels):
            raise ValueError(
                f"Unsupported channels {self.channel} "
                f"for current scene '{self.scene}' of "
                f"primary ABI product '{PRODUCT_NAME}'. "
                f"Supported channels: {sorted(supported_channels)}"
            )

        super(GOESProductLocatorDMW, self).validate_settings()


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
            channel=PRODUCT_CHANNELS,
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

        PRODUCT_NAME: str = "DMWV"
        PRODUCT_LEVEL: str = "L2"
        PRODUCT_CHANNELS: set[str] = {"C08"}

        assert (
            self.name == PRODUCT_NAME
        ), f"Invalid product name '{self.name}', expected '{PRODUCT_NAME}'"

        assert self.level == PRODUCT_LEVEL, (
            f"Invalid level '{self.level}' "
            f"for primary ABI product '{PRODUCT_NAME}', "
            f"expected '{PRODUCT_LEVEL}'"
        )

        assert set(self.channel).issubset(PRODUCT_CHANNELS), (
            f"Unsupported channels {self.channel} "
            f"for current scene '{self.scene}' of "
            f"primary ABI product '{PRODUCT_NAME}'. "
            f"Supported channels: {sorted(PRODUCT_CHANNELS)}"
        )

        super(GOESProductLocatorDMWV, self).validate_settings()
