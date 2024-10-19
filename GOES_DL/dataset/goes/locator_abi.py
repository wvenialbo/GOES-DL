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
        channels: list[str],
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
            If the provided origin, level or scene is invalid.
        """
        if scene not in self.AVAILABLE_SCENES:
            available_scenes: list[str] = sorted(self.AVAILABLE_SCENES)
            raise ValueError(
                f"Invalid scene ID: '{scene}'. "
                f"Available scene IDs: {available_scenes}"
            )

        # Instrument: Advanced Baseline Imager (ABI).
        INSTRUMENT_NAME: str = "ABI"

        # Available scan modes for the GOES-R Series imagery dataset ABI
        # products, regarding the requested scene for the product:
        # - Mode 3 (Previous Flex Mode)
        # - Mode 6 (Current Flex Mode)
        CM_MODES: list[str] = ["M3", "M6"]
        F_MODES: list[str] = ["M4"] + CM_MODES
        SCAN_MODES: list[str] = F_MODES if scene == "F" else CM_MODES

        super(GOESProductLocatorABI, self).__init__(
            name=name,
            level=level,
            scene=scene,
            instrument=INSTRUMENT_NAME,
            modes=SCAN_MODES,
            channels=channels,
            origin=origin,
        )
