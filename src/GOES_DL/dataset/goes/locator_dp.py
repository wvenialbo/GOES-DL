"""
Provide locator for GOES-R Series imagery dataset's ABI products.

Classes:
    - GOESProductLocatorABIDP: All derived ABI products.
"""

from .locator_nso import GOESProductLocatorABINSO


class GOESProductLocatorABIDP(GOESProductLocatorABINSO):
    """
    Product locator for GOES-R Series imagery dataset's ABI products.

    Instrument: Advanced Baseline Imager (ABI)
    Product: All derived ABI products.
    """

    # Available single-band products from the GOES-R Series's ABI
    # instrument:
    AVAILABLE_PRODUCTS: dict[str, str] = {
        "ACHA": "Cloud Top Height (10km for 'F' and 'C', 4km for 'M')",
        "ACHA2KM": "Cloud Top Height (2km since 24 March 2023)",
        "ACHP2KM": "Cloud Top Pressure (2km spatial resolution)",
        "ACHT": "Cloud Top Temperature",
        "ACM": "Clear Sky Mask",
        "ACTP": "Cloud Top Phase",
        "ADP": "Aerosol Detection Product",
        "AICE": "Ice Concentration and Extent",
        "AITA": "Ice Age and Thickness",
        "AOD": "Aerosol Optical Depth",
        "BRF": "Bidirectional Reflectance Factor (Land Surface)",
        "CCL": "Cloud Cover Layers",
        "COD": "Cloud Optical Depth (4km for 'F' and 2km for 'C')",
        "COD2KM": "Cloud Optical Depth (2km since 22 March 2023)",
        "CPS": "Cloud Particle Size",
        "CTP": "Cloud Top Pressure",
        "DSI": "Derived Stability Indices",
        "DSR": "Downward Shortwave Radiation",
        "FDC": "Fire (Hot Spot Characterization)",
        "FSC": "Fractional Snow Cover",
        "LSA": "Land Surface Albedo",
        "LST": "Land Surface Temperature (10km for 'F', 2km for 'C' and 'M')",
        "LST2KM": "Land Surface Temperature (2km since 10 September 2021)",
        "LVMP": "Legacy Vertical Moisture Profile",
        "LVTP": "Legacy Vertical Temperature Profile",
        "RRQPE": "Rainfall Rate (Quantitative Precipitation Estimate)",
        "RSR": "Reflected Shortwave Radiation (Top-Of-Atmosphere)",
        "SST": "Sea Surface Temperature",
        "TPW": "Total Precipitable Water",
        "VAA": "Volcanic Ash (Detection and Height)",
    }

    ONLY_CF_SCENE: set[str] = {
        "AOD",
        "COD",
        "CTP",
        "RSR",
    }

    ONLY_F_SCENE: set[str] = {
        "AICE",
        "AITA",
        "COD2KM",
        "LST2KM",
        "RRQPE",
        "SST",
        "VAA",
    }

    ONLY_FM_SCENE: set[str] = {
        "ACHT",
    }

    ONLY_G16_G17: set[str] = {
        "VAA",
    }

    ONLY_G16_G18: set[str] = {
        "ACHA2KM",
        "ACHP2KM",
        "CCL",
        "FSC",
        "COD2KM",
    }

    CF_SCENE: set[str] = {"C", "F"}
    F_SCENE: set[str] = {"F"}
    FM_SCENE: set[str] = {"F", "M1", "M2"}

    G16_G17_ORIGIN: set[str] = {"G16", "G17"}
    G16_G18_ORIGIN: set[str] = {"G16", "G18"}

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

        Raises
        ------
        ValueError
            If the provided scene or origin is invalid.
        """
        self._validate_product(name, self.AVAILABLE_PRODUCTS)

        only_in_segment: list[set[str]] = [
            self.ONLY_CF_SCENE,
            self.ONLY_F_SCENE,
            self.ONLY_FM_SCENE,
        ]
        scene_segment: list[set[str]] = [
            self.CF_SCENE,
            self.F_SCENE,
            self.FM_SCENE,
        ]

        for only, segment in zip(only_in_segment, scene_segment):
            if name in only and scene not in segment:
                raise ValueError(
                    f"Invalid scene '{scene}' "
                    f"for derived ABI product '{name}', "
                    f"supported scenes {sorted(segment)}"
                )

        only_in_segment = [
            self.ONLY_G16_G17,
            self.ONLY_G16_G18,
        ]
        origin_segment: list[set[str]] = [
            self.G16_G17_ORIGIN,
            self.G16_G18_ORIGIN,
        ]

        for only, segment in zip(only_in_segment, origin_segment):
            if name in only and origin not in segment:
                raise ValueError(
                    f"Invalid origin '{origin}' "
                    f"for derived ABI product '{name}', "
                    f"supported origins {sorted(segment)}"
                )

        super().__init__(
            name=name,
            scene=scene,
            origin=origin,
        )
