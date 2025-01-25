import argparse
import sys
import logging

from plox.ast_printer import AstPrinter
from plox.expr import Expr
from plox.parser import Parser
from plox.scanner import Scanner

from plox.token_type import TokenType
from plox.token import Token


logger = logging.getLogger(__name__)


@staticmethod
def error(token: Token, message: str) -> None:
    if token.type == TokenType.EOF:
        report(token.line, " at end", message)
    else:
        report(token.line, f" at '{token.lexeme}'", message)


def report(line: int, where: str, message: str):
    logger.info("[%d] Error: %s: %s", line, where, message)


def run(input):
    scanner = Scanner(input)
    tokens: list[Token] = scanner.scan_tokens()

    parser: Parser = Parser(tokens)
    expression: Expr = parser.parse()

    print("exprs")
    print(expression)
    print("printer")
    print(AstPrinter().print(expression))


def runFile(path: str):
    with open(path) as f:
        file = f.read(-1)
        run(file)


def runPrompt():
    while 1:
        line = input("> ")
        if line == "exit" or line == "":
            break
        run(line)


def main():
    parser = argparse.ArgumentParser()
    _, args = parser.parse_known_args()
    if len(args) > 1:
        print("Usage: plox [script]")
        sys.exit(64)
    elif len(args) == 1:
        runFile(args[0])
    else:
        runPrompt()


if __name__ == "__main__":
    main()
