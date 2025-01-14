from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Final, override
from plox.token import Token


class ExprVisitor(ABC):
    @abstractmethod
    def visit_binary_expr(self, expr: "Expr"):
        pass

    @abstractmethod
    def visit_grouping_expr(self, expr: "Expr"):
        pass

    @abstractmethod
    def visit_literal_expr(self, expr: "Expr"):
        pass

    @abstractmethod
    def visit_unary_expr(self, expr: "Expr"):
        pass

    @abstractmethod
    def visit_variable_expr(self, expr: "Expr"):
        pass


class Expr(ABC):
    @abstractmethod
    def accept(self, visitor: ExprVisitor):
        pass


@dataclass
class Binary(Expr):
    left: Final[Expr]
    operator: Final[Token]
    right: Final[Expr]

    @override
    def accept(self, visitor: ExprVisitor):
        return visitor.visit_binary_expr(self)


@dataclass
class Grouping(Expr):
    expression: Final[Expr]

    @override
    def accept(self, visitor: ExprVisitor):
        return visitor.visit_grouping_expr(self)


@dataclass
class Literal(Expr):
    value: Final[object]

    @override
    def accept(self, visitor: ExprVisitor):
        return visitor.visit_literal_expr(self)


@dataclass
class Unary(Expr):
    operator: Final[Token]
    right: Final[Expr]

    @override
    def accept(self, visitor: ExprVisitor):
        return visitor.visit_unary_expr(self)


@dataclass
class Variable(Expr):
    name: Final[Token]

    @override
    def accept(self, visitor: ExprVisitor):
        return visitor.visit_variable_expr(self)
