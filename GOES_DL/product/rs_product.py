from .product import GOESProduct


class GOESRSProduct(GOESProduct):
    # Supported instruments from the GOES-R series:
    AVAILABLE_INSTRUMENT: dict[str, str] = {
        "ABI": "Advanced Baseline Imager",
        "GLM": "Geostationary Lightning Mapper",
    }

    # Supported product levels from the GOES-R series:
    AVAILABLE_LEVEL: dict[str, str] = {
        "L1b": "Level 1b "
        "(calibrated and geographically corrected, "
        "radiance units)",
        "L2": "Level 2 "
        "(calibrated and geographically corrected, "
        "reflectance/brightness [Kelvin] units)",
    }

    # Satellites in the GOES-R series are identified by the following
    # IDs:
    AVAILABLE_ORIGIN: dict[str, str] = {
        f"G{id:02d}": f"GOES{id:02d}" for id in range(16, 19)
    }

    def __init__(
        self,
        level_id: str,
        product_id: str,
        instrument_id: str,
        origin_id: str,
    ) -> None:
        if level_id not in self.AVAILABLE_LEVEL:
            available_level: list[str] = list(self.AVAILABLE_LEVEL.keys())
            raise ValueError(
                f"Invalid level_id: '{level_id}'. "
                f"Available level IDs: {sorted(available_level)}"
            )

        if instrument_id not in self.AVAILABLE_INSTRUMENT:
            available_instrument: list[str] = list(
                self.AVAILABLE_INSTRUMENT.keys()
            )
            raise ValueError(
                f"Invalid instrument_id: '{instrument_id}'. "
                f"Available instrument IDs: {sorted(available_instrument)}"
            )

        if origin_id not in self.AVAILABLE_ORIGIN:
            available_origin: list[str] = list(self.AVAILABLE_ORIGIN.keys())
            raise ValueError(
                f"Invalid origin_id: '{origin_id}'. "
                f"Available origin IDs: {sorted(available_origin)}"
            )

        super(GOESRSProduct, self).__init__(product_id, origin_id)

        self._instrument_id: str = instrument_id
        self._level_id: str = level_id

    def __format__(self, format_spec: str) -> str:
        if format_spec == "instrument":
            return self._instrument_id
        if format_spec == "level":
            return self._level_id
        return super(GOESRSProduct, self).__format__(format_spec)

    @staticmethod
    def _format_spec() -> list[str]:
        return super(GOESRSProduct, GOESRSProduct)._format_spec() + [
            "instrument",
            "level",
        ]

    def _repr_stat(self) -> str:
        return (
            f"level_id='{self._level_id}',"
            f"product_id='{self._product_id}',"
            f"instrument_id='{self._instrument_id}',"
            f"origin_id='{self._origin_id}'"
        )

    def _str_stat(self) -> str:
        return (
            f"  Origin ID  : '{self._origin_id}'\n"
            f"  Instrument : '{self._instrument_id}'\n"
            f"  Product ID : '{self._product_id}'\n"
            f"  Level      : '{self._level_id}'"
        )

    @property
    def instrument_id(self) -> str:
        return self._instrument_id

    @property
    def level_id(self) -> str:
        return self._level_id
