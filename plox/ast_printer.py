from typing import override
from plox import expr
from plox.token import Token
from plox.token_type import TokenType


class AstPrinter(expr.ExprVisitor):
    def print(self, expr: expr.Expr):
        return expr.accept(self)

    def parenthesize(self, name: str, *exprs: expr.Expr):
        expressions = " ".join(ex.accept(self) for ex in exprs)
        return f"({name} {expressions})"

    @override
    def visit_binary_expr(self, expr: expr.Binary):
        return self.parenthesize(expr.operator.lexeme, expr.left, expr.right)

    @override
    def visit_grouping_expr(self, expr: expr.Grouping):
        return self.parenthesize("group", expr.expression)

    @override
    def visit_literal_expr(self, expr: expr.Literal):
        return str(expr.value)

    @override
    def visit_unary_expr(self, expr: expr.Unary):
        return self.parenthesize(expr.operator.lexeme, expr.right)

    @override
    def visit_variable_expr(self, expr: expr.Variable):
        return expr.name.lexeme


if __name__ == "__main__":
    exp = expr.Binary(
        expr.Unary(Token(TokenType.MINUS, "-", "", 1), expr.Literal(123)),
        Token(TokenType.STAR, "*", "", 1),
        expr.Grouping(expr.Literal(45.67)),
    )

    printer = AstPrinter()
    print(printer.print(exp))
