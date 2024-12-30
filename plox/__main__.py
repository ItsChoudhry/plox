import argparse
import sys
import logging

from plox.scanner import Scanner
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from plox.token import Token

logger = logging.getLogger(__name__)


def error(line: int, message: str):
    report(line, "", message)


def report(line: int, where: str, message: str):
    logger.info("[%d] Error: %s: %s", line, where, message)


def run(input):
    scanner = Scanner(input)
    tokens: list[Token] = scanner.scan_tokens()

    for token in tokens:
        logger.info(token)


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
