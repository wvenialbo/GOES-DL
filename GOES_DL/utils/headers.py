"""
Provide a class to manage HTTP request headers.

Defines the `RequestHeaders` class, which is used to manage HTTP request
headers for the GOES-DL project.

Classes:
    RequestHeaders: A class to represent HTTP headers for requests.
"""

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

ACCEPT_LANGUAGE: str = (
    "en-GB;q=0.9,en-US;q=0.8,en;q=0.7," + "es-ES;q=0.8,es-PY;q=0.7,es;q=0.6"
)


class RequestHeaders:
    """
    A class to represent HTTP headers for requests.

    Attributes
    ----------
    accept : str
        The value of the "accept" header.
    """

    def __init__(self, *, accept: str = TEXT_HTML) -> None:
        """
        Initialize the RequestHeaders object.

        Parameters
        ----------
        accept : str, optional
            The value of the "accept" header, by default TEXT_HTML
            ("text/html").
        """
        user_agent: str = (
            f"{__package_id__}/{__version__} "
            f"({platform.system()} {os.name.upper()} "
            f"{platform.release()}/{platform.version()})"
        )

        self._headers: dict[str, str] = {
            "accept": accept,
            "accept-encoding": "gzip, deflate, br, zstd",
            "accept-language": ACCEPT_LANGUAGE,
            "cache-control": "no-cache",
            "connection": "keep-alive",
            "pragma": "no-cache",
            "user-agent": user_agent,
        }

    @property
    def headers(self) -> dict[str, str]:
        """
        Get the HTTP headers.

        Returns
        -------
        dict[str, str]
            A dictionary containing the HTTP headers.
        """
        return self._headers
