from typing import Final
from plox.token import Token
from plox.token_type import ONE_OR_MORE_CHARS, SINGLE_CHARS, TokenType
import logging

logger = logging.getLogger(__name__)


class Scanner:
    def __init__(self, source: str) -> None:
        self.source: Final[str] = source
        self.tokens: Final[list[Token]] = []
        self.current: int = 0
        self.start: int = 0
        self.line: int = 1

    def is_at_end(self):
        return self.current >= len(self.source)

    def scan_tokens(self) -> list[Token]:
        while not self.is_at_end():
            self.start = self.current
            self.scan_token()

        self.tokens.append(Token(TokenType.EOF, "", None, self.line))
        print(self.tokens)
        return self.tokens

    def advance(self) -> str:
        if self.current <= len(self.source):
            new_value = self.source[self.current]
            self.current += 1
            return new_value
        else:
            return "\0"

    def match(self, expected: str) -> bool:
        if self.is_at_end() or self.source[self.current] != expected:
            return False

        self.current += 1
        return True

    def peek(self):
        if self.is_at_end():
            return "\0"
        return self.source[self.current]

    def scan_token(self):
        c: str = self.advance()
        try:
            if c in SINGLE_CHARS:
                self.add_token(TokenType(c))
            elif c in ONE_OR_MORE_CHARS:
                components = [i for i in ONE_OR_MORE_CHARS if i.startswith(c)]
                self.add_token(TokenType(components[1] if self.match("=") else components[0]))
            elif c == "/":
                if self.match("/"):
                    while self.peek() != "\n" and self.is_at_end() is not True:
                        self.advance()
                    return
                else:
                    self.add_token(TokenType.SLASH)
            elif c == " " or c == "\r" or c == "\t":
                return
            elif c == "\n":
                self.line += 1
                return

        except ValueError as e:
            logger.info("source of error: %s", self.source)
            raise ValueError(f"unexpected character on {self.line}: {e}") from e

    def add_token(self, type: TokenType, litral: object = None):
        text = self.source[self.start : self.current]
        self.tokens.append(Token(type, text, litral, self.line))