import sys
from plox.interpreter import Interpreter, LoxRuntimeError
from plox.token import Token
from plox.token_type import TokenType
from plox.scanner import Scanner
from plox.parser import Parser

import logging

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from plox.expr import Expr


logger = logging.getLogger(__name__)


class Plox:
    interpreter = Interpreter()
    had_error = False
    had_runtime_error = False

    @staticmethod
    def report(line: int, where: str, message: str):
        logger.info("[%d] Error: %s: %s", line, where, message)

        Plox.had_error = True

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
        Plox.interpreter.interpret(expression)

    def runFile(self, path: str):
        with open(path) as f:
            file = f.read(-1)
            self.run(file)

            if Plox.had_error:
                sys.exit(65)
            elif Plox.had_runtime_error:
                sys.exit(70)

    @staticmethod
    def repl_intro() -> None:
        python_version = ".".join(str(i) for i in sys.version_info[:3])
        print(
            "Plox REPL",
            f"[Python {python_version}] on {sys.platform}",
            'Type "copyright", "credits" or "license" for more information.',
            'Type "exit" or press Ctrl-D (i.e. EOF) to leave.',
            sep="\n",
        )

    @staticmethod
    def runPrompt():
        Plox.repl_intro()
        while True:
            try:
                line = input("> ")
                if line == "exit" or line == "":
                    break
                Plox.run(line)

            except KeyboardInterrupt as k:
                print(f"\n{k.__class__.__name__}")
            except EOFError:
                sys.exit(0)
