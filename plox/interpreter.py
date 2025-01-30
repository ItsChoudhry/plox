from typing import Any, override
from plox.expr import Binary, Expr, ExprVisitor, Grouping, Literal, Unary
from plox.token import Token
from plox.token_type import TokenType


class LoxRuntimeError(RuntimeError):
    def __init__(self, token: Token, message: str) -> None:
        super().__init__(message)
        self.token = token

    def __str__(self) -> str:
        return super().__str__()

    def __repr__(self) -> str:
        return super().__repr__()


class Interpreter(ExprVisitor):
    def check_if_number(self, operator: Token, left: Any, right: Any) -> None:
        if isinstance(left, int | float) and isinstance(right, int | float):
            return

        raise RuntimeError(operator, "Operands must be numeric objects.")

    @staticmethod
    def is_equal(a: Any, b: Any) -> bool:
        return a == b

    @staticmethod
    def stringify(obj: Any) -> str:
        if obj is None:
            return "null"

        if isinstance(obj, str):
            return obj

        if isinstance(obj, bool):
            return str(obj).lower()

        return str(obj)

    @override
    def visit_binary_expr(self, expr: Binary) -> object:
        left: Any = self.evaluate(expr.left)
        right: Any = self.evaluate(expr.right)

        if expr.operator.type == TokenType.PLUS:
            if (isinstance(left, int | float) and isinstance(right, int | float)) or (
                isinstance(left, str) and isinstance(right, str)
            ):
                return left + right
            raise RuntimeError(expr.operator, "Operands must be two strings or two numeric objects.")
        elif expr.operator.type == TokenType.MINUS:
            self.check_if_number(expr.operator, left, right)
            return left - right
        elif expr.operator.type == TokenType.SLASH:
            self.check_if_number(expr.operator, left, right)
            return left / right
        elif expr.operator.type == TokenType.STAR:
            self.check_if_number(expr.operator, left, right)
            return left * right
        elif expr.operator.type == TokenType.GREATER:
            self.check_if_number(expr.operator, left, right)
            return left > right
        elif expr.operator.type == TokenType.GREATER_EQUAL:
            self.check_if_number(expr.operator, left, right)
            return left >= right
        elif expr.operator.type == TokenType.LESS:
            self.check_if_number(expr.operator, left, right)
            return left < right
        elif expr.operator.type == TokenType.LESS_EQUAL:
            self.check_if_number(expr.operator, left, right)
            return left <= right
        elif expr.operator.type == TokenType.BANG_EQUAL:
            self.check_if_number(expr.operator, left, right)
            return not self.is_equal(left, right)
        elif expr.operator.type == TokenType.EQUAL_EQUAL:
            self.check_if_number(expr.operator, left, right)
            return self.is_equal(left, right)

        return None

    def evaluate(self, expr: Expr) -> Any:
        return expr.accept(self)

    @override
    def visit_grouping_expr(self, expr: Grouping) -> object:
        return self.evaluate(expr.expression)

    @override
    def visit_literal_expr(self, expr: Literal) -> object:
        return expr.value

    @staticmethod
    def is_truthy(obj: Any) -> bool:
        return bool(obj)

    @override
    def visit_unary_expr(self, expr: Unary) -> object:
        right = self.evaluate(expr.right)
        if expr.operator.type is TokenType.BANG:
            return not self.is_truthy(right)
        if expr.operator.type is TokenType.MINUS:
            return -right
        return None

    @override
    def visit_variable_expr(self, expr: "Expr") -> None:
        pass

    def interpret(self, expression: "Expr") -> None:
        try:
            value: Any = self.evaluate(expression)
            print(value)
        except RuntimeError as e:
            print(e)
