#!/bin/env python3
# somedit - a small text editor
"""
MAIN IDEA:
everything should be relative, there should just be a two positions a start and stop
position of the cursor.
There sould also be support for multiple of these selections

It should only include the features that I ACTUALLY USE. SHOULDN'T be a complete framework for EVERYTHING.
"""


class Selection:
    def __init__(self, start: int = 0, end: int = 0):
        self.start = start
        self.end = end

        self.wish_x_start = None


class Text:
    def __init__(self, filename: str, newline: str = "\n"):
        self.filename = filename
        self.newline = newline

        self.text: str = newline

    def read(self) -> None:
        try:
            with open(self.filename) as f:
                self.text = f.read()
        except FileNotFoundError:
            self.write()
        finally:
            self.add_newline()

    def write(self) -> None:
        with open(self.filename, "w") as f:
            f.write(self.text)

    # Add the newline char if needed
    def add_newline(self) -> None:
        if not self.text.endswith(self.newline):
            self.text += "\n"

    # Insert `what` at `location` and return `what` length
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

    # move selection to the next newline
    def go_line(self, line: int, stay_x: bool = True) -> Selection:
        pass

    def prev_newline_idx(self, select: Selection) -> int or None:
        result = self.text[: select.start].rfind(self.newline)
        return result if not result == -1 else 0

    def next_newline_idx(self, select: Selection) -> int:
        result = self.text[select.start :].find(self.newline)
        return result if not result == -1 else len(self.text) - 1

    def go_line_up(self, select: Selection) -> Selection:
        """
        012345
        ABOVEn

        678
        ABn

        9 10 11 12 13 14
        C D  E  F  G  n
             ^
        """
        prev_newline_idx = self.prev_newline_idx(select)
        prev_prev_newline_idx = self.prev_newline_idx(Selection(prev_newline_idx))

        above_line_len = prev_newline_idx - prev_prev_newline_idx
        if above_line_len:
            above_line_len -= 1

        chars_into_line = select.start - prev_newline_idx
        print("above", above_line_len)
        print("chars", chars_into_line)

        if select.wish_x_start and select.wish_x_start <= above_line_len:
            new_select = Selection(prev_prev_newline_idx + select.wish_x_start)
            print("restored wish")
        else:
            if above_line_len < chars_into_line:
                # want to move n chars into line, but we can't since the line is
                # smaller than our current position.
                # -> set wish_x_start to that position
                new_select = Selection(prev_newline_idx)
                new_select.wish_x_start = chars_into_line
                print("set wish")
            else:
                # -1 so we don't end up with the cursor ON the newline
                new_select = Selection(prev_prev_newline_idx + chars_into_line)
                print("normal")

        new_select.end = new_select.start + (select.end - select.start)
        return new_select


T = Text(None)
# T.text = "ABOVE\nAB\nCDEFG\n"
T.text = "\nABCD\n"
select = Selection(2, 3)
print(T.text[select.start : select.end])
# print(T.text[: select.start].replace("\n", "n"))
# print(T.text[select.start :].replace("\n", "n"))

print("initial selection: ", select.__dict__)
ret = T.go_line_up(select)
print("new selection: ", ret.__dict__)

ret = T.go_line_up(ret)
print("new selection: ", ret.__dict__)
# T.insert(ret, "TEST")
# print(T.text.replace('\n', 'n'))

# print(T.text[ret.start : ret.end].replace('\n', 'n'))

# ret = T.go_line_up(ret)
# print("new selection: ", ret.__dict__)

# ret = T.go_line_up(ret)
# print("new selection: ", ret.__dict__)
