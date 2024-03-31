from GOES_DL.dataset.gridsat.constants import (
    GOES_PRODUCT_DATE_FORMAT,
    GOES_PRODUCT_DATE_PATTERN,
    GOES_PRODUCT_LATEST_VERSION,
)
from GOES_DL.dataset.gridsat.product import GridSatProduct


class GridSatProductGOES(GridSatProduct):
    """
    Represent the GridSat-GOES dataset product filename checker.

    This class implements the interface for the GridSat-GOES dataset
    product filename checker. The checker is responsible for extracting
    the datetime from a dataset product filename and verifying if a
    given filename matches the expected pattern.

    The data in the GridSat-GOES dataset (Geostationary Operational
    Environmental Satellites - GOES/CONUS) products comes from GOES
    2nd generation (GOES-I to GOES-M) series, GOES-8 to GOES-15; they
    provide data for two separate domains: the entire GOES domain
    (Full Disk) and the CONUS (Contiguous United States). The domain
    and origin names are reflected in the product's filename, as is the
    product's version. The product's filename pattern is as follows:

    'GridSat-DOMAIN.origin.yyyy.mm.dd.HHMM.version.nc',

    where `DOMAIN` is the scene name in uppercase (e.g. 'CONUS' or
    'GOES'), `origin` is the satellite identifier in lowercase (e.g.
    'goes08' to 'goes15'), and `version` is the product's version (e.g.
    'v01'). `yyyy`, `mm`, `dd`, `HH` and `MM` are the year, month, day,
    hour, and minute, respectively, fixed length and padded with zeros.

    Input is half-hourly data from the GOES 2nd generation satellite
    series with gridded 0.04°x0.04° spatial resolution that spans from
    1994 to 2017. Six total channels are available

    For more information visit the following link and links therein:
    https://www.ncei.noaa.gov/products/satellite/gridded-goes-conus

    Attributes
    ----------
    scene : str
        The scene ID for the dataset. Supported scenes are "F" (Full
        Disk) and "C" (CONUS, Contiguous United States). Due to how
        the GridSat-GOES dataset is organised, only a single scene
        may be provided.
    origin : str | list[str]
        The origin of the GridSat-GOES product, namely a satellite
        identifier, e.g. "goes08". The origin may be a single origin
        or a list of origins.
    version : str | list[str], optional
        The version of the GridSat-GOES product; e.g., "v01". The
        version may be a single version or a list of versions. Only
        the latest version is available in the public repository. The
        default is the latest version ("v01").

    Methods
    -------
    get_datetime(filename: str) -> datetime:
        Extracts the datetime from a GridSat-GOES product filename.
        (inherited)
    invalid_origin(origin: list[str]) -> str:
        Check for unavailable origins in a list of origins.
    invalid_scene(scene: list[str]) -> str:
        Check for unavailable scenes in a list of scenes.
    invalid_version(version: list[str]) -> str:
        Check for unsupported versions in a list of versions.
    match(filename: str) -> bool:
        Checks if a given filename matches the GridSat-GOES product
        filename pattern. (inherited)

    Raises
    ------
    ValueError
        If the provided origin, scene, or version is invalid.
    """

    # Satellites in the GOES 2nd generation (GOES-I to GOES-M) series
    # are identified by the following IDs:
    AVAILABLE_ORIGIN: dict[str, str] = {
        f"G{id:02d}": f"goes{id:02d}" for id in range(8, 16)
    }

    # Available scenes/domains from the GOES 2nd generation Imager
    # Products:
    #
    # NOTE: In its strictest sense, “contiguous United States” refers
    # to the lower 48 states in North America (including the District of
    # of Columbia), and “continental United States” refers to 49 states
    # (including Alaska and the District of Columbia).
    AVAILABLE_SCENE: dict[str, str] = {
        "F": "Full Disk",
        "C": "CONUS (Contiguous United States)",
    }

    # Available versions of the GOES 2nd generation Imager Products:
    AVAILABLE_VERSION: set[str] = {"v01"}

    # Mapping between scene IDs and dataset group names:
    SCENE_TO_NAME: dict[str, str] = {
        "F": "GOES",
        "C": "CONUS",
    }

    def __init__(
        self,
        scene: str,
        origin: str | list[str],
        version: str | list[str] = GOES_PRODUCT_LATEST_VERSION,
    ) -> None:
        """
        Initialise a GridSat-GOES dataset product object.

        Constructs a new GridSat-GOES dataset product object.

        Parameters
        ----------
        scene : str
            The scene ID for the dataset. Supported scenes are "F" (Full
            Disk) and "C" (CONUS, Contiguous United States). Due to how
            the GridSat-GOES dataset is organised, only a single scene
            may be provided.
        origin : str | list[str]
            The origin of the GridSat-GOES product, namely a satellite
            identifier, e.g. "goes08". The origin may be a single origin
            or a list of origins.
        version : str | list[str]
            The version of the GridSat-GOES product; e.g., "v01". The
            version may be a single version or a list of versions.

        Raises
        ------
        ValueError
            If the provided origin, scene, or version is invalid.
        """
        if unavailable_scene := self.invalid_scene([scene]):
            available_scene: list[str] = sorted(self.AVAILABLE_SCENE.keys())
            raise ValueError(
                f"Invalid scene: {unavailable_scene}. "
                f"Available scene IDs: {available_scene}"
            )

        if isinstance(origin, str):
            origin = [origin]

        if unavailable_origin := self.invalid_origin(origin):
            available_origin: list[str] = sorted(self.AVAILABLE_ORIGIN.keys())
            raise ValueError(
                f"Invalid origin: '{unavailable_origin}'. "
                f"Available origin IDs: {available_origin}"
            )

        if isinstance(version, str):
            version = [version]

        if unsupported_version := self.invalid_version(version):
            raise ValueError(
                f"Unsupported version: {unsupported_version}. "
                f"Supported versions: {sorted(self.AVAILABLE_VERSION)}"
            )

        product_name: str = self.SCENE_TO_NAME[scene]
        data_origin: list[str] = [
            self.AVAILABLE_ORIGIN[orig] for orig in origin
        ]

        super().__init__(
            name=product_name,
            origin=data_origin,
            version=version,
            date_format=GOES_PRODUCT_DATE_FORMAT,
            date_pattern=GOES_PRODUCT_DATE_PATTERN,
        )

    def invalid_origin(self, origin: list[str]) -> str:
        """
        Check for unavailable or invalid origins.

        Verifies and returns the first unavailable origin from a list of
        origins.

        Parameters
        ----------
        origin : list[str]
            The list of origins to check for unavailable origins.

        Returns
        -------
        str
            The first unavailable origin found in the list of origins.
            An empty string is returned if all origins are available.
        """
        return next(
            (orig for orig in origin if orig not in self.AVAILABLE_ORIGIN),
            "",
        )

    def invalid_scene(self, scene: list[str]) -> str:
        """
        Check for unavailable or invalid scenes.

        Verifies and returns the first unavailable scene from a list of
        scenes.

        Parameters
        ----------
        scene : list[str]
            The list of scenes to check for unavailable scenes.

        Returns
        -------
        str
            The first unavailable scene found in the list of scenes.
            An empty string is returned if all scenes are available.
        """
        return next(
            (sce for sce in scene if sce not in self.AVAILABLE_SCENE),
            "",
        )

    def invalid_version(self, version: list[str]) -> str:
        """
        Check for unsupported or invalid versions.

        Verifies and returns the first unsupported version from a list
        of versions.

        Parameters
        ----------
        version : list[str]
            The list of versions to check for unsupported versions.

        Returns
        -------
        str
            The first unsupported version found in the list of versions.
            An empty string is returned if all versions are supported.
        """
        return next(
            (ver for ver in version if ver not in self.AVAILABLE_VERSION),
            "",
        )


if __name__ == "__main__":
    FILENAME_1: str = "GridSat-GOES.goes12.1994.09.01.0000.v01.nc"
    FILENAME_2: str = "GridSat-GOES.goes12.2017.12.31.2300.v01.nc"
    product: GridSatProductGOES = GridSatProductGOES("F", "G12")
    print(product)
    print(FILENAME_2.startswith(product.get_prefix()))
    print(FILENAME_2.endswith(product.get_suffix()))
    print(product.match(FILENAME_1))
    print(product.get_datetime(FILENAME_1))
    print(product.get_datetime(FILENAME_2).astimezone())
