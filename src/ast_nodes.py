from dataclasses import dataclass
from typing import List, Optional, Tuple
from enum import Enum, auto
from token_type import TokenType

class DataType(Enum):
    NUMBER = auto()
    STRING = auto()
    BOOL = auto()

class Expr: pass
class Stmt: pass

@dataclass
class NumberExpr(Expr):
    value: float

@dataclass
class StringExpr(Expr):
    value: str

@dataclass
class VariableExpr(Expr):
    name: str

@dataclass
class UnaryExpr(Expr):
    op: TokenType
    right: Expr

@dataclass
class BinaryExpr(Expr):
    left: Expr
    op: TokenType
    right: Expr

@dataclass
class AssignExpr(Expr):
    name: str
    value: Expr

@dataclass
class CallExpr(Expr):
    callee: Expr
    arguments: List[Expr]

# --- Инструкции (Statements) ---

@dataclass
class ExpressionStmt(Stmt):
    expr: Expr

@dataclass
class PrintStmt(Stmt):
    expr: Expr

@dataclass
class VarStmt(Stmt):
    name: str
    type: DataType
    initializer: Optional[Expr]

@dataclass
class BlockStmt(Stmt):
    statements: List[Stmt]

@dataclass
class IfStmt(Stmt):
    condition: Expr
    then_branch: Stmt
    else_branch: Optional[Stmt]

@dataclass
class WhileStmt(Stmt):
    condition: Expr
    body: Stmt

@dataclass
class ReturnStmt(Stmt):
    value: Optional[Expr]

@dataclass
class FunctionStmt(Stmt):
    name: str
    params: List[Tuple[str, DataType]]
    return_type: DataType
    body: List[Stmt]
