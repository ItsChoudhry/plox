from typing import Final
from plox.stmt import Block, Class, Expression, Function, If, Print, Return, Stmt, Var, While
from plox.token import Token
from plox.expr import Assign, Binary, Call, Expr, Get, Grouping, Literal, Logical, Set, Unary, Variable
from plox.token_type import TokenType


class ParseError(RuntimeError):
    def __init__(self, token: Token, message: str) -> None:
        super().__init__(message)
        self.token = token


class Parser:
    """
    program     → declaration* eof ;

    declaration → classDecl
                | funDecl
                | varDecl
                | statement ;
    classDecl   → "class" IDENTIFIER "{" function* "}" ;
    funDecl     → "fun" function ;
    function    → IDENTIFIER "(" parameters? ")" block ;
    parameters  → IDENTIFIER ("," IDENTIFIER)* ;
    varDecl     → "var" IDENTIFIER ( "=" expression )? ";" ;
    statement   → exprStmt
                | forStmt
                | ifStmt
                | printStmt
                | returnStmt
                | whileStmt
                | block ;
    forStmt        → "for" "(" ( varDecl | exprStmt | ";" )
                 expression? ";"
                 expression? ")" statement ;
    whileStmt   → "while" "(" expression ")" statement ;
    ifStmt      → "if" "(" expression ")" statement
                ( "else" statement )? ;
    block       → "{" declaration* "}" ;

    exprStmt    → expression ";" ;
    printStmt   → "print" expression ";" ;
    exprStmt    → "return" expression? ";" ;
    expression  → assignment ;
    assignment  → ( call "." )? IDENTIFIER "=" assignment
                | logic_or ;
    logic_or    → logic_and ( "or" logic_and )* ;
    logic_and   → equality ( "and" equality )* ;
    equality    → comparison ( ( "!=" | "==" ) comparison )*
    comparison  → term ( ( ">" | ">=" | "<" | "<=" ) term )*
    term        → factor ( ( "-" | "+" ) factor )*
    factor      → unary ( ( "/" | "*" ) unary | "(" expression ")" )*
    unary       → ( "!" | "-" ) unary | call
    call        → primary ( "(" arguments? ")" | "." INDENTIFIER )*;
    arguments   → expression ( "," expression )* ;
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
            if self.match(TokenType.CLASS):
                return self.class_declaration()
            if self.match(TokenType.FUN):
                return self.function("function")
            if self.match(TokenType.VAR):
                return self.var_declaration()
            return self.statement()
        except ParseError:
            self.synchronize()

    def function(self, kind: str) -> Stmt:
        name = self.consume(TokenType.IDENTIFIER, f"Expect {kind} name.")

        self.consume(TokenType.LEFT_PAREN, f"Expect '(' after {kind} name.")
        params: list[Token] = []
        if not self.check(TokenType.RIGHT_PAREN):
            while True:
                if len(params) >= 255:
                    self.error(self.peek(), "Can't have more than 255 parameters.")

                params.append(self.consume(TokenType.IDENTIFIER, "Expect parameter name."))
                if not self.match(TokenType.COMMA):
                    break

        self.consume(TokenType.RIGHT_PAREN, "Expect ')' after parameters.")
        self.consume(TokenType.LEFT_CURLY_BRACE, f"Expect '{{' before {kind} body.")
        body = self.block()
        return Function(name, params, body)

    def var_declaration(self):
        name = self.consume(TokenType.IDENTIFIER, "Expect variable name.")

        initializer: Expr = None

        if self.match(TokenType.EQUAL):
            initializer = self.expression()

        self.consume(TokenType.SEMICOLON, "Expect ';' after variable declaration")
        return Var(name, initializer)

    def class_declaration(self):
        name: Token = self.consume(TokenType.IDENTIFIER, "Expect class name.")
        self.consume(TokenType.LEFT_CURLY_BRACE, "Expect '{' before class body.")

        methods = []
        while not self.check(TokenType.RIGHT_CURLY_BRACE) and not self.is_at_end():
            methods.append(self.function("method"))

        self.consume(TokenType.RIGHT_CURLY_BRACE, "Expect '}' after class body.")

        return Class(name, methods)

    def statement(self):
        if self.match(TokenType.FOR):
            return self.for_statement()
        if self.match(TokenType.IF):
            return self.if_statement()
        if self.match(TokenType.PRINT):
            return self.print_statement()
        if self.match(TokenType.RETURN):
            return self.return_statement()
        if self.match(TokenType.WHILE):
            return self.while_statement()
        if self.match(TokenType.LEFT_CURLY_BRACE):
            return Block(self.block())
        return self.expression_statement()

    def for_statement(self) -> Stmt:
        self.consume(TokenType.LEFT_PAREN, "Exprect '(' after 'while'.")

        initializer: Stmt | None
        if self.match(TokenType.SEMICOLON):
            initializer = None
        elif self.match(TokenType.VAR):
            initializer = self.var_declaration()
        else:
            initializer = self.expression_statement()

        condition: Expr | None = None
        if not self.check(TokenType.SEMICOLON):
            condition = self.expression()
        self.consume(TokenType.SEMICOLON, "Expect ';' after loop condition")

        increament: Expr | None = None
        if not self.check(TokenType.RIGHT_PAREN):
            increament = self.expression()
        self.consume(TokenType.RIGHT_PAREN, "Exprect ')' after for clauses.")

        body: Stmt = self.statement()

        if increament is not None:
            body = Block([body, Expression(increament)])

        if condition is None:
            condition = Literal(True)
        body = While(condition, body)

        if initializer is not None:
            body = Block([initializer, body])

        return body

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

    def return_statement(self) -> Stmt:
        keyword: Token = self.previous()
        value: Expr | None = None

        if not self.check(TokenType.SEMICOLON):
            value = self.expression()

        self.consume(TokenType.SEMICOLON, "Exprect ';' after return value.")
        return Return(keyword, value)

    def if_statement(self) -> Stmt:
        self.consume(TokenType.LEFT_PAREN, "Expect '(' after 'if'.")
        condition = self.expression()
        self.consume(TokenType.RIGHT_PAREN, "Expect ')' after 'if' condition.")

        thenBranch: Stmt = self.statement()
        elseBranch: Stmt | None = None

        if self.match(TokenType.ELSE):
            elseBranch = self.statement()

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
        print(f"[line {token.line}] Error at '{token.lexeme}': {message}")
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
        return self.call()

    def call(self) -> Expr:
        expr: Expr = self.primary()

        while True:
            if self.match(TokenType.LEFT_PAREN):
                expr = self.finish_call(expr)
            elif self.match(TokenType.DOT):
                name: Token = self.consume(TokenType.IDENTIFIER, "Expect property name after '.'.")
                expr = Get(name, expr)
            else:
                break

        return expr

    def finish_call(self, callee: Expr) -> Expr:
        arguments: list[Expr] = []
        if not self.check(TokenType.RIGHT_PAREN):
            while True:
                arguments.append(self.expression())
                if len(arguments) >= 255:
                    self.error(self.peek(), "Can't have more than 255 arguements.")
                if not self.match(TokenType.COMMA):
                    break
        paren: Token = self.consume(TokenType.RIGHT_PAREN, "Expect ')' after arguements.")

        return Call(callee, paren, arguments)

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
            elif isinstance(expr, Get):
                get: Get = expr
                return Set(get.name, get.obj, value)

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
