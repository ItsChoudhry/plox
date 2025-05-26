from typing import Optional, Self

from plox.token import Token
from typing import Any


class Environment:
    def __init__(self, enclosing: Self | None = None):
        self.enclosing = enclosing
        self.values: dict[str, Any] = {}

    def define(self, name: str, value: Optional[Any]):
        self.values[name] = value

    def get(self, name: Token) -> Any:
        if name.lexeme in self.values:
            if (value := self.values[name.lexeme]) is not None:
                return value
            else:
                raise RuntimeError("Unassigned variable '" + name.lexeme + "'.")

        if self.enclosing:
            return self.enclosing.get(name)

        raise RuntimeError("Undefined variable '" + name.lexeme + "'.")

    def assign(self, name: Token, value: Any):
        if name.lexeme in self.values:
            self.values[name.lexeme] = value
            return

        if self.enclosing:
            return self.enclosing.assign(name, value)

        raise RuntimeError("Undefined variable '" + name.lexeme + "'.")

    def get_at(self, distance: int, name: str):
        return self.ancestor(distance).values[name]

    def assign_at(self, distance: int, name: Token, value: Any):
        self.ancestor(distance).values[name.lexeme] = value

    def ancestor(self, distance: int):
        environment: Environment = self

        for i in range(distance):
            environment = environment.enclosing

        return environment
