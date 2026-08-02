import shlex
from typing import List

class TokenType:
    WORD = "WORD"
    PIPE = "PIPE"
    REDIRECT_OUT = "REDIRECT_OUT"       # >
    REDIRECT_APPEND = "REDIRECT_APPEND"   # >>
    REDIRECT_IN = "REDIRECT_IN"         # <
    BACKGROUND = "BACKGROUND"           # &

class Token:
    def __init__(self, token_type: str, value: str):
        self.type = token_type
        self.value = value

    def __repr__(self):
        return f"Token({self.type}, {repr(self.value)})"

    def __eq__(self, other):
        if isinstance(other, Token):
            return self.type == other.type and self.value == other.value
        return False

def tokenize(input_string: str) -> List[Token]:
    """
    Tokenize raw shell input into structured tokens.
    Handles quotes, pipes, redirection operators, and background flags.
    """
    if not input_string or not input_string.strip():
        return []

    tokens: List[Token] = []
    i = 0
    length = len(input_string)

    while i < length:
        ch = input_string[i]

        # Skip whitespace
        if ch.isspace():
            i += 1
            continue

        # Check operators
        if ch == '|':
            tokens.append(Token(TokenType.PIPE, "|"))
            i += 1
            continue

        if ch == '>':
            if i + 1 < length and input_string[i + 1] == '>':
                tokens.append(Token(TokenType.REDIRECT_APPEND, ">>"))
                i += 2
            else:
                tokens.append(Token(TokenType.REDIRECT_OUT, ">"))
                i += 1
            continue

        if ch == '<':
            tokens.append(Token(TokenType.REDIRECT_IN, "<"))
            i += 1
            continue

        if ch == '&':
            tokens.append(Token(TokenType.BACKGROUND, "&"))
            i += 1
            continue

        # Word parsing (handles quotes and escaped chars)
        word_buf = []
        in_quote = None  # None, '"', or "'"

        while i < length:
            c = input_string[i]

            if in_quote:
                if c == in_quote:
                    in_quote = None
                else:
                    word_buf.append(c)
                i += 1
            else:
                if c in ('"', "'"):
                    in_quote = c
                    i += 1
                elif c.isspace() or c in ('|', '>', '<', '&'):
                    break
                elif c == '\\' and i + 1 < length:
                    word_buf.append(input_string[i + 1])
                    i += 2
                else:
                    word_buf.append(c)
                    i += 1

        if word_buf:
            tokens.append(Token(TokenType.WORD, "".join(word_buf)))

    return tokens
