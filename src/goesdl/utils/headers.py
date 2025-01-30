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
    """A class to represent HTTP headers for requests."""

    def __init__(self, *, accept: str | None = None) -> None:
        """
        Initialize the RequestHeaders object.

        Parameters
        ----------
        accept : str | None, optional
            The value of the "accept" header, by default TEXT_HTML
            ("text/html").
        """
        if accept is None:
            accept = TEXT_HTML
        self._headers: dict[str, str] = self._build_headers(accept)

    @staticmethod
    def get_user_agent() -> str:
        """
        Get the user agent string.

        Returns
        -------
        str
            The user agent string.
        """
        return (
            f"{__package_id__}/{__version__} "
            f"({platform.system()} {os.name.upper()} "
            f"{platform.release()}/{platform.version()})"
        )

    @staticmethod
    def _build_headers(accept: str) -> dict[str, str]:
        """
        Build the headers dictionary.

        Parameters
        ----------
        accept : str
            The value of the "accept" header.

        Returns
        -------
        dict[str, str]
            A dictionary containing the headers.
        """
        user_agent: str = RequestHeaders.get_user_agent()

        return {
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
        """dict[str, str]: A dictionary containing the HTTP headers."""
        return self._headers
