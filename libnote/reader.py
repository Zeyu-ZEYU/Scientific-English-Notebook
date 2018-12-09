from libnote.item import Item
from typing import Optional, Tuple


class Reader:
    def __init__(self, file: str):
        self.__last_line = "\n"
        self.__reader = open(file, "r", encoding="utf-8")

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.__reader.close()

    def next_item(self) -> Optional[Tuple[bool, Item]]:
        if self.__last_line == "":
            return None

        is_vocabulary = True
        item = Item("", [])

        line = self.__last_line
        while line != "":
            if line == "\n" or len(line) > 4 and line[0] == line[1] == line[
                    2] == line[3] == " ":
                line = self.__reader.readline()
                self.__last_line = line
            else:
                item.key = line.strip()
                if item.key[0] == "$":
                    is_vocabulary = False
                line = self.__reader.readline()
                while len(line) > 4 and line[0] == line[1] == line[2] == line[
                        3] == " ":
                    item.values.append(line[4:-1])
                    line = self.__reader.readline()
                self.__last_line = line
                break

        return is_vocabulary, item
