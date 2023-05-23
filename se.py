#!/usr/bin/env python3
from enum import Enum, auto

# Modify this to your liking
class Config:
    newlines = ("\n", "\r\n")
    default_newline = newlines[0]
    tab_size = 4


class Selection:
    def __init__(self, start: int = 0, end: int = 1, offset: int = 1):
        self.start = start
        self.end = end
        self.chars_into_line = offset


class LineDir(Enum):
    Up = auto()
    Down = auto()
    Left = auto()
    Right = auto()


# This class allows modification of selections and the text itself, according 
# to any given selections.
class Text:
    def __init__(self, path: str = None):
        self.newline = Config.default_newline
        self.data = self.newline
        self.path = path

        self.read()

    def read(self):
        try:
            with open(self.path, "r") as f:
                self.data = f.read()
        except FileNotFoundError:
            self.write()

    def write(self):
        with open(self.path, "w") as f:
            f.write(self.data)
    
    # Return text in `select`
    def selected_text(self, select: Selection) -> str:
        return self.data[select.start : select.end]

    # Return the line select.start is currently on.
    def line_num(self, select: Selection) -> int:
        # Count the number of newline characters before the start of the selection.
        return self.data.count(self.newline, 0, select.start)

    # Move the `select` to a specific line and/or char in the data.
    def line(self, select: Selection, line_num: int, x_pos: int = 1, cache: [str] = None) -> Selection:

        # temporarily create a list of lines of text, or use the cache
        lines = cache
        if not cache:
            lines = self.data.split(self.newline)[:-1]

        # use the correct line (wrap lines around max)
        line_num %= len(lines)

        # if specified, set the x starting pos
        if x_pos > 1:
            select.chars_into_line = x_pos

        chars_into_line = select.chars_into_line
        if chars_into_line < 1:
            offset = 1 - (chars_into_line + 1)
            l = (line_num - 1) % len(lines)
            select.chars_into_line = len(lines[l]) - offset

            return self.line(select, l, cache=lines)

        elif chars_into_line > len(lines[line_num]):
            cur_len = len(lines[line_num])
            select.chars_into_line = chars_into_line - cur_len

            return self.line(select, (line_num + 1) % len(lines), cache=lines)

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

    # Move around the given selection using deltas instead of absolute values.
    def line_delta(self, select: Selection, direction: LineDir, delta: int = 1) -> Selection:
        delta = abs(delta)
        if direction in LineDir:
            if direction in (LineDir.Up, LineDir.Left):
                delta = -delta

            if direction in (LineDir.Up, LineDir.Down):
                return self.line(select, self.line_num(select) + delta)

            elif direction in (LineDir.Left, LineDir.Right):
                select.chars_into_line += delta
                return self.line(select, self.line_num(select))
        else:
            raise ValueError("Wrong direction specified.")

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

sel = t.line_delta(sel, LineDir.Down, delta=2)
sel = t.line(sel, line_num=0, x_pos=4)
# sel = t.line_delta(sel, LineDir.Right, 3)

print(f"cur line: {t.line_num(sel)}")

print(sel.__dict__)
print(f"'{t.selected_text(sel)}'")
