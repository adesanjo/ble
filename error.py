################
# UTILS
################


def stringWithArrows(text, pos_start, pos_end):
    result = ""

    # Calculate indices
    idx_start = max(text.rfind("\n", 0, pos_start.idx), 0)
    idx_end = text.find("\n", idx_start + 1)
    if idx_end < 0:
        idx_end = len(text)

    # Generate each line
    line_count = pos_end.ln - pos_start.ln + 1
    for i in range(line_count):
        # Calculate line columns
        line = text[idx_start:idx_end]
        col_start = pos_start.col if i == 0 else 0
        col_end = pos_end.col if i == line_count - 1 else len(line) - 1

        # Append to result
        result += line + "\n"
        result += " " * col_start + "^" * (col_end - col_start)

        # Re-calculate indices
        idx_start = idx_end
        idx_end = text.find("\n", idx_start + 1)
        if idx_end < 0:
            idx_end = len(text)

    return result.replace("\t", "")


################
# ERRORS
################


class Error:
    def __init__(self, startPos, endPos, name, details):
        self.startPos = startPos
        self.endPos = endPos
        self.name = name
        self.details = details

    def __repr__(self):
        res = f"{self.name}: {self.details}\n"
        res += f"File {self.startPos.fn}, line {self.startPos.ln + 1}\n\n"
        res += stringWithArrows(self.startPos.ftxt, self.startPos, self.endPos)
        return res + "\n"


class IllegalCharError(Error):
    def __init__(self, startPos, endPos, details):
        super().__init__(startPos, endPos, "Illegal Character", details)


class ExpectedCharError(Error):
    def __init__(self, startPos, endPos, details):
        super().__init__(startPos, endPos, "Expected Character", details)


class InvalidSyntaxError(Error):
    def __init__(self, startPos, endPos, details):
        super().__init__(startPos, endPos, "Invalid Syntax", details)


class RTError(Error):
    def __init__(self, startPos, endPos, details, context):
        super().__init__(startPos, endPos, "Runtime Error", details)
        self.context = context

    def generateTraceback(self):
        res = ""
        pos = self.startPos
        ctx = self.context

        while ctx:
            oldRes = res
            res = f"  File {pos.fn}, line {pos.ln + 1}, in {ctx.displayName}\n"
            res += oldRes
            pos = ctx.parentEntryPos
            ctx = ctx.parent

        return "Traceback (most recent call last):\n" + res

    def __repr__(self):
        res = self.generateTraceback()
        res += f"{self.name}: {self.details}\n"
        res += stringWithArrows(self.startPos.ftxt, self.startPos, self.endPos)
        return res + "\n"


################
# POSITION
################


class Position:
    def __init__(self, idx, ln, col, fn, ftxt):
        self.idx = idx
        self.ln = ln
        self.col = col
        self.fn = fn
        self.ftxt = ftxt

    def advance(self, char=None):
        self.idx += 1
        self.col += 1
        if char == "\n":
            self.ln += 1
            self.col = 0

        return self

    def copy(self):
        return Position(self.idx, self.ln, self.col, self.fn, self.ftxt)