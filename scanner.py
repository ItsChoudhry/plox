from typing import Final
from .token import Token
from .token_type import TokenType


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

        self.tokens.append(Token(TokenType.EOF, "", None, self.line))
        return self.tokens