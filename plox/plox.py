from plox.interpreter import LoxRuntimeError
from plox.token import Token
from plox.token_type import TokenType
from plox.scanner import Scanner
from plox.parser import Parser
from plox.ast_printer import AstPrinter

import logging

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from plox.expr import Expr


logger = logging.getLogger(__name__)


class Plox:
    had_runtime_error = False

    @staticmethod
    def report(line: int, where: str, message: str):
        logger.info("[%d] Error: %s: %s", line, where, message)

    @staticmethod
    def error(token: Token, message: str) -> None:
        if token.type == TokenType.EOF:
            Plox.report(token.line, " at end", message)
        else:
            Plox.report(token.line, f" at '{token.lexeme}'", message)

    @staticmethod
    def runtime_error(error: LoxRuntimeError) -> None:
        print(f"{error}\n[line {error.token.line}]")

        Plox.had_runtime_error = True

    @staticmethod
    def run(input: str):
        scanner = Scanner(input)
        tokens: list[Token] = scanner.scan_tokens()

        parser: Parser = Parser(tokens)
        expression: Expr = parser.parse()

        print("exprs")
        print(expression)
        print("printer")
        print(AstPrinter().print(expression))

    def runFile(self, path: str):
        with open(path) as f:
            file = f.read(-1)
            self.run(file)

    @staticmethod
    def runPrompt():
        while 1:
            line = input("> ")
            if line == "exit" or line == "":
                break
            Plox.run(line)
