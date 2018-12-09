from typing import Dict, List


class Saved:
    def __init__(self):
        self.__saved: Dict[str, List[str]] = {}

    def add(self, key: str, values: List[str]):
        self.__saved[key] = values

    def check_existence(self, key: str) -> bool:
        return key in self.__saved
