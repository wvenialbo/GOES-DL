from .product import GOESProduct


class GOES2GProduct(GOESProduct):
    # Satellites in the GOES 2nd generation (GOES-I to GOES-M) series
    # are identified by the following IDs:
    AVAILABLE_ORIGIN: dict[str, str] = {
        f"G{id:02d}": f"GOES{id:02d}" for id in range(8, 16)
    }

    def __init__(self, product_id: str, origin_id: str) -> None:
        if origin_id not in self.AVAILABLE_ORIGIN:
            available_origin: list[str] = list(self.AVAILABLE_ORIGIN.keys())
            raise ValueError(
                f"Invalid origin_id: '{origin_id}'. "
                f"Available origin IDs: {sorted(available_origin)}"
            )

        super(GOES2GProduct, self).__init__(product_id, origin_id)
