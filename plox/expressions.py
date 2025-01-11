from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Final
from plox.token import Token


class Expr(ABC):
    @abstractmethod
    def accept(self):
        pass


@dataclass
class Binary(Expr):
    left: Final[Expr]
    operator: Final[Token]
    right: Final[Expr]


@dataclass
class Grouping(Expr):
    expression: Final[Expr]


@dataclass
class Literal(Expr):
    value: Final[object]


@dataclass
class Unary(Expr):
    operator: Final[Token]
    right: Final[Expr]


@dataclass
class Variable(Expr):
    name: Final[Token]
