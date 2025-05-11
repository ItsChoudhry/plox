from dataclasses import dataclass
from plox.expr import Expr
from plox.token import Token


class Stmt:
    pass


@dataclass
class Expression(Stmt):
    expression: Expr


@dataclass
class Print(Stmt):
    expression: Expr


@dataclass
class Var(Stmt):
    name: Token
    initializer: Expr


@dataclass
class Block(Stmt):
    statements: list[Stmt]
