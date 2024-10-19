from .locator_glm import GOESProductLocatorGLM


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
        PRODUCT_NAME: str = "LCFA"

        super(GOESProductLocatorLCFA, self).__init__(
            name=PRODUCT_NAME, origin=origin
        )
