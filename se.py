#!/usr/bin/env python3
from enum import Enum, auto
from pathlib import Path
import re

# Modify this to your liking
class Config:
    # how tabs (\t) should be represented
    tab_size = 4


class Selection:
    def __init__(self, start: int = 0, end: int = 1, wish_x: int = None):
        self.start = start
        self.end = end

        self.wish_x = wish_x


class FindMode(Enum):
    Global = auto()
    Below = auto()
    In = auto()
    Above = auto()


# This class allows modification of selections and the text itself, according
# to any given selections.
class Text:
    def __init__(self, path: Path = None):
        self.data = "\n"
        self.path = path


    def read(self):
        if self.path:
            try:
                self.data = self.path.read_text()
                # re-encode all the newline breaks to be uniform \n's
                self.data = "\n".join(self.data.splitlines()) + "\n"
            except FileNotFoundError:
                pass
        self.write()

    def write(self):
        self.path.write_text(self.data)

    # Return text range by `select`
    def selected_text(self, select: Selection) -> str:
        return self.data[select.start : select.end]

    def line_lengths(self) -> [int]:
        return list(map(len, self.data.splitlines()))

    def convert_yx_to_sel(self, select: Selection, y: int, x: int, line_lengths: [int] = None) -> Selection:
        if not line_lengths:
            line_lengths = self.line_lengths()

        if select.wish_x is not None and select.wish_x < line_lengths[y]:
            x = select.wish_x
            select.wish_x = None
        elif x >= line_lengths[y]:
            x = line_lengths[y] - 1
            select.wish_x = x

        selection_length = select.end - select.start

        select.start = sum(line_lengths[:y]) + y + x
        select.end = select.start + selection_length

        return select

    def current_yx(self, index: int, line_lengths: [int] = None, human = False) -> (int, int):
        if not line_lengths:
            line_lengths = self.line_lengths()

        total_length = sum(line_lengths)

        # as a safty measure
        index %= total_length + 1

        line_start = 0
        for i, line_length in enumerate(line_lengths):
            line_end = line_start + line_length
            if index < line_end:
                if human:
                    i += 1 ; index += 1
                return i, index - line_start
            line_start = line_end + 1

    def goto(self, select: Selection, y: int = 0, x: int = 0, dy: int = 0, dx: int = 0) -> Selection:
        line_lengths = self.line_lengths()

        if dy or dx:
            current_y, current_x = self.current_yx(select.start, line_lengths)
            y += current_y + dy
            x += current_x + dx

        y %= len(line_lengths) + 1
        x %= line_lengths[y]

        new_select = self.convert_yx_to_sel(select, y, x, line_lengths)
        return new_select

    # Insert `what` at `location` and return length of `what`
    def insert(self, select: Selection, what: str) -> int:
        self.data = self.data[: select.start] + what + self.data[select.start :]
        return len(what)

    # Delete the text from range provided with `selection`
    def delete(self, select: Selection) -> None:
        self.data = self.data[: select.start] + self.data[select.end :]

    # Wrapper around insert & delete
    def replace(self, select: Selection, With: str) -> None:
        self.delete(select)
        self.insert(select, With)

    # Modes: find below, IN, above the selection OR globally.
    def find(self, mode: FindMode = FindMode.Global, expr: str = "", select: Selection = None) -> [Selection]:
        match mode:
            case FindMode.Global:
                area = self.data
                start = 0

            case FindMode.Below:
                area = self.data[select.end :]
                start = select.end

            case FindMode.In:
                area = self.selected_text(select)
                start = select.start

            case FindMode.Above:
                area = self.data[: select.start]
                start = 0

            case _:
                raise TypeError("Invalid FindMode specified.")

        matches = [select]
        try:
            ctx = re.compile(expr)
            matches = [Selection(m.start() + start, m.end() + start) for m in ctx.finditer(area)]
            # TODO: implement messages
            #if not matches:
            #    self.ui.message.put(Message.Error, "No Matches found.")
            #    pass
        except re.error as err:
            self.ui.message.put(Message.Error, f"Bad expression: {err}")

        return matches

# Example usage:
select = Selection(0, 5)
t = Text("test.txt")

select = t.goto(select, dy=0, dx=0)
print(t.selected_text(select))
print(select.__dict__)

matches = t.find(FindMode.Below, "*", select)
for match in matches:
    print("Matched:", t.selected_text(match))

if __name__ == "__main__":
    # init UI, ncurses, main loop
    pass
