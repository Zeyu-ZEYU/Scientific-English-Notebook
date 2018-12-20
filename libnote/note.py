from .item import Item
from typing import List, Optional, Set


class Note:
    def __init__(self, name: str):
        self.__cursor = 0
        self.__item_keys: Set[str] = set()
        self.__items: List[Item] = []
        self.__name = name

        self.is_show_more = True

    def __str__(self):
        is_started = False
        string = ""

        for item in self.__items:
            if is_started:
                string += "\n"

            string += str(item)
            is_started = True

        return string

    @property
    def cursor(self) -> int:
        return self.__cursor

    @cursor.setter
    def cursor(self, cursor_value: int):
        if cursor_value >= 0 and cursor_value < len(self.__items):
            self.__cursor = cursor_value

    @property
    def length(self) -> int:
        return len(self.__items)

    @property
    def name(self) -> str:
        return self.__name

    def add(self, item: Item):
        self.__items.append(item)
        self.__item_keys.add(item.key)

    def cursor_forward(self):
        if self.__cursor < len(self.__items) - 1:
            self.__cursor += 1

    def cursor_backward(self):
        if self.__cursor > 0:
            self.__cursor -= 1

    def get_current_item(self) -> Optional[Item]:
        if len(self.__items) == 0:
            return None

        return self.__items[self.__cursor]

    def get_the_refreshed(self) -> str:
        string = ""

        if len(self.__items) == 0:
            return string

        if self.is_show_more:
            string += str(self.__items[self.__cursor])
        else:
            string += self.__items[self.__cursor].key + "\n"

        return string

    def has_item_key(self, item_key: str) -> bool:
        return item_key in self.__item_keys
