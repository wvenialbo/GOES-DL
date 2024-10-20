from urllib.parse import ParseResult, urljoin, urlparse


class url:
    @staticmethod
    def abspath(path: str) -> str:
        parsed_url: ParseResult = urlparse(path)
        abs_path = urljoin(parsed_url.netloc, parsed_url.path)
        parsed_url = parsed_url._replace(path=abs_path)
        return parsed_url.geturl()

    @staticmethod
    def join(base_url: str, *parts: str) -> str:
        dest_url: str = base_url
        for part in parts:
            dest_url = urljoin(dest_url, part)
        return dest_url

    @staticmethod
    def parse(path: str) -> ParseResult:
        return urlparse(path)
