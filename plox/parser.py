from typing import Final
from plox.stmt import Block, Expression, If, Print, Stmt, Var, While
from plox.token import Token
from plox.expr import Assign, Binary, Expr, Grouping, Literal, Logical, Unary, Variable
from plox.token_type import TokenType


class ParseError(RuntimeError):
    def __init__(self, token: Token, message: str) -> None:
        super().__init__(message)
        self.token = token


class Parser:
    """
    program     → declaration* eof ;

    declaration → varDecl
                | statement ;
    varDecl     → "var" IDENTIFIER ( "=" expression )? ";" ;
    statement   → exprStmt
                | ifStmt
                | printStmt
                | block ;
    whileStmt   → "while" "(" expression ")" statement ;
    ifStmt      → "if" "(" expression ")" statement
                ( "else" statement )? ;
    block       → "{" declaration* "}" ;

    exprStmt    → expression ";" ;
    printStmt   → "print" expression ";" ;

    expression  → assignment ;
    assignment  → IDENTIFIER "=" assignment
                | logic_or ;
    logic_or    → logic_and ( "or" logic_and )* ;
    logic_and   → equality ( "and" equality )* ;
    equality    → comparison ( ( "!=" | "==" ) comparison )*
    comparison  → term ( ( ">" | ">=" | "<" | "<=" ) term )*
    term        → factor ( ( "-" | "+" ) factor )*
    factor      → unary ( ( "/" | "*" ) unary | "(" expression ")" )*
    unary       → ( "!" | "-" ) unary
                | primary
    primary     → NUMBER | STRING | "false" | "true" | "nil"
                | "(" expression ")"
                | IDENTIFIER ;
    """

    def __init__(self, tokens: list[Token]) -> None:
        self.tokens: Final[list[Token]] = tokens
        self.current: int = 0

    def parse(self) -> list[Stmt]:
        stmts: list[Stmt] = []
        while not self.is_at_end():
            stmts.append(self.declaration())

        return stmts

    def declaration(self):
        try:
            if self.match(TokenType.VAR):
                return self.varDeclaration()
            return self.statement()
        except ParseError:
            self.synchronize()

    def varDeclaration(self):
        name = self.consume(TokenType.IDENTIFIER, "Expect variable name.")

        initializer: Expr = None

        if self.match(TokenType.EQUAL):
            initializer = self.expression()

        self.consume(TokenType.SEMICOLON, "Expect ';' after variable declaration")
        return Var(name, initializer)

    def statement(self):
        if self.match(TokenType.IF):
            return self.if_statement()
        if self.match(TokenType.PRINT):
            return self.print_statement()
        if self.match(TokenType.WHILE):
            return self.while_statement()
        if self.match(TokenType.LEFT_CURLY_BRACE):
            return Block(self.block())
        return self.expression_statement()

    def while_statement(self) -> Stmt:
        self.consume(TokenType.LEFT_PAREN, "Exprect '(' after 'while'.")
        condition: Expr = self.expression()
        self.consume(TokenType.RIGHT_PAREN, "Exprect ')' after 'while'.")
        body = self.statement()
        return While(condition, body)

    def print_statement(self) -> Stmt:
        value: Expr = self.expression()
        self.consume(TokenType.SEMICOLON, "Exprect ';' after value.")
        return Print(value)

    def if_statement(self) -> Stmt:
        self.consume(TokenType.LEFT_PAREN, "Expect '(' after 'if'.")
        condition = self.expression()
        self.consume(TokenType.RIGHT_PAREN, "Expect ')' after 'if' condition.")

        thenBranch: Stmt = self.statement()
        elseBranch: Stmt | None = None

        if self.match(TokenType.ELSE):
            elseBranch: Stmt = self.statement()

        return If(condition, thenBranch, elseBranch)

    def expression_statement(self) -> Stmt:
        expr: Expr = self.expression()
        self.consume(TokenType.SEMICOLON, "Expect ';' after expression.")
        return Expression(expr)

    def block(self) -> list[Stmt]:
        statements: list[Stmt] = []

        while not self.check(TokenType.RIGHT_CURLY_BRACE) and not self.is_at_end():
            statements.append(self.declaration())

        self.consume(TokenType.RIGHT_CURLY_BRACE, "Expect '}' after block.")
        return statements

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

        if self.match(TokenType.IDENTIFIER):
            return Variable(self.previous())

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

    def assignment(self) -> Expr:
        expr = self.logic_or()

        if self.match(TokenType.EQUAL):
            equals = self.previous()
            value = self.assignment()

            if isinstance(expr, Variable):
                name = expr.name
                return Assign(name, value)

            self.error(equals, "Invalid assignment target.")

        return expr

    def logic_or(self) -> Expr:
        expr: Expr = self.logic_and()

        while self.match(TokenType.OR):
            operator: Token = self.previous()
            right: Expr = self.equality()
            expr = Logical(expr, operator, right)
        return expr

    def logic_and(self) -> Expr:
        expr: Expr = self.equality()

        while self.match(TokenType.OR):
            operator: Token = self.previous()
            right: Expr = self.equality()
            expr = Logical(expr, operator, right)
        return expr

    def expression(self) -> Expr:
        return self.assignment()
