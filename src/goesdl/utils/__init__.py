"""
Provide utility classes and functions for the GOES-DL project.

Classes:
    RequestHeaders: A class for managing HTTP request headers.
    url: A utility function for URL manipulations.
"""

from .headers import RequestHeaders
from .url import URL

__all__ = ["RequestHeaders", "URL"]
