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
    def __init__(self, start: int = 0, end: int = 0, wish: int = None):
        self.start = start
        self.end = end
        self.wish_x_start = wish


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
            if not self.text.endswith(self.newline):
                self.text += "\n"

    def write(self) -> None:
        with open(self.filename, "w") as f:
            f.write(self.text)

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

        if prev_newline_idx == prev_prev_newline_idx:
            print("STH WRONG, THE END OR START REACHED")
            return select

        above_line_len = prev_newline_idx - prev_prev_newline_idx
        chars_into_line = select.start - prev_newline_idx
        
        # Is a wish set, and is it valid?
        if select.wish_x_start and select.wish_x_start <= above_line_len:
            new_select = Selection(prev_prev_newline_idx + select.wish_x_start-1)

        # Can I move up one line at my current chars_into_line position?
        elif above_line_len < chars_into_line:
            # No I can't, but I'd wish to
            new_select = Selection(prev_newline_idx-1)
            new_select.wish_x_start = chars_into_line
        else:
            # Yes I can.
            # -1 so we don't end up with the cursor ON the newline
            new_select = Selection(prev_prev_newline_idx + chars_into_line-1)

        new_select.end = new_select.start + (select.end - select.start)
        return new_select

T = Text(None)
T.text = "ABOVE\nAB\nCDEFG\n"
select = Selection(11, 12)

print(T.text[select.start : select.end])
print("initial selection: ", select.__dict__)
print(T.text.replace('\n', 'n'))

def do_test(n, sel):
    for _ in range(n):
        sel = T.go_line_up(sel)
        print("new selection: ", sel.__dict__)
        print(T.text[sel.start : sel.end].replace('\n', 'n'))
    return sel

select = do_test(4, select)
T.replace(select, "!")
print(T.text.replace('\n', 'n'))
