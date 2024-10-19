from .locator import GOESProductLocator


class GOESProductLocatorGLM(GOESProductLocator):
    """
    Product locator for GOES-R Series imagery dataset's GLM products.

    Instrument: Geostationary Lightning Mapper (GLM).
    Product: All GLM products.
    """

    AVAILABLE_PRODUCTS: dict[str, str] = {
        "LCFA": "Lightning Cluster-Filter Algorithm"
    }

    def __init__(self, name: str, origin: str) -> None:
        """
        Initialise a GOES-R Series imagery dataset GLM product locator.

        Constructs a GOES-R Series imagery dataset GLM product locator
        object.

        Parameters
        ----------
        name : str
            The name of the GOES-R Series imagery dataset GLM product.
            Due to how the dataset directories are organised, only a
            single product can be provided.
        origin : str
            The origin of the GOES-R Series imagery dataset GLM product,
            namely a satellite identifier, e.g. "G16". Due to how the
            dataset directories are organised, only a single origin may
            be provided.

        Raises
        ------
        ValueError
            If the provided product name is invalid.
        """
        if name not in self.AVAILABLE_PRODUCTS:
            available_products: list[str] = sorted(self.AVAILABLE_PRODUCTS)
            raise ValueError(
                f"Invalid product ID: '{name}'. "
                f"Available product IDs: {available_products}"
            )

        INSTRUMENT_NAME: str = "GLM"
        PRODUCT_LEVEL: str = "L2"

        super(GOESProductLocatorGLM, self).__init__(
            name=name,
            level=PRODUCT_LEVEL,
            scene="",
            instrument=INSTRUMENT_NAME,
            modes=[],
            channels=[],
            origin=origin,
        )
