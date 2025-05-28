from dataclasses import dataclass
from typing import Any
from plox.token import Token


class Expr:
    pass


@dataclass(unsafe_hash=True)
class Binary(Expr):
    left: Expr
    operator: Token
    right: Expr


@dataclass(unsafe_hash=True)
class Grouping(Expr):
    expression: Expr


@dataclass(unsafe_hash=True)
class Literal(Expr):
    value: Any


@dataclass(unsafe_hash=True)
class Unary(Expr):
    operator: Token
    right: Expr


@dataclass(unsafe_hash=True)
class Variable(Expr):
    name: Token


@dataclass(unsafe_hash=True)
class Assign(Expr):
    name: Token
    value: Expr


@dataclass(unsafe_hash=True)
class Logical(Expr):
    left: Expr
    operator: Token
    right: Expr


@dataclass(unsafe_hash=True)
class Call(Expr):
    callee: Expr
    paren: Token
    arguments: list[Expr]


@dataclass(unsafe_hash=True)
class Get(Expr):
    name: Token
    obj: Expr


@dataclass(unsafe_hash=True)
class Set(Expr):
    name: Token
    obj: Expr
    value: Expr
