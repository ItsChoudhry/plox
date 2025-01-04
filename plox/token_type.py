from enum import Enum


class TokenType(Enum):
    # single  character token
    LEFT_PAREN = "("
    RIGHT_PAREN = ")"
    LEFT_BRACE = "["
    RIGHT_BRACE = "]"
    LEFT_CURLY_BRACE = "{"
    RIGHT_CURLY_BRACE = "}"
    COMMA = ","
    DOT = "."
    MINUS = "-"
    PLUS = "+"
    SEMICOLON = ";"
    SLASH = "/"
    STAR = "*"

    # one or two  characters token
    BANG = "!"
    BANG_EQUAL = "!="
    EQUAL = "="
    EQUAL_EQUAL = "=="
    GREATER = ">"
    GREATER_EQUAL = ">="
    LESS = "<"
    LESS_EQUAL = "<="

    # Literals
    IDENTIFIER = "identifier"
    STRING = "str"
    NUMBER = "int"

    # KEYWORDS
    AND = "and"
    CLASS = "class"
    ELSE = "else"
    FALSE = "false"
    FUN = "fun"
    FOR = "for"
    IF = "if"
    NIL = "nil"
    OR = "or"
    PRINT = "print"
    RETURN = "return"
    SUPER = "super"
    THIS = "this"
    TRUE = "true"
    VAR = "var"
    WHILE = "while"

    EOF = ""

    def __str__(self):
        return self.name


SINGLE_CHARS: tuple[str, ...] = (
    "(",
    ")",
    "{",
    "}",
    ",",
    ".",
    "-",
    "+",
    ";",
    "*",
)

ONE_OR_MORE_CHARS: tuple[str, ...] = ("!", "!=", "=", "==", ">", ">=", "<", "<=")

KEYWORDS: dict[str, TokenType] = {
    "and": TokenType.AND,
    "class": TokenType.CLASS,
    "else": TokenType.ELSE,
    "false": TokenType.FALSE,
    "fun": TokenType.FUN,
    "for": TokenType.FOR,
    "if": TokenType.IF,
    "nil": TokenType.NIL,
    "or": TokenType.OR,
    "print": TokenType.PRINT,
    "return": TokenType.RETURN,
    "super": TokenType.SUPER,
    "this": TokenType.THIS,
    "true": TokenType.TRUE,
    "var": TokenType.VAR,
    "while": TokenType.WHILE,
}
