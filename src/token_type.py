from enum import Enum, auto
from dataclasses import dataclass

class TokenType(Enum):
    NUMBER = auto()
    ID = auto()
    STRING = auto()
    VAR = auto()
    PRINT = auto()
    IF = auto()
    ELSE = auto()
    WHILE = auto()
    PLUS = auto()
    MINUS = auto()
    STAR = auto()
    SLASH = auto()
    STRING_TYPE = auto()
    BOOL_TYPE = auto()
    NUMBER_TYPE = auto()
    EQ = auto()
    EQEQ = auto()
    EXCL = auto()
    NEQ = auto()
    LT = auto()
    GT = auto()
    LTEQ = auto()
    GTEQ = auto()
    AND = auto()
    OR = auto()
    LPAREN = auto()
    RPAREN = auto()
    LBRACE = auto()
    RBRACE = auto()
    LBRACKET = auto()
    RBRACKET = auto()
    SEMICOLON = auto()
    COLON = auto()
    END_OF_FILE = auto()
    FUNC = auto()
    RETURN = auto()
    COMMA = auto()

@dataclass
class Token:
    type: TokenType
    value: str
    position: int
    line: int
    column: int