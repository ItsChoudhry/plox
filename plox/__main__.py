import argparse
import sys
import logging

from plox.plox import Plox


logger = logging.getLogger(__name__)


def main():
    parser = argparse.ArgumentParser()
    _, args = parser.parse_known_args()
    if len(args) > 1:
        print("Usage: plox [script]")
        sys.exit(64)
    elif len(args) == 1:
        print(args[0])
        Plox.runFile(args[0])
    else:
        Plox.runPrompt()


if __name__ == "__main__":
    main()
