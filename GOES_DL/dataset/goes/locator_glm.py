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
            mode=[],
            channel=[],
            origin=origin,
        )

    def validate_settings(self) -> None:
        """
        Validate the product locator settings after initialization.

        Validate the ABI product locator settings after initialization
        to ensure that the settings are consistent with the product
        locator's requirements and specifications.

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

        INSTRUMENT_NAME: str = "GLM"
        PRODUCT_LEVEL: str = "L2"

        assert (
            self.instrument == INSTRUMENT_NAME
        ), f"Invalid instrument name '{self.instrument}' for GLM product"

        assert self.level == PRODUCT_LEVEL, (
            f"Invalid level '{self.level}' "
            f"for GLM product '{self.name}', "
            f"expected '{PRODUCT_LEVEL}'"
        )

        # In fact, GLM products are Full Disk products but the scene ID
        # is not used in the directory structure nor in the file names.
        assert not self.scene, (
            f"Invalid scene ID '{self.scene}'. "
            "GLM products do not support scenes."
        )

        assert not self.mode, (
            f"Invalid scan modes {self.mode}. "
            "GLM instrument does not support scanning modes."
        )

        assert not self.channel, (
            f"Invalid channels {self.channel}. "
            "GLM instrument does not support channels."
        )

        super(GOESProductLocatorGLM, self).validate_settings()


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
