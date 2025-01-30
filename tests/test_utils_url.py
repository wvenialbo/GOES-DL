import unittest

from goesdl.utils.url import URL as URL


class TestUrlMethods(unittest.TestCase):
    HOST_URL = "http://example.com"
    BASE_URL = "http://example.com/path/"
    FOLDER_URL = "http://example.com/path/to"
    FILE_URL = "http://example.com/path/to/file"
    FULL_URL = (
        "http://user:pass@example.com:80/"
        "path/to/file;parameters?query#fragment"
    )

    def test_abspath_current_dir(self) -> None:
        original_url = "http://example.com/path/./to/file"
        expected_url = self.FILE_URL
        self.assertEqual(URL.abspath(original_url), expected_url)

    def test_abspath_sub_dir(self) -> None:
        original_url = "http://example.com/path/../to/file"
        expected_url = "http://example.com/to/file"
        self.assertEqual(URL.abspath(original_url), expected_url)

    def test_join_single_part_override(self) -> None:
        original_url = self.BASE_URL
        override_url = self.FILE_URL
        self.helper_join_single_part(original_url, override_url, override_url)

    def test_join_single_part_override_alt(self) -> None:
        original_url = self.FILE_URL
        override_url = self.FOLDER_URL
        self.helper_join_single_part(original_url, override_url, override_url)

    def test_join_single_part_override_same(self) -> None:
        override_url = self.FILE_URL
        self.helper_join_single_part(override_url, override_url, override_url)

    def test_join_multiple_parts_to_base(self) -> None:
        original_url = self.BASE_URL
        expected_url = self.FILE_URL
        self.helper_join_multiple_parts(
            original_url, "to/", "file", expected_url
        )

    def test_join_multiple_parts_host(self) -> None:
        original_url = self.HOST_URL
        expected_url = self.FILE_URL
        self.helper_join_multiple_parts(
            original_url, "path/to/", "file", expected_url
        )

    def test_join_single_part_to_base(self) -> None:
        original_url = self.BASE_URL
        expected_url = self.FILE_URL
        self.helper_join_single_part(original_url, "to/file", expected_url)

    def test_join_single_part_to_host(self) -> None:
        original_url = self.HOST_URL
        expected_url = self.FILE_URL
        self.helper_join_single_part(
            original_url, "path/to/file", expected_url
        )

    def test_parse_scheme(self) -> None:
        parsed_url = URL.parse(self.FULL_URL)
        self.assertEqual(parsed_url.scheme, "http")

    def test_parse_location(self) -> None:
        parsed_url = URL.parse(self.FULL_URL)
        self.assertEqual(parsed_url.netloc, "user:pass@example.com:80")

    def test_parse_path(self) -> None:
        parsed_url = URL.parse(self.FULL_URL)
        self.assertEqual(parsed_url.path, "/path/to/file")

    def test_parse_path_parameters(self) -> None:
        parsed_url = URL.parse(self.FULL_URL)
        self.assertEqual(parsed_url.params, "parameters")

    def test_parse_path_query(self) -> None:
        parsed_url = URL.parse(self.FULL_URL)
        self.assertEqual(parsed_url.query, "query")

    def test_parse_path_fragment(self) -> None:
        parsed_url = URL.parse(self.FULL_URL)
        self.assertEqual(parsed_url.fragment, "fragment")

    def test_parse_path_username(self) -> None:
        parsed_url = URL.parse(self.FULL_URL)
        self.assertEqual(parsed_url.username, "user")

    def test_parse_path_password(self) -> None:
        parsed_url = URL.parse(self.FULL_URL)
        self.assertEqual(parsed_url.password, "pass")

    def test_parse_path_hostname(self) -> None:
        parsed_url = URL.parse(self.FULL_URL)
        self.assertEqual(parsed_url.hostname, "example.com")

    def test_parse_path_port(self) -> None:
        parsed_url = URL.parse(self.FULL_URL)
        self.assertEqual(parsed_url.port, 80)

    def helper_join_multiple_parts(
        self,
        base_url: str,
        part_url_1: str,
        part_url_2: str,
        expected_url: str,
    ) -> None:
        joined_url = URL.join(base_url, part_url_1, part_url_2)
        self.assertEqual(joined_url, expected_url)

    def helper_join_single_part(
        self, base_url: str, part_url: str, expected_url: str
    ) -> None:
        joined_url = URL.join(base_url, part_url)
        self.assertEqual(joined_url, expected_url)
