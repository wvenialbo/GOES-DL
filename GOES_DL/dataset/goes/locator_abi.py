from .locator import GOESProductLocator


class GOESProductLocatorABI(GOESProductLocator):
    """
    Product locator for GOES-R Series imagery dataset's ABI products.

    Instrument: Advanced Baseline Imager (ABI).
    Product: All ABI products.
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

        if instrument_error := (self._verify_settings(name, level, channel)):
            raise ValueError(instrument_error)

        mode: list[str] = ["M3", "M4", "M6"] if scene == "F" else ["M3", "M6"]

        super(GOESProductLocatorABI, self).__init__(
            name=name,
            level=level,
            scene=scene,
            instrument="ABI",
            mode=mode,
            channel=channel,
            origin=origin,
        )

    def _verify_settings(
        self,
        name: str,
        level: str,
        channel: list[str],
    ) -> str:
        if name not in ["Rad", "CMIP", "DMW"] and channel:
            return f"Invalid channel {channel} for the requested ABI product."

        bad_level: str = ""
        if name == "Rad":
            bad_level = level if level != "L1b" else ""
        else:
            bad_level = level if level != "L2" else ""

        if bad_level:
            return f"Invalid level '{bad_level}' for requested ABI product."

        return ""
