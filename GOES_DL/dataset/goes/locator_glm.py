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
            available_products: list[str] = sorted(
                self.AVAILABLE_PRODUCTS.keys()
            )
            raise ValueError(
                f"Invalid product ID: '{origin}'. "
                f"Available product IDs: {available_products}"
            )

        super(GOESProductLocatorGLM, self).__init__(
            name=name,
            level="L2",
            scene="",
            instrument="GLM",
            mode=[],
            channel=[],
            origin=origin,
        )


class GOESProductLocatorLCFA(GOESProductLocatorGLM):
    """
    Product locator for GOES-R Series imagery dataset's GLM products.

    Instrument: Geostationary Lightning Mapper (GLM).
    Product: Lightning Cluster-Filter Algorithm (LCFA).
    """

    def __init__(self, origin: str) -> None:
        """
        Initialise a GOES-R Series imagery dataset LCFA product locator.

        Constructs a GOES-R Series imagery dataset LCFA product locator
        object.

        Parameters
        ----------
        origin : str
            The origin of the GOES-R Series dataset LCFA product, namely
            a satellite identifier, e.g. "G16". Due to how the dataset
            directories are organised, only a single origin may be
            provided.
        """
        super(GOESProductLocatorLCFA, self).__init__(
            name="LCFA",
            origin=origin,
        )
