from typing import MutableSequence


class Item:
    def __init__(self, key: str, values: MutableSequence[str]):
        self.key = key
        self.values = values

    def __str__(self):
        string = ""

        string += self.key + "\n"
        for value in self.values:
            string += "    " + value + "\n"

        return string
