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

    def validate_settings(self) -> None:
        """
        Validate the product locator settings after initialization.

        Validate the ABI primary product locator settings after
        initialization to ensure that the settings are consistent with
        the product locator's requirements and specifications.

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

        PRODUCT_NAME: str = "LCFA"

        assert (
            self.name == PRODUCT_NAME
        ), f"Invalid product name '{self.name}', expected '{PRODUCT_NAME}'"

        super(GOESProductLocatorLCFA, self).validate_settings()
