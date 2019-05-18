import string

from error import Position, IllegalCharError, ExpectedCharError
from tokens import *

################
# CONSTANTS
################

DIGITS = "0123456789"
LETTERS = string.ascii_letters + "_"
LETTERS_DIGITS = LETTERS + DIGITS

################
# TOKENS
################

KEYWORDS = [
    "class",
    "include",
    "as",
    "and",
    "or",
    "not",
    "if",
    "then",
    "elif",
    "else",
    "for",
    "to",
    "step",
    "each",
    "in",
    "while",
    "do",
    "fn",
    "disp",
    "input",
    "rand",
    "int",
    "float",
    "str",
    "mut",
    "at",
    "type",
    "read",
    "write"
]


class Token:
    def __init__(self, type_, value=None, startPos=None, endPos=None):
        self.type = type_
        self.value = value
        self.startPos = None
        self.endPos = None
        if startPos:
            self.startPos = startPos.copy()
            self.endPos = startPos.copy()
            self.endPos.advance()
        if endPos:
            self.endPos = endPos.copy()

    def matches(self, tknType, tknValue):
        return self.type == tknType and self.value == tknValue

    def __repr__(self):
        if self.value is not None:
            return f"{self.type}:{self.value}"
        return f"{self.type}"


################
# LEXER
################


class Lexer:
    def __init__(self, fn, text, module):
        self.fn = fn
        self.text = text
        self.module = module
        self.pos = Position(-1, 0, -1, fn, text, module)
        self.char = None
        self.advance()

    def advance(self):
        self.pos.advance(self.char)
        if self.pos.idx < len(self.text):
            self.char = self.text[self.pos.idx]
        else:
            self.char = None

    def makeTokens(self):
        tokens = []

        while self.char is not None:
            if self.char in " \t\r\n":
                self.advance()
            elif self.char in DIGITS:
                tokens.append(self.makeNumber())
            elif self.char in LETTERS:
                tokens.append(self.makeIdentifier())
            elif self.char == "\"":
                tokens.append(self.makeString())
            elif self.char == "#":
                while self.char is not None and self.char != "\n":
                    self.advance()
            elif self.char == ".":
                tokens.append(Token(TT_DOT, startPos=self.pos))
                self.advance()
            elif self.char == "+":
                tokens.append(Token(TT_PLUS, startPos=self.pos))
                self.advance()
            elif self.char == "-":
                tokens.append(Token(TT_MINUS, startPos=self.pos))
                self.advance()
            elif self.char == "*":
                tokens.append(Token(TT_MUL, startPos=self.pos))
                self.advance()
            elif self.char == "/":
                tokens.append(Token(TT_DIV, startPos=self.pos))
                self.advance()
            elif self.char == "%":
                tokens.append(Token(TT_MOD, startPos=self.pos))
                self.advance()
            elif self.char == "^":
                tokens.append(Token(TT_POW, startPos=self.pos))
                self.advance()
            elif self.char == "(":
                tokens.append(Token(TT_LPAREN, startPos=self.pos))
                self.advance()
            elif self.char == ")":
                tokens.append(Token(TT_RPAREN, startPos=self.pos))
                self.advance()
            elif self.char == ":":
                tokens.append(Token(TT_COLON, startPos=self.pos))
                self.advance()
            elif self.char == "!":
                tkn, err = self.makeNotEquals()
                if err:
                    return [], err
                tokens.append(tkn)
            elif self.char == "=":
                tokens.append(self.makeEquals())
            elif self.char == "<":
                tokens.append(self.makeLessThan())
            elif self.char == ">":
                tokens.append(self.makeGreaterThan())
            elif self.char == "[":
                tokens.append(Token(TT_LSQBRACKET, startPos=self.pos))
                self.advance()
            elif self.char == "]":
                tokens.append(Token(TT_RSQBRACKET, startPos=self.pos))
                self.advance()
            elif self.char == ",":
                tokens.append(Token(TT_COMMA, startPos=self.pos))
                self.advance()
            elif self.char == "{":
                tokens.append(Token(TT_LBRACKET, startPos=self.pos))
                self.advance()
            elif self.char == "}":
                tokens.append(Token(TT_RBRACKET, startPos=self.pos))
                self.advance()
            elif self.char == ";":
                tokens.append(Token(TT_SEMICOLON, startPos=self.pos))
                self.advance()
            else:
                startPos = self.pos.copy()
                char = self.char
                self.advance()
                return [], IllegalCharError(startPos, self.pos, f"'{char}'")

        tokens.append(Token(TT_EOF, startPos=self.pos))
        return tokens, None

    def makeNumber(self):
        numStr = ""
        hasDot = False
        startPos = self.pos.copy()

        while self.char is not None and self.char in DIGITS + ".":
            if self.char == ".":
                if hasDot:
                    break
                hasDot = True
            numStr += self.char
            self.advance()

        if hasDot:
            return Token(TT_FLOAT, float(numStr), startPos, self.pos)
        return Token(TT_INT, int(numStr), startPos, self.pos)

    def makeIdentifier(self):
        idStr = ""
        startPos = self.pos.copy()

        while self.char is not None and self.char in LETTERS_DIGITS:
            idStr += self.char
            self.advance()

        if idStr in KEYWORDS:
            tknType = TT_KEYWORD
        else:
            tknType = TT_IDENTIFIER
        return Token(tknType, idStr, startPos, self.pos)
    
    def makeString(self):
        string = ""
        startPos = self.pos.copy()
        
        escapeChars = {
            "n": "\n",
            "t": "\t",
            "r": "\r"
        }
        
        self.advance()
        while self.char is not None and self.char != "\"":
            if self.char == "\\":
                self.advance()
                if self.char in escapeChars:
                    string += escapeChars[self.char]
                else:
                    string += self.char
            else:
                string += self.char
            self.advance()
        self.advance()
        
        return Token(TT_STRING, string, startPos, self.pos)

    def makeNotEquals(self):
        startPos = self.pos.copy()
        self.advance()
        if self.char == "=":
            self.advance()
            return Token(TT_NE, startPos=startPos, endPos=self.pos), None
        self.advance()
        return None, ExpectedCharError(
            startPos, self.pos,
            "'=' (after '!')"
        )

    def makeEquals(self):
        tknType = TT_EQ
        startPos = self.pos.copy()
        self.advance()
        if self.char == "=":
            self.advance()
            tknType = TT_EE
        return Token(tknType, startPos=startPos, endPos=self.pos)

    def makeLessThan(self):
        tknType = TT_LT
        startPos = self.pos.copy()
        self.advance()
        if self.char == "=":
            self.advance()
            tknType = TT_LTE
        return Token(tknType, startPos=startPos, endPos=self.pos)

    def makeGreaterThan(self):
        tknType = TT_GT
        startPos = self.pos.copy()
        self.advance()
        if self.char == "=":
            self.advance()
            tknType = TT_GTE
        return Token(tknType, startPos=startPos, endPos=self.pos)
