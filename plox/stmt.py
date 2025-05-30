from dataclasses import dataclass
from plox.expr import Expr, Variable
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
class Return(Stmt):
    keyword: Token
    value: Expr | None


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
class Function(Stmt):
    name: Token
    params: list[Token]
    body: list[Stmt]


@dataclass
class If(Stmt):
    condition: Expr
    thenBranch: Stmt
    elseBranch: Stmt


@dataclass
class Class(Stmt):
    name: Token
    superclass: Variable
    methods: list[Function]
