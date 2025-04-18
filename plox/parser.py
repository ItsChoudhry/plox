from typing import Final
from plox.stmt import Expression, Print, Stmt
from plox.token import Token
from plox.expr import Binary, Expr, Grouping, Literal, Unary
from plox.token_type import TokenType


class ParseError(RuntimeError):
    def __init__(self, token: Token, message: str) -> None:
        super().__init__(message)
        self.token = token


class Parser:
    def __init__(self, tokens: list[Token]) -> None:
        self.tokens: Final[list[Token]] = tokens
        self.current: int = 0

    def parse(self) -> list[Stmt]:
        stmts: list[Stmt] = []
        while not self.is_at_end():
            stmts.append(self.statement())

        return stmts

    def statement(self):
        if self.match(TokenType.PRINT):
            return self.print_statement()
        return self.expression_statement()

    def print_statement(self) -> Stmt:
        value: Expr = self.expression()
        self.consume(TokenType.SEMICOLON, "Exprect ';' after value.")
        return Print(value)

    def expression_statement(self) -> Stmt:
        expr: Expr = self.expression()
        self.consume(TokenType.SEMICOLON, "Expect ';' after expression.")
        return Expression(expr)

    def synchronize(self) -> None:
        self.advance()
        while not self.is_at_end():
            if self.previous().type == TokenType.SEMICOLON:
                return
            if self.peek().type in (
                TokenType.CLASS,
                TokenType.FUN,
                TokenType.VAR,
                TokenType.FOR,
                TokenType.IF,
                TokenType.WHILE,
                TokenType.PRINT,
                TokenType.RETURN,
            ):
                return
        self.advance()

    @staticmethod
    def error(token: Token, message: str) -> ParseError:
        return ParseError(token, message)

    def consume(self, type: TokenType, message: str) -> Token:
        if self.check(type):
            return self.advance()
        raise self.error(self.peek(), message)

    def primary(self) -> Expr:
        if self.match(TokenType.FALSE):
            return Literal(False)
        if self.match(TokenType.TRUE):
            return Literal(True)
        if self.match(TokenType.NIL):
            return Literal(None)

        if self.match(TokenType.NUMBER, TokenType.STRING):
            return Literal(self.previous().literal)

        if self.match(TokenType.LEFT_PAREN):
            expr: Expr = self.expression()
            self.consume(TokenType.RIGHT_PAREN, "Expect ')' after expression.")
            return Grouping(expr)

        raise self.error(self.peek(), "Expect expression.")

    def unary(self) -> Expr:
        if self.match(TokenType.BANG, TokenType.MINUS):
            operator: Token = self.previous()
            right: Expr = self.unary()
            return Unary(operator, right)
        return self.primary()

    def factor(self) -> Expr:
        expr: Expr = self.unary()

        while self.match(TokenType.SLASH, TokenType.STAR):
            operator = self.previous()
            right = self.unary()
            expr = Binary(expr, operator, right)

        if self.match(TokenType.LEFT_PAREN):
            rightParen: Expr = self.expression()
            self.consume(TokenType.RIGHT_PAREN, "Expext ')' after expression.")

            operatorParen: Token = Token(TokenType.STAR, "*", None, self.previous().line)

            expr = Binary(expr, operatorParen, rightParen)

        return expr

    def term(self) -> Expr:
        expr: Expr = self.factor()

        while self.match(TokenType.MINUS, TokenType.PLUS):
            operator = self.previous()
            right = self.factor()
            expr = Binary(expr, operator, right)
        return expr

    def comparison(self) -> Expr:
        expr: Expr = self.term()

        while self.match(TokenType.GREATER, TokenType.GREATER_EQUAL, TokenType.LESS, TokenType.LESS_EQUAL):
            operator = self.previous()
            right = self.term()
            expr = Binary(expr, operator, right)
        return expr

    def match(self, *types: TokenType) -> bool:
        for type in types:
            if self.check(type):
                self.advance()
                return True
        return False

    def check(self, type: TokenType) -> bool:
        if self.is_at_end():
            return False
        return self.peek().type == type

    def advance(self) -> Token:
        if not self.is_at_end():
            self.current += 1
        return self.previous()

    def is_at_end(self) -> bool:
        return self.peek().type == TokenType.EOF

    def peek(self) -> Token:
        return self.tokens[self.current]

    def previous(self) -> Token:
        return self.tokens[self.current - 1]

    def equality(self) -> Expr:
        expr: Expr = self.comparison()
        while self.match(TokenType.BANG_EQUAL, TokenType.EQUAL_EQUAL):
            operator: Token = self.previous()
            right: Expr = self.comparison()
            expr = Binary(expr, operator, right)
        return expr

    def expression(self) -> Expr:
        return self.equality()
