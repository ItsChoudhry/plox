from enum import Enum
from typing import TYPE_CHECKING, Union

from plox.expr import Assign, Binary, Call, Expr, Grouping, Literal, Logical, Unary, Variable
from plox.stmt import Block, Expression, Function, If, Print, Return, Stmt, Var, While
from plox.token import Token

if TYPE_CHECKING:
    from plox.interpreter import Interpreter


class FunctionType(Enum):
    NONE = 0
    FUNCTION = 1


class Resolver:
    def __init__(self, interpreter) -> None:
        self.interpreter: Interpreter = interpreter
        self.scopes = []
        self.currentFunction = FunctionType.NONE

    def begin_scope(self):
        self.scopes.append({})

    def end_scope(self):
        self.scopes.pop()

    def resolve_expr(self, expr: Expr):
        match expr:
            case Variable(name):
                if not self.scopes and self.scopes[-1][name.lexeme] is False:
                    # Plox.error(name, "Can't read local variable in it's own initializer.")
                    pass

                self.resolve_local(expr, name)
            case Assign(name, value):
                self.resolve(value)
                self.resolve_local(expr, name)
            case Literal(_):
                pass
            case Binary(left, _, right):
                self.resolve_expr(left)
                self.resolve_expr(right)
            case Call(callee, _, arguments):
                self.resolve_expr(callee)
                for arg in arguments:
                    self.resolve(arg)
            case Grouping(expression):
                self.resolve(expression)
            case Logical(left, _, right):
                self.resolve(left)
                self.resolve(right)
            case Unary(_, right):
                self.resolve(right)

    def resolve_local(self, expr, name):
        for distance, scope in enumerate(reversed(self.scopes)):
            if name.lexeme in scope:
                self.interpreter.resolve(expr, distance)
                return

    def resolve_stmt(self, stmt: Stmt):
        match stmt:
            case Expression(expression):
                self.resolve_expr(expression)
            case Print(expression):
                self.resolve_expr(expression)
            case Block(statements):
                self.begin_scope()
                for s in statements:
                    self.resolve_stmt(s)
                self.end_scope()
            case Var(name, initializer):
                self.declare(name)
                if initializer is not None:
                    self.resolve(initializer)
                self.define(name)
            case If(condition, thenBranch, elseBranch):
                self.resolve(condition)
                self.resolve(thenBranch)
                if elseBranch:
                    self.resolve(elseBranch)
            case Function(name, _, _):
                self.declare(name)
                self.define(name)
                self.resolve_function(stmt, FunctionType.FUNCTION)
            case Return(keyword, value):
                if self.currentFunction == FunctionType.NONE:
                    # Plox.error(keyword, "Can't return from top-level code.")
                    pass
                if value:
                    self.resolve(value)
            case While(condition, body):
                self.resolve(condition)
                self.resolve(body)

    def resolve_function(self, func: Function, type: FunctionType):
        enclosingFunction = self.currentFunction
        self.currentFunction = type

        self.begin_scope()
        for param in func.params:
            self.declare(param)
            self.define(param)

        for statement in func.body:
            self.resolve_stmt(statement)
        self.end_scope()
        self.currentFunction = enclosingFunction

    def declare(self, name: Token):
        if not self.scopes:
            return

        scope = self.scopes[-1]
        if name.lexeme in self.scopes:
            # Plox.error(name, "Already a variable with this name in this scope.")
            pass
        scope[name.lexeme] = False

    def define(self, name: Token):
        if not self.scopes:
            return
        self.scopes[-1][name.lexeme] = True

    def resolve(self, node: Union[Expr, Stmt]):
        if isinstance(node, Stmt):
            self.resolve_stmt(node)
        else:
            self.resolve_expr(node)
