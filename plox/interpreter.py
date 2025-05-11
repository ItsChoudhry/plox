from typing import Any
from plox.expr import Assign, Binary, Expr, Grouping, Literal, Unary, Variable
from plox.stmt import Block, Stmt, Print, Expression, Var
from plox.token import Token
from plox.token_type import TokenType
from plox.environment import Environment


class LoxRuntimeError(RuntimeError):
    def __init__(self, token: Token, message: str) -> None:
        super().__init__(message)
        self.token = token

    def __str__(self) -> str:
        return super().__str__()

    def __repr__(self) -> str:
        return super().__repr__()


class Interpreter:
    environment: Environment = Environment()

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
                return self.environment.get(name)
            case Assign(name, value):
                value = self.evaluate(value)
                self.environment.assign(name, value)
                return value
            case _:
                raise ValueError("Unknown expression type")

    def execute(self, stmt: Stmt):
        match stmt:
            case Print(expression):
                value = self.evaluate(expression)
                print(str(value))
            case Expression(expression):
                print(self.evaluate(expression))
            case Var(name, initializer):
                value = self.evaluate(initializer) if initializer else None
                self.environment.define(name.lexeme, value)
            case Block(statements):
                self.executeBlock(statements, Environment(self.environment))
            case _:
                raise ValueError("Unknown statement type")

    def executeBlock(self, statements: list[Stmt], environment: Environment):
        previous = self.environment
        try:
            self.environment = environment

            for statement in statements:
                self.execute(statement)
        finally:
            self.environment = previous

    def interpret(self, stmts: list[Stmt]) -> None:
        try:
            for stmt in stmts:
                self.execute(stmt)
        except Exception as e:
            print(e)
