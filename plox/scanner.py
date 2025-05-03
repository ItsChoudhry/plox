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

    def is_at_end(self) -> bool:
        return self.current >= len(self.source)

    def scan_tokens(self) -> list[Token]:
        while not self.is_at_end():
            self.start = self.current
            self.scan_token()

        self.tokens.append(Token(TokenType.EOF, "", None, self.line))
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

    def peek(self) -> str:
        if self.is_at_end():
            return "\0"
        return self.source[self.current]

    def peek_next(self) -> str:
        if self.current + 1 >= len(self.source):
            return "\0"
        return self.source[self.current + 1]

    def string(self) -> None:
        while self.peek() != '"' and not self.is_at_end():
            if self.peek() == "\n":
                self.line += 1
            self.advance()

        if self.is_at_end():
            logger.error("%s unterminated string.", self.line)
            return
        self.advance()

        value = self.source[self.start + 1 : self.current - 1]
        self.add_token(TokenType.STRING, value)

    def number(self) -> None:
        while self.peek().isdigit():
            self.advance()
        if self.peek() == "." and self.peek_next().isdigit():
            self.advance()
            while self.peek().isdigit():
                self.advance()
        self.add_token(TokenType.NUMBER, float(self.source[self.start : self.current]))

    def identifier(self):
        while self.peek().isalnum():
            self.advance()

        text = self.source[self.start : self.current]
        type: TokenType = TokenType.IDENTIFIER if text not in TokenType else TokenType(text)
        self.add_token(type)

    def multi_line_comment(self) -> None:
        while self.peek() != "*" and not self.is_at_end():
            if self.peek() == "\n":
                self.line += 1
            self.advance()

        if not self.is_at_end() and self.peek_next() == "/":
            self.advance()
            self.advance()
        else:
            raise Exception("unterminated comment on line: %s", self.line)  # noqa: TRY002

    def scan_token(self) -> None:
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
                elif self.match("*"):
                    self.multi_line_comment()
                else:
                    self.add_token(TokenType.SLASH)
            elif c == " " or c == "\r" or c == "\t":
                return
            elif c == "\n":
                self.line += 1
                return
            elif c == '"':
                self.string()
            elif c.isdigit():
                self.number()
            elif c.isalpha():
                self.identifier()

        except ValueError as e:
            logger.error("source of error: %s", self.source)
            raise ValueError(f"unexpected character on {self.line}: {e}") from e

    def add_token(self, type: TokenType, litral: object = None) -> None:
        text = self.source[self.start : self.current]
        self.tokens.append(Token(type, text, litral, self.line))
