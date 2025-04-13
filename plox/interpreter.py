from typing import Any
from plox.ast_printer import ast_string
from plox.expr import Binary, Expr, Grouping, Literal, Unary, Variable
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


class Interpreter:
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

    def evaluate(self, expr: Expr) -> Any:
        match expr:
            case Binary(left, op, right):
                left_val = self.evaluate(left)
                right_val = self.evaluate(right)
                if op.type == TokenType.PLUS:
                    return left_val + right_val
                elif op.type == TokenType.MINUS:
                    return left_val - right_val
                elif op.type == TokenType.STAR:
                    return left_val * right_val
                elif op.type == TokenType.SLASH:
                    if right_val == 0:
                        raise ValueError("Division by zero")
                    return left_val / right_val
                else:
                    raise ValueError(f"Unknown operator {op.lexeme}")
            case Literal(value):
                return value
            case Unary(op, right):
                right_val = self.evaluate(right)
                if op.type == "MINUS":
                    return -right_val
                elif op.type == "BANG":
                    return not right_val
                else:
                    raise ValueError(f"Unknown unary operator {op.lexeme}")
            case Grouping(expression):
                return self.evaluate(expression)
            case Variable(name):
                print(name.lexeme)
            case _:
                raise ValueError("Unknown expression type")

    def interpret(self, expression: "Expr") -> None:
        try:
            print(ast_string(expression))
            value: Any = self.evaluate(expression)
            print(value)
        except Exception as e:
            print(e)
