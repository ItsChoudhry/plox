from plox.expr import Binary, Expr, Grouping, Literal, Unary, Variable
from plox.token import Token
from plox.token_type import TokenType


def ast_string(expr: Expr) -> str:
    match expr:
        case Binary(left, op, right):
            return f"({op.lexeme} {ast_string(left)} {ast_string(right)})"
        case Literal(value):
            if value is None:
                return "nil"
            return str(value)
        case Unary(op, right):
            return f"({op.lexeme} {ast_string(right)})"
        case Grouping(expression):
            return f"(group {ast_string(expression)})"
        case Variable(name):
            return f"(variable {name})"
        case _:
            raise ValueError("Unknown expression type", expr)


if __name__ == "__main__":
    exp = Binary(
        Unary(Token(TokenType.MINUS, "-", "", 1), Literal(123)),
        Token(TokenType.STAR, "*", "", 1),
        Grouping(Literal(45.67)),
    )

    printer = ast_string(exp)
    print(printer)
