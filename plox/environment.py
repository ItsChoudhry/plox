from typing import Optional

from plox.token import Token
from typing import Any


class Environment:
    values: dict[str, Any] = {}

    def define(self, name: str, value: Optional[Any]):
        Environment.values[name] = value

    def get(self, name: Token) -> Any:
        if name.lexeme in Environment.values:
            return Environment.values[name.lexeme]

        raise RuntimeError("Undefined variable '" + name.lexeme + "'.")
