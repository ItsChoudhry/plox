from typing import override
from plox.expr import Expr, ExprVisitor, Grouping, Literal


class Interpreter(ExprVisitor):
    @override
    def visit_binary_expr(self, expr: "Expr") -> None:
        pass

    def evaluate(self, expr: Expr) -> object:
        return expr.accept(self)

    @override
    def visit_grouping_expr(self, expr: Grouping) -> object:
        return self.evaluate(expr.expression)

    @override
    def visit_literal_expr(self, expr: Literal) -> object:
        return expr.value

    @override
    def visit_unary_expr(self, expr: "Expr") -> None:
        pass

    @override
    def visit_variable_expr(self, expr: "Expr") -> None:
        pass
