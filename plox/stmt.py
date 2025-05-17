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
class While(Stmt):
    condition: Expr
    body: Stmt


@dataclass
class Block(Stmt):
    statements: list[Stmt]


@dataclass
class If(Stmt):
    condition: Expr
    thenBranch: Stmt
    elseBranch: Stmt
