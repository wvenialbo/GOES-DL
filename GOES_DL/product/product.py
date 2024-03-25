from abc import ABC, abstractmethod


class GOESProduct(ABC):
    def __init__(self, product_id: str, origin_id: str) -> None:
        self._product_id: str = product_id
        self._origin_id: str = origin_id

    def __format__(self, format_spec: str) -> str:
        if format_spec == "product":
            return self._product_id
        if format_spec == "origin":
            return self._origin_id
        if format_spec == "":
            return str(self)
        available_format_spec: list[str] = sorted(self._format_spec())
        raise ValueError(
            f"Invalid format specifier: '{format_spec}'. "
            f"Available format specifiers: {available_format_spec}"
        )

    @staticmethod
    def _format_spec() -> list[str]:
        return ["product", "origin"]

    def __repr__(self) -> str:
        module_name: str = self.__module__
        class_name: str = self.__class__.__name__
        current_state: str = self._repr_stat()
        return (
            f"<{module_name}.{class_name}({current_state}) at {id(self):#x}>"
        )

    def _repr_stat(self) -> str:
        return f"origin_id='{self._origin_id}',product_id='{self._product_id}'"

    def __str__(self) -> str:
        class_name: str = self.__class__.__name__
        current_state: str = self._str_stat()
        return f"{class_name}:\n{current_state}"

    def _str_stat(self) -> str:
        return (
            f"  Origin ID  : '{self._origin_id}'\n"
            f"  Product ID : '{self._product_id}'"
        )

    @abstractmethod
    def get_baseurl(self, timestamp: str) -> str:
        pass

    @abstractmethod
    def get_filename(self, timestamp: str) -> str:
        pass

    @property
    def product_id(self) -> str:
        return self._product_id

    @property
    def origin_id(self) -> str:
        return self._origin_id
