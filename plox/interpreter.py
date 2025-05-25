from dataclasses import dataclass
import time
from typing import Any, override
from plox.expr import Assign, Binary, Call, Expr, Grouping, Literal, Logical, Unary, Variable
from plox.stmt import Block, Function, If, Stmt, Print, Expression, Var, While
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
    def __init__(self):
        self.globals = Environment()
        self.environment = self.globals

        self.globals.define("clock", NativeClockFunction())

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

    @staticmethod
    def is_truthy(obj: Any) -> bool:
        if obj is None:
            return False
        elif isinstance(obj, bool):
            return bool(obj)
        return True

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
                elif op.type == TokenType.LESS:
                    return left_val < right_val
                elif op.type == TokenType.LESS_EQUAL:
                    return left_val <= right_val
                elif op.type == TokenType.GREATER:
                    return left_val > right_val
                elif op.type == TokenType.GREATER_EQUAL:
                    return left_val >= right_val
                else:
                    raise ValueError(f"Unknown operator {op.lexeme}")
            case Literal(value):
                return value
            case Logical(left, op, right):
                logic_left: Any = self.evaluate(left)
                if op.type == TokenType.OR:
                    if self.is_truthy(logic_left):
                        return logic_left
                else:
                    if not self.is_truthy(logic_left):
                        return logic_left
                return self.evaluate(right)
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
            case Call(callee, paren, arguments):
                callee_value = self.evaluate(callee)

                if not isinstance(callee_value, PloxCallable):
                    raise RuntimeError("Can only call functions and classes.")

                evaluated_args = [self.evaluate(arg) for arg in arguments]

                if len(arguments) != callee_value.arity():
                    pass

                return callee_value.call(self, evaluated_args)
            case _:
                raise ValueError("Unknown expression type")

    def execute(self, stmt: Stmt):
        match stmt:
            case Print(expression):
                value = self.evaluate(expression)
                print(str(value))
            case Expression(expression):
                self.evaluate(expression)
            case Var(name, initializer):
                value = self.evaluate(initializer) if initializer else None
                self.environment.define(name.lexeme, value)
            case Block(statements):
                self.executeBlock(statements, Environment(self.environment))
            case If(condition, thenBranch, elseBranch):
                if self.is_truthy(self.evaluate(condition)):
                    self.execute(thenBranch)
                else:
                    self.execute(elseBranch)
            case While(condition, body):
                while self.is_truthy(self.evaluate(condition)):
                    self.execute(body)
            case Function(name, params, body):
                function: PloxFunction = PloxFunction(stmt)
                self.environment.define(name.lexeme, function)
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


class PloxCallable:
    def arity(self) -> int:
        raise NotImplementedError("Subclasses must implement arity")

    def call(self, interpreter: Interpreter, arguments: list[Any]) -> Any:
        raise NotImplementedError("Subclasses must implement call")

    def __str__(self) -> str:
        return "<callable>"


@dataclass
class PloxFunction(PloxCallable):
    declaraction: Function

    def __init__(self, declaraction: Function) -> None:
        super().__init__()
        self.declaraction = declaraction

    @override
    def arity(self):
        return len(self.declaraction.params)

    @override
    def __str__(self) -> str:
        return f"<fn {self.declaraction.name.lexeme} >"

    @override
    def call(self, interpreter: Interpreter, arguments: list[Any]) -> Any:
        environment: Environment = Environment(interpreter.globals)
        for i, param in enumerate(self.declaraction.params):
            environment.define(param.lexeme, arguments[i])

        interpreter.executeBlock(self.declaraction.body, environment)
        return None


# Native clock function
class NativeClockFunction(PloxCallable):
    @override
    def arity(self) -> int:
        return 0  # Takes no arguments

    @override
    def call(self, interpreter, arguments: list[Any]) -> float:
        return time.time()  # Python's time.time() is equivalent to System.currentTimeMillis() / 1000.0

    @override
    def __str__(self) -> str:
        return "<native fn>"
