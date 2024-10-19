import os
import platform
from .. import __package_id__, __version__

IMAGE_JPEG: str = "image/jpeg"
IMAGE_PNG: str = "image/png"
TEXT_HTML: str = "text/html"
APPLICATION_JSON: str = "application/json"

# THREDDS defines two mime-types for NetCDF:
APPLICATION_NETCDF3: str = "application/x-netcdf"
APPLICATION_NETCDF4: str = "application/x-netcdf4"


class RequestHeaders:
    """
    A class to represent HTTP headers for requests.

    Attributes
    ----------
    accept : str
        The value of the "accept" header.
    """

    def __init__(self, *, accept: str = TEXT_HTML) -> None:
        """Inicializa una nueva instancia de la clase Headers.

        Parameters
        ----------
        referrer : str
            El valor de la cabecera "referer".
        accept : str, optional
            El valor de la cabecera "accept", por defecto es "text/html".
        authorization : str, optional
            El valor de la cabecera "authorization", por defecto es "".
        """
        USER_AGENT: str = (
            f"{__package_id__}/{__version__} "
            f"({platform.system()} {os.name.upper()} "
            f"{platform.release()}/{platform.version()})"
        )
        ACCEPT_LANGUAGE: str = (
            "en-GB;q=0.9,en-US;q=0.8,en;q=0.7,"
            "es-ES;q=0.8,es-PY;q=0.7,es;q=0.6"
        )

        self._headers: dict[str, str] = {
            "accept": accept,
            "accept-encoding": "gzip, deflate, br, zstd",
            "accept-language": ACCEPT_LANGUAGE,
            "cache-control": "no-cache",
            "connection": "keep-alive",
            "pragma": "no-cache",
            "user-agent": USER_AGENT,
        }

    @property
    def headers(self) -> dict[str, str]:
        return self._headers
