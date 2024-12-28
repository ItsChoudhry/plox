from typing import Final
from .token_type import TokenType


class Token:
    def __init__(self, type: TokenType, lexeme: str, literal: object, line: int):
        self.type: Final[TokenType] = type
        self.lexeme: Final[str] = lexeme
        self.literal: Final[object] = literal
        self.line: Final[int] = line

    def __str__(self):
        return f"{self.type} {self.lexeme} {self.literal}"
