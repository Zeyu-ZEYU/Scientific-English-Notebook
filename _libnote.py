from os import path
from typing import List, Optional, Sequence, Set, Tuple


class _SubNotePage:
    @property
    def cursor(self) -> int:
        return self.__cursor

    @cursor.setter
    def cursor(self, value: int):
        if value >= 0 and value < self.length:
            self.__cursor = value

    @property
    def length(self) -> int:
        return len(self.__sub_page)

    @property
    def name(self) -> str:
        return self.__name

    def __init__(self, name: str = ""):
        self.show_more = True

        self.__cursor = 0
        self.__keys: Set[str] = set()
        self.__name = name
        self.__sub_page: List[Tuple[str, List[Tuple[str, List[str]]]]] = []

    def add(self, key: str, value: Tuple[str, Sequence[str]]):
        annotation = value[0]
        content: List[str] = []

        for line in value[1]:
            content.append(line)

        if key in self.__keys:
            for item in self.__sub_page:
                if item[0] == key:
                    item[1].append((annotation, content))

                    break
        else:
            self.__keys.add(key)
            self.__sub_page.append((key, [(annotation, content)]))

    def delete(self, key: str):
        if key in self.__keys:
            self.__keys.remove(key)

            for index in range(self.length):
                if self.__sub_page[index][0] == key:
                    self.__sub_page.pop(index)

                    break

    def item_str(self, cursor: Optional[int] = None) -> str:
        if self.length == 0:
            return ""

        if not cursor or cursor < 0 or cursor >= self.length:
            cursor = self.__cursor

        item = self.__sub_page[cursor]
        key = item[0]
        values = item[1]
        brief_str = key
        remaining_str = ""
        started = False

        for annotation, content in values:
            if annotation != "":
                brief_str += "  # " + annotation

            if content != []:
                if started:
                    remaining_str += "    " + "========\n"

                for line in content:
                    remaining_str += "    " + line + "\n"

                started = True

        brief_str += "\n"

        if self.show_more:
            return brief_str + remaining_str
        else:
            return brief_str

    def __str__(self):
        string = ""
        show_more_tmp = self.show_more
        started = False

        self.show_more = True

        for index in range(self.length):
            if started:
                string += "\n"

            string += self.item_str(index)
            started = True

        self.show_more = show_more_tmp

        return string


class NotePage:
    @property
    def cursor(self) -> int:
        if self.sub_page_num != 0:
            return self.__sub_pages[self.__index].cursor

    @cursor.setter
    def cursor(self, value: int):
        if self.sub_page_num != 0:
            self.__sub_pages[self.__index].cursor = value

    @property
    def cursors(self) -> List[int]:
        cursors: List[int] = []

        for sub_page in self.__sub_pages:
            cursors.append(sub_page.cursor)

        return cursors

    @cursors.setter
    def cursors(self, value: Sequence[int]):
        for index in range(self.sub_page_num
                           if self.sub_page_num <= len(value) else len(value)):
            self.__sub_pages[index].cursor = value[index]

    @property
    def index(self) -> int:
        return self.__index

    @index.setter
    def index(self, value: int):
        if value >= 0 and value < self.sub_page_num:
            self.__index = value

    @property
    def length(self) -> int:
        length = 0

        for sub_page in self.__sub_pages:
            length += sub_page.length

        return length

    @property
    def name(self) -> str:
        return self.__name

    @property
    def show_more(self) -> bool:
        show_more = True

        if self.sub_page_num != 0:
            show_more = self.__sub_pages[self.__index].show_more

        return show_more

    @show_more.setter
    def show_more(self, value: bool):
        if self.sub_page_num != 0:
            self.__sub_pages[self.__index].show_more = value

    @property
    def sub_page_len(self) -> int:
        length = 0

        if self.sub_page_num != 0:
            length = self.__sub_pages[self.__index].length

        return length

    @property
    def sub_page_name(self) -> str:
        if self.sub_page_num != 0:
            return self.__sub_pages[self.__index].name

    @property
    def sub_page_num(self) -> int:
        return len(self.__sub_pages)

    def __init__(self, file_path: str, name: str = ""):
        self.__index = 0
        self.__name = name
        self.__sub_pages: List[_SubNotePage] = []

        self.__load(file_path)

    def add(self, key: str, value: Tuple[str, Sequence[str]]):
        if self.sub_page_num != 0:
            self.__sub_pages[self.__index].add(key, value)

    def delete(self, key: str):
        if self.sub_page_num != 0:
            self.__sub_pages[self.__index].delete(key)

    def item_str(self,
                 index: Optional[int] = None,
                 cursor: Optional[int] = None) -> str:
        if self.sub_page_num == 0:
            return ""

        if not index or index < 0 or index >= self.sub_page_num:
            index = self.__index

        return self.__sub_pages[index].item_str(cursor)

    def __load(self, file_path: str):
        if path.exists(file_path):
            with open(file_path, "r", encoding="utf-8") as file:
                line = file.readline()

                while True:
                    annotation = ""
                    content: List[str] = []
                    key = ""

                    while line == "\n" or len(line) > 3 and line[:4] == "    ":
                        line = file.readline()

                    if line == "":
                        break

                    if line.strip() == "\"\"\"":
                        sub_page_name = ""

                        line = file.readline()

                        while line != "" and line.strip() != "\"\"\"":
                            sub_page_name += line
                            line = file.readline()

                        if line == "":
                            break
                        else:
                            self.__sub_pages.append(
                                _SubNotePage(sub_page_name.strip()))
                            line = file.readline()

                            continue

                    if self.sub_page_num == 0:
                        self.__sub_pages.append(_SubNotePage())

                    sharp_position = line.find("#")

                    if sharp_position == -1:
                        key = line.strip()
                    else:
                        key = line[:sharp_position].strip()
                        annotation = line[sharp_position + 1:].strip()

                    line = file.readline()

                    while True:
                        if line == "\n":
                            content.append("\n")
                        elif len(line) > 3 and line[:4] == "    ":
                            content.append(line[4:].rstrip())
                        else:
                            for index in range(len(content) - 1, -1, -1):
                                if content[index] == "\n":
                                    content.pop(index)
                                else:
                                    break

                            break

                        line = file.readline()

                    self.__sub_pages[-1].add(key, (annotation, content))
