from typing import Any

from .datasource_cached import DatasourceCached


class DatasourceHTTP(DatasourceCached):
    def get_file(self, file_path: str) -> Any:
        return None

    def get_folder_path(self, dir_path: str) -> str:
        return ""

    def listdir(self, dir_path: str) -> list[str]:
        return []
