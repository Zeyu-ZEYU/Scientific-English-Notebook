from os import makedirs
from os.path import dirname, exists, getsize, isfile
from time import localtime, mktime, time
from typing import Dict, List, Optional, Sequence, Tuple


class _SubNotePage:
    @property
    def cursor(self) -> int:
        return self.__cursor

    @cursor.setter
    def cursor(self, value: int):
        if value >= 0 and value < self.length:
            self.__cursor = value

    @property
    def key_num(self) -> int:
        return len(self.__contents)

    @property
    def length(self) -> int:
        return len(self.__keys)

    @property
    def name(self) -> str:
        return self.__name

    def __init__(self, name: str = ""):
        self.show_more = True

        self.__contents: Dict[str, List[Tuple[str, List[str]]]] = {}
        self.__cursor = 0
        self.__keys: List[str] = []
        self.__name = name

    def add(self, key: Optional[str], value: Tuple[str, Sequence[str]]):
        if not key:
            return

        annotation = value[0]
        content: List[str] = []

        for line in value[1]:
            content.append(line)

        self.__keys.append(key)

        if key not in self.__contents:
            self.__contents[key] = []

        self.__contents[key].append((annotation, content))

    def delete(self, key: Optional[str]):
        if not key:
            return

        if key not in self.__contents:
            return

        while True:
            try:
                self.__keys.remove(key)
            except ValueError:
                break

        self.__contents.pop(key)

    def item_by_key(
            self, key: Optional[str]) -> Optional[List[Tuple[str, List[str]]]]:
        if key not in self.__contents:
            return None

        return self.__contents[key]

    def item_str(self, cursor: Optional[int] = None) -> str:
        if self.length == 0:
            return ""

        if not cursor or cursor < 0 or cursor >= self.length:
            cursor = self.__cursor

        key = self.__keys[cursor]
        values = self.__contents[key]
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

    def keys(self):
        return self.__contents.keys()

    def key_by_cursor(self, cursor: Optional[int] = None) -> Optional[str]:
        if self.length == 0:
            return None

        if not cursor or cursor < 0 or cursor >= self.length:
            cursor = self.__cursor

        return self.__keys[cursor]

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
        if self.in_reviewer:
            return self.__reviewer.cursor

        if self.sub_page_num != 0:
            return self.__sub_pages[self.__index].cursor

    @cursor.setter
    def cursor(self, value: int):
        if self.in_reviewer:
            self.__reviewer.cursor = value

            return

        if self.sub_page_num != 0:
            self.__sub_pages[self.__index].cursor = value

    @property
    def cursors(self) -> List[int]:
        cursors: List[int] = []

        for sub_page in self.__sub_pages:
            cursors.append(sub_page.cursor)

        cursors.append(self.__reviewer.cursor)

        return cursors

    @cursors.setter
    def cursors(self, value: Sequence[int]):
        for index in range(self.sub_page_num
                           if self.sub_page_num <= len(value) else len(value)):
            self.__sub_pages[index].cursor = value[index]

        if self.sub_page_num < len(value):
            self.__reviewer.cursor = value[self.sub_page_num]

    @property
    def index(self) -> int:
        return self.__index

    @index.setter
    def index(self, value: int):
        if self.in_reviewer:
            return

        if value >= 0 and value < self.sub_page_num:
            self.__index = value

    @property
    def key_presented(self) -> Optional[str]:
        sub_page: _SubNotePage = None

        if self.in_reviewer:
            sub_page = self.__reviewer
        else:
            sub_page = self.__sub_pages[self.index]

        return sub_page.key_by_cursor()

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
    def reviewed_num(self) -> int:
        number = 0

        for key in self.__reviewer.keys():
            days_interval = self.__tmstamp_to_days(time()) - int(
                self.__reviewer.item_by_key(key)[0][1][0])

            if days_interval == 0:
                number += 1

        return number

    @property
    def show_more(self) -> bool:
        if self.in_reviewer:
            return self.__reviewer.show_more

        show_more = True

        if self.sub_page_num != 0:
            show_more = self.__sub_pages[self.__index].show_more

        return show_more

    @show_more.setter
    def show_more(self, value: bool):
        if self.in_reviewer:
            self.__reviewer.show_more = value

            return

        if self.sub_page_num != 0:
            self.__sub_pages[self.__index].show_more = value

    @property
    def sub_page_len(self) -> int:
        if self.in_reviewer:
            return self.__reviewer.length

        length = 0

        if self.sub_page_num != 0:
            length = self.__sub_pages[self.__index].length

        return length

    @property
    def sub_page_name(self) -> str:
        if self.in_reviewer:
            return self.__reviewer.name

        if self.sub_page_num != 0:
            return self.__sub_pages[self.__index].name

    @property
    def sub_page_num(self) -> int:
        return len(self.__sub_pages)

    @property
    def unreviewed_num(self) -> int:
        return self.__reviewer.length - self.reviewed_num

    def __init__(self, file_path: str, data_path: str, name: str = ""):
        self.in_reviewer = False

        self.__file_path = file_path
        self.__hidden_reviewer = _SubNotePage(f"{name} Hidden Reviewer")
        self.__index = 0
        self.__name = name
        self.__reviewer = _SubNotePage(f"{name} Reviewer")
        self.__data_path = data_path
        self.__sub_pages: List[_SubNotePage] = []

        self.__load(self.__file_path, self.__data_path)

    def add(self, key: Optional[str], value: Tuple[str, Sequence[str]]):
        if not key:
            return

        if self.in_reviewer:
            self.__reviewer.add(key, value)

            return

        if self.sub_page_num != 0:
            self.__sub_pages[self.__index].add(key, value)

    def close(self):
        if not exists(self.__data_path) or not isfile(self.__data_path):
            dir_name = dirname(self.__data_path)

            if not exists(dir_name):
                makedirs(dir_name)

        with open(self.__data_path, "w") as file:
            string = ""

            string += str(self.index) + "\n"
            string += " ".join(map(str, self.cursors)) + "\n"
            string += str(int(self.in_reviewer)) + "\n"

            for key in self.__reviewer.keys():
                content = self.__reviewer.item_by_key(key)[0][1]

                string += f"{key}\n    {content[0]}\n    {content[1]}\n"

            for key in self.__hidden_reviewer.keys():
                content = self.__hidden_reviewer.item_by_key(key)[0][1]

                string += f"{key}\n    {content[0]}\n    {content[1]}\n"

            file.write(string)

    def delete(self, key: Optional[str]):
        if not key:
            return

        if self.in_reviewer:
            self.__reviewer.delete(key)

            return

        if self.sub_page_num != 0:
            self.__sub_pages[self.__index].delete(key)

    def item_str(self,
                 index: Optional[int] = None,
                 cursor: Optional[int] = None) -> str:
        if self.in_reviewer:
            string = ""
            key = self.__reviewer.key_by_cursor(cursor)
            page_tmp = _SubNotePage()

            if not key:
                return string

            page_tmp.show_more = self.__reviewer.show_more
            self.__review(key)

            for sub_page in self.__sub_pages:
                if key in sub_page.keys():
                    for content_line in sub_page.item_by_key(key):
                        page_tmp.add(key, content_line)

            return string + page_tmp.item_str()

        if self.sub_page_num == 0:
            return ""

        if not index or index < 0 or index >= self.sub_page_num:
            index = self.__index

        self.__view(self.__sub_pages[index].key_by_cursor(cursor))

        return self.__sub_pages[index].item_str(cursor)

    def reset_review(self, key: Optional[str]):
        if not key:
            return

        if key in self.__reviewer.keys():
            self.__reviewer.delete(key)
            self.__hidden_reviewer.add(
                key, ("", [str(self.__tmstamp_to_days(time())), "0"]))
        elif key in self.__hidden_reviewer.keys():
            content = self.__hidden_reviewer.item_by_key(key)[0][1]

            content[0] = str(self.__tmstamp_to_days(time()))
            content[1] = "0"
        else:
            self.__hidden_reviewer.add(
                key, ("", [str(self.__tmstamp_to_days(time())), "0"]))

    def reviewed_today(self, key: Optional[str]) -> bool:
        if not key:
            return False

        content = self.__reviewer.item_by_key(key)[0][1]
        days_recorded = int(content[0])
        days_interval = self.__tmstamp_to_days(time()) - days_recorded

        if days_interval == 0:
            return True
        else:
            return False

    def review_times(self, key: Optional[str]) -> int:
        if not key:
            return 0

        return int(self.__reviewer.item_by_key(key)[0][1][1])

    def __load(self, file_path: str, data_path: str):
        if exists(file_path) and isfile(file_path):
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

        if exists(data_path) and isfile(data_path) and getsize(data_path):
            with open(data_path, "r", encoding="utf-8") as file:
                self_index = int(file.readline())
                self_cursors = list(map(int, file.readline().split()))
                self_in_reviewer = True if int(file.readline()) else False

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

                    days_recorded = int(content[0])
                    review_times = int(content[1])
                    days_interval = self.__tmstamp_to_days(
                        time()) - days_recorded

                    if days_interval == 2**review_times or review_times != 0 and days_interval == 0:
                        self.__reviewer.add(key, (annotation, content))
                    elif review_times != 8 and days_interval > 2**review_times:
                        self.reset_review(key)
                    else:
                        self.__hidden_reviewer.add(key, (annotation, content))

                self.index = self_index
                self.cursors = self_cursors
                self.in_reviewer = self_in_reviewer

    def __review(self, key: Optional[str]):
        if key in self.__reviewer.keys():
            content = self.__reviewer.item_by_key(key)[0][1]

            days_recorded = int(content[0])
            review_times = int(content[1])
            days_interval = self.__tmstamp_to_days(time()) - days_recorded

            if days_interval > 0 and review_times != 8:
                content[0] = str(self.__tmstamp_to_days(time()))
                content[1] = str(review_times + 1)

    def __tmstamp_to_days(self, tmstamp: float) -> int:
        lctime = localtime(tmstamp)
        new_tmstamp = mktime((lctime[0], lctime[1], lctime[2], 0, 0, 0,
                              lctime[6], lctime[7], lctime[8]))

        return int(new_tmstamp / 86400)

    def __view(self, key: Optional[str]):
        if not key:
            return

        if key not in self.__reviewer.keys(
        ) and key not in self.__hidden_reviewer.keys():
            self.__hidden_reviewer.add(
                key, ("", [str(self.__tmstamp_to_days(time())), "0"]))
