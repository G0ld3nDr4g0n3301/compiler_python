from token_type import Token, TokenType

KEYWORDS = {
    "var": TokenType.VAR,
    "print": TokenType.PRINT,
    "if": TokenType.IF,
    "else": TokenType.ELSE,
    "while": TokenType.WHILE,
    "number": TokenType.NUMBER_TYPE,
    "string": TokenType.STRING_TYPE,
    "bool": TokenType.BOOL_TYPE,
    "func": TokenType.FUNC,
    "return": TokenType.RETURN
}

OPERATORS = {
    "==": TokenType.EQEQ,
    "!=": TokenType.NEQ,
    "<=": TokenType.LTEQ,
    ">=": TokenType.GTEQ,
    "&&": TokenType.AND,
    "||": TokenType.OR,
    "+": TokenType.PLUS,
    "-": TokenType.MINUS,
    "*": TokenType.STAR,
    "/": TokenType.SLASH,
    "=": TokenType.EQ,
    "<": TokenType.LT,
    ">": TokenType.GT,
    "!": TokenType.EXCL,
    "(": TokenType.LPAREN,
    ")": TokenType.RPAREN,
    "{": TokenType.LBRACE,
    "}": TokenType.RBRACE,
    ";": TokenType.SEMICOLON,
    ":": TokenType.COLON,
    ",": TokenType.COMMA
}

class Lexer:
    def __init__(self, text: str):
        self._input = text
        self._position = 0
        self._line = 1
        self._column = 1

    def tokenize(self) -> list[Token]:
        tokens =[]
        
        while self._position < len(self._input):
            current = self._peek()

            if current.isspace():
                self._next()
                continue

            if current.isdigit():
                tokens.append(self._read_number())
                continue

            if current.isalpha() or current == '_':
                tokens.append(self._read_word())
                continue

            if current == '"':
                tokens.append(self._read_string())
                continue

            tokens.append(self._read_operator_or_punctuation())

        tokens.append(Token(TokenType.END_OF_FILE, "\0", self._position, self._line, self._column))
        return tokens

    def _read_number(self) -> Token:
        start_pos, start_line, start_col = self._position, self._line, self._column
        while self._peek().isdigit():
            self._next()
            
        text = self._input[start_pos:self._position]
        return Token(TokenType.NUMBER, text, start_pos, start_line, start_col)

    def _read_word(self) -> Token:
        start_pos, start_line, start_col = self._position, self._line, self._column
        while self._peek().isalnum() or self._peek() == '_':
            self._next()
            
        text = self._input[start_pos:self._position]
        token_type = KEYWORDS.get(text, TokenType.ID)
        return Token(token_type, text, start_pos, start_line, start_col)

    def _read_string(self) -> Token:
        start_pos, start_line, start_col = self._position, self._line, self._column
        self._next() # Пропускаем открывающую кавычку

        while self._peek() != '"' and not self._is_at_end():
            self._next()

        if self._peek() != '"':
            raise RuntimeError(f"[Lexer Error] Unclosed string literal at line {start_line}, Column {start_col}")

        # Берем текст без кавычек
        text = self._input[start_pos + 1 : self._position]
        self._next() # Пропускаем закрывающую кавычку
        
        return Token(TokenType.STRING, text, start_pos, start_line, start_col)

    def _read_operator_or_punctuation(self) -> Token:
        start_pos, start_line, start_col = self._position, self._line, self._column

        # Пробуем считать 2 символа
        if self._position + 1 < len(self._input):
            two_chars = self._input[self._position : self._position + 2]
            if two_chars in OPERATORS:
                self._next()
                self._next()
                return Token(OPERATORS[two_chars], two_chars, start_pos, start_line, start_col)

        # Пробуем считать 1 символ
        one_char = self._input[self._position : self._position + 1]
        if one_char in OPERATORS:
            self._next()
            return Token(OPERATORS[one_char], one_char, start_pos, start_line, start_col)

        bad_char = self._peek()
        raise RuntimeError(f"[Lexer Error] Unexpected character '{bad_char}' at Line {start_line}, Column {start_col}")

    def _peek(self) -> str:
        if self._position >= len(self._input):
            return '\0'
        return self._input[self._position]

    def _next(self) -> str:
        if self._position >= len(self._input):
            return '\0'

        current = self._input[self._position]
        self._position += 1

        if current == '\n':
            self._line += 1
            self._column = 1
        else:
            self._column += 1

        return current

    def _is_at_end(self) -> bool:
        return self._position >= len(self._input)
