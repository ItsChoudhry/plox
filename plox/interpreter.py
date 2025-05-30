from dataclasses import dataclass
import time
from typing import Any, Optional, override
from plox.expr import Assign, Binary, Call, Expr, Get, Grouping, Literal, Logical, Set, Super, This, Unary, Variable
from plox.stmt import Block, Class, Function, If, Return, Stmt, Print, Expression, Var, While
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
        self.locals = {}

        self.globals.define("clock", NativeClockFunction())

    def resolve(self, expr: Expr, depth: int):
        self.locals[expr] = depth

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
                return self.look_up_variable(name, expr)
            case Assign(name, value):
                value = self.evaluate(value)
                distance = self.locals[expr]
                if distance:
                    self.environment.assign_at(distance, name, value)
                else:
                    self.globals.assign(name, value)
                return value
            case Call(callee, _, arguments):
                callee_value = self.evaluate(callee)

                if not isinstance(callee_value, PloxCallable):
                    raise RuntimeError("Can only call functions and classes.")

                evaluated_args = [self.evaluate(arg) for arg in arguments]

                if len(arguments) != callee_value.arity():
                    pass

                return callee_value.call(self, evaluated_args)
            case Get(name, obj):
                obje: Any = self.evaluate(obj)

                if isinstance(obje, PloxInstance):
                    return obje.get(expr.name)

                raise RuntimeError(expr.name, "Only instances have properties.")
            case Set(name, obj, value):
                obje = self.evaluate(obj)

                if not isinstance(obje, PloxInstance):
                    raise RuntimeError(name, "Only instances have fields.")

                value = self.evaluate(value)
                obje.set(name, value)
                return value
            case This(keyword):
                return self.look_up_variable(keyword, expr)
            case Super(keyword, method):
                dist: int = self.locals.get(expr)
                superclass: PloxClass = self.environment.get_at(dist, "super")

                super_object: PloxInstance = self.environment.get_at(dist - 1, "this")

                m_func: PloxFunction = superclass.find_method(method.lexeme)

                if not m_func:
                    raise RuntimeError(method, f"Undefined property'{method.lexeme}'.")
                return m_func.bind(super_object)

            case _:
                raise ValueError("Unknown expression type")

    def look_up_variable(self, name: Token, expr: Expr):
        distance = self.locals.get(expr)
        if distance is not None:
            return self.environment.get_at(distance, name.lexeme)
        return self.globals.get(name)

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
                elif elseBranch is not None:
                    self.execute(elseBranch)
            case While(condition, body):
                while self.is_truthy(self.evaluate(condition)):
                    self.execute(body)
            case Function(name, _, body):
                function: PloxFunction = PloxFunction(stmt, self.environment, False)
                self.environment.define(name.lexeme, function)
            case Return(_, value):
                return_value: Any = None

                if value is not None:
                    return_value = self.evaluate(value)

                raise PloxReturn(return_value)
            case Class(name, superclass, methods):
                s_class = None
                if superclass:
                    s_class = self.evaluate(superclass)
                    if not isinstance(s_class, PloxClass):
                        raise RuntimeError(superclass.name, "Superclass must be a class.")
                self.environment.define(name.lexeme, None)

                if superclass:
                    environment: Environment = Environment(self.environment)
                    environment.define("super", s_class)

                mets = {}
                for method in methods:
                    func = PloxFunction(
                        method, environment if superclass else self.environment, method.name.lexeme == "init"
                    )
                    mets[method.name.lexeme] = func

                klass: PloxClass = PloxClass(name.lexeme, s_class, mets)

                if superclass:
                    environment = self.environment.enclosing

                self.environment.assign(name, klass)
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


class PloxReturn(Exception):
    def __init__(self, value):
        super().__init__()
        self.value = value


class PloxCallable:
    def arity(self) -> int:
        raise NotImplementedError("Subclasses must implement arity")

    def call(self, interpreter: Interpreter, arguments: list[Any]) -> Any:
        raise NotImplementedError("Subclasses must implement call")

    def __str__(self) -> str:
        return "<callable>"


@dataclass
class PloxFunction(PloxCallable):
    def __init__(self, declaraction: Function, closure: Environment, is_initializer: bool) -> None:
        super().__init__()
        self.declaraction = declaraction
        self.closure = closure
        self.is_initializer = is_initializer

    @override
    def arity(self):
        return len(self.declaraction.params)

    @override
    def __str__(self) -> str:
        return f"<fn {self.declaraction.name.lexeme} >"

    @override
    def call(self, interpreter: Interpreter, arguments: list[Any]) -> Any:
        environment: Environment = Environment(self.closure)
        for i, param in enumerate(self.declaraction.params):
            environment.define(param.lexeme, arguments[i])

        try:
            interpreter.executeBlock(self.declaraction.body, environment)
        except PloxReturn as return_value:
            if self.is_initializer:
                return self.closure.get_at(0, "this")
            return return_value.value

        if self.is_initializer:
            return self.closure.get_at(0, "this")
        return None

    def bind(self, instance: "PloxInstance"):
        environment: Environment = Environment(self.closure)
        environment.define("this", instance)
        return PloxFunction(self.declaraction, environment, self.is_initializer)


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


class PloxClass(PloxCallable):
    def __init__(self, name: str, super_class: Optional["PloxClass"], methods: dict[str, PloxFunction]) -> None:
        self.name = name
        self.methods = methods
        self.super_class = super_class

    def find_method(self, name: str):
        if name in self.methods:
            return self.methods[name]

        if self.super_class:
            return self.super_class.find_method(name)

        return None

    @override
    def __str__(self) -> str:
        return f"{self.name}"

    @override
    def arity(self) -> int:
        initializer = self.find_method("init")
        if initializer is None:
            return 0
        return initializer.arity()

    @override
    def call(self, interpreter: Interpreter, arguments: list[Any]) -> Any:
        instance: PloxInstance = PloxInstance(self)
        initializer = self.find_method("init")
        if initializer is not None:
            initializer.bind(instance).call(interpreter, arguments)
        return instance


class PloxInstance:
    def __init__(self, klass: PloxClass) -> None:
        self.klass = klass
        self.fields = {}

    def get(self, name: Token):
        if name.lexeme in self.fields:
            return self.fields[name.lexeme]

        method: PloxFunction = self.klass.find_method(name.lexeme)
        if method:
            return method.bind(self)

        raise RuntimeError(f"{name}, undefined property '{name.lexeme}'.")

    def set(self, name: Token, value: Any):
        self.fields[name.lexeme] = value

    @override
    def __str__(self) -> str:
        return f"{self.klass} instance"
