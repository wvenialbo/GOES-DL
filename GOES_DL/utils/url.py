import posixpath
from urllib.parse import ParseResult, urlparse


class url:
    @staticmethod
    def abspath(base: str, path: str) -> str:
        return path if path.startswith(base) else url.join(base, path)

    @staticmethod
    def join(base: str, *parts: str) -> str:
        base_url = urlparse(base)
        dest_url = base_url
        for part in parts:
            dest_url = dest_url._replace(
                path=posixpath.join(dest_url.path, part)
            )
        return dest_url.geturl()

    @staticmethod
    def parse(path: str) -> ParseResult:
        return urlparse(path)
