from typing import Optional

from plox.token import Token
from typing import Any


class Environment:
    values: dict[str, object]

    def define(self, name: str, value: Optional[Any]):
        self.values[name] = value

    def get(self, name: Token):
        if name.lexeme in self.values:
            return self.values[name.lexeme]

        raise RuntimeError(name, "Undefined variable '" + name.lexeme + "'.")
