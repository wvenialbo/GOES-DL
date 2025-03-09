"""
Provide a utility class for URL manipulations.

Classes:
    url: Utility class for URL manipulations.
"""

from urllib.parse import ParseResult, urljoin, urlparse


class URL:
    """
    Utility class for URL manipulations.

    Methods
    -------
    abspath(path: str)
        Returns the absolute path of the given URL.
    join(base_url: str, *parts: str)
        Joins one or more URL parts to the base URL.
    parse(path: str)
        Parses the given URL and returns a ParseResult object.
    """

    @staticmethod
    def abspath(path: str) -> str:
        """
        Return the absolute path of the given URL.

        Parameters
        ----------
        path : str
            The URL to be converted to an absolute path.

        Returns
        -------
        str
            The absolute path of the given URL.
        """
        parsed_url: ParseResult = urlparse(path)
        abs_path = urljoin(parsed_url.netloc, parsed_url.path)
        parsed_url = parsed_url._replace(path=abs_path)
        return parsed_url.geturl()

    @staticmethod
    def join(base_url: str, *parts: str) -> str:
        """
        Join one or more URL parts to the base URL.

        Parameters
        ----------
        base_url : str
            The base URL to which parts will be joined.
        *parts : str
            One or more URL parts to be joined to the base URL.

        Returns
        -------
        str
            The resulting URL after joining the parts to the base URL.
        """
        dest_url: str = base_url
        for part in parts:
            dest_url = urljoin(dest_url, part)
        return dest_url

    @staticmethod
    def parse(path: str) -> ParseResult:
        """
        Parse the given URL and returns a ParseResult object.

        Parameters
        ----------
        path : str
            The URL to be parsed.

        Returns
        -------
        ParseResult
            The parsed URL as a ParseResult object.
        """
        return urlparse(path)
