from .datasource import Any, Datasource


class DatasourceHTTP(Datasource):
    def clear_cache(self, dir_path: str = "") -> None:
        pass

    def get_file(self, file_path: str) -> Any:
        return None

    def listdir(self, dir_path: str) -> list[str]:
        return []
