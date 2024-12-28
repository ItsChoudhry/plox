import argparse
import sys


def error(line: int, message: str):
    report(line, "", message)


def report(line: int, where: str, message: str):
    report(f"[line] Error: {where}: {message}")


def run(input):
    print(input)


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
