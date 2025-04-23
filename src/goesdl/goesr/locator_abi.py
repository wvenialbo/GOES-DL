"""
Provide locator for GOES-R Series imagery dataset's ABI products.

Classes:
    - GOESProductLocatorABI: All primary and derived Advanced Baseline
      Imager (ABI) products.
"""

import re

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
        GOESProductLocator.FULL_DISK: "Full Disk",
        GOESProductLocator.CONUS: "CONUS (Continental United States)",
        GOESProductLocator.MESO_1: "Mesoscale (Domain 1)",
        GOESProductLocator.MESO_2: "Mesoscale (Domain 2)",
    }

    # Instrument: Advanced Baseline Imager (ABI).
    INSTRUMENT_NAME: str = "ABI"

    # Available scan modes for the GOES-R Series imagery dataset ABI
    # products, regarding the requested scene for the product:
    # - Mode 3 (Previous Flex Mode)
    # - Mode 6 (Current Flex Mode)
    CM_MODES: list[str] = ["M3", "M6"]
    F_MODES: list[str] = ["M4"] + CM_MODES

    LEVEL_RAD: str = "L1b"
    LEVEL_NOT_RAD: str = "L2"
    DEFAULT_PRODUCT_LEVEL: str = LEVEL_NOT_RAD

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

        Notes
        -----
        ValueError is raised if the provided origin, level or scene is
        invalid.
        """
        # TODO: Too many positional arguments. Solve it by using
        #       the Builder or Factory methods, or patterns like
        #       Essence or Fluent.
        self._validate_scene(scene, self.AVAILABLE_SCENES)

        scan_modes: list[str] = (
            self.F_MODES if scene == self.FULL_DISK else self.CM_MODES
        )

        super().__init__(
            name=name,
            level=level,
            scene=scene,
            instrument=self.INSTRUMENT_NAME,
            modes=scan_modes,
            channels=channels,
            origin=origin,
        )

    @staticmethod
    def _explode_channels(channels: list[str]) -> list[str]:
        channel_range_pattern = re.compile(r"^C(\d{2})-(\d{2})$")

        exploded_channels: set[str] = set()

        for channel_item in channels:
            if match_range := channel_range_pattern.match(channel_item):
                first_channel, last_channel = match_range.groups()
                try:
                    start_num = int(first_channel)
                    end_num = int(last_channel)
                except ValueError as error:
                    raise ValueError(
                        "Syntax error processing "
                        f"channel range '{channel_item}'"
                    ) from error
                if end_num < start_num:
                    raise ValueError(
                        f"Invalid order for channel range '{channel_item}'"
                    )
                channel_range = {
                    f"C{channel_num:02d}"
                    for channel_num in range(start_num, end_num + 1)
                }
                exploded_channels.update(channel_range)
            else:
                exploded_channels.add(channel_item)

        return sorted(exploded_channels)
