from .locator import GOESProductLocator


class GOESProductLocatorABI(GOESProductLocator):
    """
    Product locator for GOES-R Series imagery dataset's ABI products.

    Instrument: Advanced Baseline Imager (ABI).
    Product: All primary and derived ABI products.
    """

    # Available scenes for the GOES-R Series imagery dataset products:
    #
    # NOTE: In its strictest sense, “Contiguous United States” refers
    # to the lower 48 states in North America (including the District
    # of Columbia), and “Continental United States” refers to 49 states
    # (including Alaska and the District of Columbia).
    AVAILABLE_SCENES: dict[str, str] = {
        "F": "Full Disk",
        "C": "CONUS (Continental United States)",
        "M1": "Mesoscale (Domain 1)",
        "M2": "Mesoscale (Domain 2)",
    }

    def __init__(
        self,
        name: str,
        level: str,
        scene: str,
        channel: list[str],
        origin: str,
    ) -> None:
        """
        Initialise a GOES-R Series imagery dataset ABI product locator.

        Constructs a GOES-R Series imagery dataset ABI product locator
        object.

        Parameters
        ----------
        name : str
            The name of the GOES-R Series imagery dataset ABI product.
            Due to how the dataset directories are organised, only a
            single product can be provided.
        level : str
            The level of the GOES-R Series imagery dataset product, e.g.
            "L1b" or "L2".
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
            If the provided origin, level or scene is invalid.
        """
        if scene not in self.AVAILABLE_SCENES:
            available_levels: list[str] = sorted(self.AVAILABLE_SCENES.keys())
            raise ValueError(
                f"Invalid scene ID: '{scene}'. "
                f"Available scene IDs: {available_levels}"
            )

        # Instrument: Advanced Baseline Imager (ABI).
        INSTRUMENT_NAME: str = "ABI"

        # Available scan modes for the GOES-R Series imagery dataset ABI
        # products, regarding the requested scene for the product:
        F_MODES: list[str] = ["M3", "M4", "M6"]
        CM_MODES: list[str] = ["M3", "M6"]
        SCAN_MODE: list[str] = F_MODES if scene == "F" else CM_MODES

        super(GOESProductLocatorABI, self).__init__(
            name=name,
            level=level,
            scene=scene,
            instrument=INSTRUMENT_NAME,
            mode=SCAN_MODE,
            channel=channel,
            origin=origin,
        )

    def validate_settings(self) -> None:
        """
        Validate the product locator settings after initialization.

        Validate the ABI product locator settings after initialization
        to ensure that the settings are consistent with the product
        locator's requirements and specifications.

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

        INSTRUMENT_NAME: str = "ABI"
        NOT_F_MODES: set[str] = {"M3", "M6"}
        F_MODES: set[str] = {"M4"} | NOT_F_MODES

        assert (
            self.instrument == INSTRUMENT_NAME
        ), f"Invalid instrument name '{self.instrument}' for ABI product"

        assert (
            self.scene == "F"
            and set(self.mode).issubset(F_MODES)
            or self.scene != "F"
            and set(self.mode).issubset(NOT_F_MODES)
        ), f"Invalid scan modes {self.mode} for current scene '{self.scene}'"

        super(GOESProductLocatorABI, self).validate_settings()
