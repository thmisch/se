#!/usr/bin/env python3
from enum import Enum, auto

# Modify this to your liking
class Config:
    newlines = ("\n", "\r\n")
    default_newline = newlines[0]
    tabsize = 4


class Selection:
    def __init__(self, start: int = 0, end: int = 1, offset: int = 1):
        self.start = start
        self.end = end
        self.chars_into_line = offset


class Text:
    def __init__(self, path: str = None):
        self.newline = Config.default_newline
        self.data = self.newline
        self.path = path

        self.read()

    class LineDir(Enum):
        Up = auto()
        Down = auto()

    class OnLineDir(Enum):
        Left = auto()
        Right = auto()

    def read(self):
        try:
            with open(self.path, "r") as f:
                self.data = f.read()
        except FileNotFoundError:
            self.write()

    def write(self):
        with open(self.path, "w") as f:
            f.write(self.data)

    def selected_text(self, select: Selection) -> str:
        return self.data[select.start : select.end]

    # Return the line select.start is currently on.
    def line_num(self, select: Selection) -> int:
        # Count the number of newline characters before the start of the selection.
        return self.data.count(self.newline, 0, select.start)

    # Move the selection to a specific line in the data.
    def line(self, select: Selection, line_num: int, line_cache: [str] = None) -> Selection:
        lines = line_cache
        if not line_cache:
            lines = self.data.split(self.newline)[:-1]

        # use the correct line
        if line_num < 0:
            line_num = 0
        elif line_num >= len(lines):
            line_num = len(lines) - 1

        chars_into_line = select.chars_into_line
        if chars_into_line < 1:
            offset = 1 - (chars_into_line + 1)
            l = (line_num - 1) % len(lines)
            select.chars_into_line = len(lines[l]) - offset

            return self.line(select, l, lines)

        elif chars_into_line > len(lines[line_num]):
            cur_len = len(lines[line_num])
            select.chars_into_line = chars_into_line - cur_len

            return self.line(select, (line_num + 1) % len(lines), lines)

        # find the starting index of `line_num`
        start = chars_into_line - 1  # -1 since start is an index, and chars_into_line is not
        for i in range(line_num):
            start += len(lines[i]) + len(self.newline)

        # update end of selection
        end = start + (select.end - select.start)

        # we never want the end to exceed the actual file length
        max_len = len(self.data) - len(self.newline)
        if end > max_len:
            end = max_len

        return Selection(start, end, select.chars_into_line)

    def line_delta(self, select: Selection, direction: LineDir, delta: int = 1) -> Selection:
        delta = abs(delta)
        if direction == self.LineDir.Up:
            delta = -delta
        return self.line(select, self.line_num(select) + delta)

    # Set the x starting position of the selection
    def line_x(self, select: Selection, x: int) -> Selection:
        select.chars_into_line = x
        return self.line_delta(select, None, 0)

    def line_x_delta(self, select: Selection, direction: OnLineDir, delta: int = 1) -> Selection:
        delta = abs(delta)
        if direction == self.OnLineDir.Left:
            delta = -delta
        return self.line_x(select, select.chars_into_line + delta)

    # Insert `what` at `location` and return length of `what`
    def insert(self, select: Selection, what: str) -> int:
        self.text = self.text[: select.start] + what + self.text[select.start :]
        return len(what)

    # Delete the text from range provided with `selection`
    def delete(self, select: Selection) -> None:
        self.text = self.text[: select.start] + self.text[select.end :]

    # Wrapper around insert & delete
    def replace(self, select: Selection, what: str) -> None:
        self.delete(select)
        self.insert(select, what)


sel = Selection(0, 2, 1)
print(sel.__dict__)
t = Text("test.txt")
"""
0123
ABC

456
DE

789 10
YOh
"""
print(f"'{t.selected_text(sel)}'")
print(f"cur line: {t.line_num(sel)}")

sel = t.line_x_delta(sel, t.OnLineDir.Left, 2)

print(f"cur line: {t.line_num(sel)}")

print(sel.__dict__)
print(f"'{t.selected_text(sel)}'")
