from argparse import ArgumentParser
from pathlib import Path
from typing import TextIO


arg_parser = ArgumentParser(usage="generate_ast.py <output directory>")
arg_parser.add_argument("output")
args = arg_parser.parse_args()

ASTDict = dict[str, tuple[str]]

EXPRESSIONS: ASTDict = {
    "Binary": ("left: Expr", "operator: Token", "right: Expr"),
    "Grouping": ("expression: Expr",),
    "Literal": ("value: object",),
    "Unary": ("operator: Token", "right: Expr"),
    "Variable": ("name: Token",),
}


INDENTATION = "    "


def define_type(f: TextIO, base_name: str, class_name: str, fields: tuple[str]):
    f.write("@dataclass")
    f.write("\n")
    f.write(f"class {class_name}({base_name}):")
    f.write("\n")

    for field in fields:
        variable = field.split(":")[0].strip()
        type_name = field.split(":")[1].strip()
        f.write(f"{INDENTATION}{variable}: Final[{type_name}]")
        f.write("\n")

    f.write("\n")
    f.write(f"{INDENTATION}@abstractmethod")
    f.write("\n")
    f.write(f"{INDENTATION}def accept(self, visitor: {base_name}Visitor):")
    f.write("\n")
    f.write(f"{INDENTATION*2}return visitor.visit_{class_name.lower()}_{base_name.lower()}(self)")
    f.write("\n")


def define_visitor(f: TextIO, base_name: str, types: ASTDict):
    f.write("\n")
    f.write(f"class {base_name}Visitor(ABC):")
    f.write("\n")
    for type in types.keys():
        f.write(f"{INDENTATION}@abstractmethod")
        f.write("\n")
        f.write(f'{INDENTATION}def visit_{type.lower()}_{base_name.lower()}(self, {base_name.lower()}: "Expr"):')
        f.write("\n")
        f.write(f"{INDENTATION*2}pass")
        f.write("\n\n")


def define_imports(f: TextIO):
    f.write("from abc import ABC, abstractmethod")
    f.write("\n")
    f.write("from dataclasses import dataclass")
    f.write("\n")
    f.write("from typing import Final")
    f.write("\n")
    f.write("from plox.token import Token")
    f.write("\n\n")


def define_ast(output_dir: Path, base_name: str, types: ASTDict):
    name = base_name.title()

    with output_dir.open(mode="w", encoding="utf-8") as f:
        define_imports(f)
        define_visitor(f, base_name, types)
        f.write("\n")
        f.write(f"class {base_name}(ABC):")
        f.write("\n")
        f.write(f"{INDENTATION}@abstractmethod")
        f.write("\n")
        f.write(f"{INDENTATION}def accept(self, visitor: {base_name}Visitor):")
        f.write("\n")
        f.write(f"{INDENTATION*2}pass")
        f.write("\n\n")

        for class_name, fields in types.items():
            f.write("\n")
            define_type(f, name, class_name, fields)
            f.write("\n")


def main():
    path = Path(args.output).resolve()

    if not path.is_dir():
        arg_parser.error("Output must be a valid dir")

    define_ast(path / "expr.py", "Expr", EXPRESSIONS)


if __name__ == "__main__":
    main()
