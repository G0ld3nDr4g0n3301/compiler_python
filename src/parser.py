from token_type import Token, TokenType
from ast_nodes import *

class ParseError(Exception):
    pass

class Parser:
    def __init__(self, tokens: list[Token]):
        self._tokens = tokens
        self._position = 0

    def parse(self) -> list[Stmt]:
        statements =[]
        while not self._is_at_end():
            statements.append(self._parse_declaration())
        return statements

    # --- Уровень деклараций и инструкций (Statements) ---

    def _parse_declaration(self) -> Stmt:
        if self._match(TokenType.VAR):
            return self._parse_var_declaration()
        if self._match(TokenType.FUNC):
            return self._parse_function_declaration()
        return self._parse_statement()

    def _parse_statement(self) -> Stmt:
        if self._match(TokenType.IF):
            return self._parse_if_statement()
        if self._match(TokenType.WHILE):
            return self._parse_while_statement()
        if self._match(TokenType.PRINT):
            return self._parse_print_statement()
        if self._match(TokenType.LBRACE):
            return BlockStmt(self._parse_block())
        if self._match(TokenType.RETURN):
            return self._parse_return_statement()

        return self._parse_expression_statement()

    def _parse_type(self) -> DataType:
        if self._match(TokenType.NUMBER_TYPE):
            return DataType.NUMBER
        if self._match(TokenType.BOOL_TYPE):
            return DataType.BOOL
        if self._match(TokenType.STRING_TYPE):
            return DataType.STRING
        raise ParseError("[Parse Error] Unknown Type, expected [string, number, bool]")

    def _parse_var_declaration(self) -> Stmt:
        name_token = self._consume(TokenType.ID, "Ожидается имя переменной.")
        self._consume(TokenType.COLON, "Ожидается ':' перед типом переменной.")
        
        var_type = self._parse_type()
        initializer = None

        if self._match(TokenType.EQ):
            initializer = self._parse_expression()

        self._consume(TokenType.SEMICOLON, "Ожидается ';' после объявления переменной.")
        return VarStmt(name=name_token.value, type=var_type, initializer=initializer)

    def _parse_function_declaration(self) -> Stmt:
        name_token = self._consume(TokenType.ID, "Ожидается имя функции.")
        self._consume(TokenType.LPAREN, "Ожидается '(' после имени функции.")

        parameters =[]
        if not self._check(TokenType.RPAREN):
            while True:
                param_name = self._consume(TokenType.ID, "Ожидается имя параметра.")
                self._consume(TokenType.COLON, "Ожидается ':' после имени параметра.")
                param_type = self._parse_type()
                parameters.append((param_name.value, param_type))
                if not self._match(TokenType.COMMA):
                    break

        self._consume(TokenType.RPAREN, "Ожидается ')' после параметров.")
        self._consume(TokenType.COLON, "Ожидается ':' перед типом возвращаемого значения.")
        return_type = self._parse_type()

        self._consume(TokenType.LBRACE, "Ожидается '{' перед телом функции.")
        body = self._parse_block()

        return FunctionStmt(name=name_token.value, params=parameters, return_type=return_type, body=body)


    def _parse_if_statement(self) -> Stmt:
        self._consume(TokenType.LPAREN, "Ожидается '(' после 'if'.")
        condition = self._parse_expression()
        self._consume(TokenType.RPAREN, "Ожидается ')' после условия 'if'.")

        then_branch = self._parse_statement()
        else_branch = None

        if self._match(TokenType.ELSE):
            else_branch = self._parse_statement()

        return IfStmt(condition=condition, then_branch=then_branch, else_branch=else_branch)

    def _parse_while_statement(self) -> Stmt:
        self._consume(TokenType.LPAREN, "Ожидается '(' после 'while'.")
        condition = self._parse_expression()
        self._consume(TokenType.RPAREN, "Ожидается ')' после условия 'while'.")

        body = self._parse_statement()
        return WhileStmt(condition=condition, body=body)

    def _parse_print_statement(self) -> Stmt:
        value = self._parse_expression()
        self._consume(TokenType.SEMICOLON, "Ожидается ';' после значения.")
        return PrintStmt(expr=value)

    def _parse_return_statement(self) -> Stmt:
        value = None
        if not self._check(TokenType.SEMICOLON):
            value = self._parse_expression()
        self._consume(TokenType.SEMICOLON, "Ожидается ';' после возвращаемого значения.")
        return ReturnStmt(value=value)

    def _parse_expression_statement(self) -> Stmt:
        expr = self._parse_expression()
        self._consume(TokenType.SEMICOLON, "Ожидается ';' после выражения.")
        return ExpressionStmt(expr=expr)

    def _parse_block(self) -> list[Stmt]:
        statements =[]
        while not self._check(TokenType.RBRACE) and not self._is_at_end():
            statements.append(self._parse_declaration())
        self._consume(TokenType.RBRACE, "Ожидается '}' после блока.")
        return statements

    # --- Уровень выражений (Expressions) ---

    def _parse_expression(self) -> Expr:
        return self._parse_assignment()

    def _parse_assignment(self) -> Expr:
        expr = self._parse_logical_or()

        if self._match(TokenType.EQ):
            equals = self._previous()
            value = self._parse_assignment()

            if isinstance(expr, VariableExpr):
                return AssignExpr(name=expr.name, value=value)

            raise ParseError(f"[Parser Error] Line {equals.line}: Недопустимая цель для присваивания.")

        return expr

    def _parse_logical_or(self) -> Expr:
        expr = self._parse_logical_and()
        while self._match(TokenType.OR):
            op = self._previous().type
            right = self._parse_logical_and()
            expr = BinaryExpr(left=expr, op=op, right=right)
        return expr

    def _parse_logical_and(self) -> Expr:
        expr = self._parse_equality()
        while self._match(TokenType.AND):
            op = self._previous().type
            right = self._parse_equality()
            expr = BinaryExpr(left=expr, op=op, right=right)
        return expr

    def _parse_equality(self) -> Expr:
        expr = self._parse_comparison()
        while self._match(TokenType.EQEQ, TokenType.NEQ):
            op = self._previous().type
            right = self._parse_comparison()
            expr = BinaryExpr(left=expr, op=op, right=right)
        return expr

    def _parse_comparison(self) -> Expr:
        expr = self._parse_term()
        while self._match(TokenType.LT, TokenType.LTEQ, TokenType.GT, TokenType.GTEQ):
            op = self._previous().type
            right = self._parse_term()
            expr = BinaryExpr(left=expr, op=op, right=right)
        return expr

    def _parse_term(self) -> Expr:
        expr = self._parse_factor()
        while self._match(TokenType.PLUS, TokenType.MINUS):
            op = self._previous().type
            right = self._parse_factor()
            expr = BinaryExpr(left=expr, op=op, right=right)
        return expr


    def _parse_factor(self) -> Expr:
        expr = self._parse_unary()
        while self._match(TokenType.STAR, TokenType.SLASH):
            op = self._previous().type
            right = self._parse_unary()
            expr = BinaryExpr(left=expr, op=op, right=right)
        return expr

    def _parse_unary(self) -> Expr:
        if self._match(TokenType.EXCL, TokenType.MINUS):
            op = self._previous().type
            right = self._parse_unary()
            return UnaryExpr(op=op, right=right)
        return self._parse_call()

    def _parse_call(self) -> Expr:
        expr = self._parse_primary()
        while True:
            if self._match(TokenType.LPAREN):
                args =[]
                if not self._check(TokenType.RPAREN):
                    while True:
                        args.append(self._parse_expression())
                        if not self._match(TokenType.COMMA):
                            break
                self._consume(TokenType.RPAREN, "Ожидается ')' после аргументов.")
                expr = CallExpr(callee=expr, arguments=args)
            else:
                break
        return expr

    def _parse_primary(self) -> Expr:
        if self._match(TokenType.NUMBER):
            return NumberExpr(value=float(self._previous().value))

        if self._match(TokenType.STRING):
            return StringExpr(value=self._previous().value)

        if self._match(TokenType.ID):
            return VariableExpr(name=self._previous().value)

        if self._match(TokenType.LPAREN):
            expr = self._parse_expression()
            self._consume(TokenType.RPAREN, "Ожидается ')' после выражения.")
            return expr

        error_token = self._peek()
        raise ParseError(f"[Parser Error] Line {error_token.line}, Col {error_token.column}: Ожидается выражение.")

    # --- Вспомогательные функции ---

    def _match(self, *types: TokenType) -> bool:
        for t in types:
            if self._check(t):
                self._advance()
                return True
        return False

    def _check(self, type_: TokenType) -> bool:
        if self._is_at_end():
            return False
        return self._peek().type == type_

    def _advance(self) -> Token:
        if not self._is_at_end():
            self._position += 1
        return self._previous()

    def _is_at_end(self) -> bool:
        return self._peek().type == TokenType.END_OF_FILE

    def _peek(self) -> Token:
        return self._tokens[self._position]

    def _previous(self) -> Token:
        return self._tokens[self._position - 1]

    def _consume(self, type_: TokenType, message: str) -> Token:
        if self._check(type_):
            return self._advance()
        token = self._peek()
        raise ParseError(f"[Parser Error] Line {token.line}, Col {token.column}: {message}")
