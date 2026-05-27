from ast_nodes import *
from token_type import TokenType

class AstPrinter:
    def print_ast(self, statements: list[Stmt]):
        for stmt in statements:
            self._print_stmt(stmt, 0)

    def _print_stmt(self, stmt: Stmt, indent: int):
        tab = "  " * indent

        if isinstance(stmt, VarStmt):
            print(f"{tab}VarDecl: {stmt.name} ({self._type_to_str(stmt.type)})")
            if stmt.initializer:
                self._print_expr(stmt.initializer, indent + 1)
        
        elif isinstance(stmt, PrintStmt):
            print(f"{tab}Print:")
            self._print_expr(stmt.expr, indent + 1)
            
        elif isinstance(stmt, BlockStmt):
            print(f"{tab}Block:")
            for substmt in stmt.statements:
                self._print_stmt(substmt, indent + 1)
                
        elif isinstance(stmt, IfStmt):
            print(f"{tab}If:")
            print(f"{tab}  Cond:")
            self._print_expr(stmt.condition, indent + 2)
            print(f"{tab}  Then:")
            self._print_stmt(stmt.then_branch, indent + 2)
            if stmt.else_branch:
                print(f"{tab}  Else:")
                self._print_stmt(stmt.else_branch, indent + 2)
                
        elif isinstance(stmt, WhileStmt):
            print(f"{tab}While:")
            print(f"{tab}  Cond:")
            self._print_expr(stmt.condition, indent + 2)
            print(f"{tab}  Body:")
            self._print_stmt(stmt.body, indent + 2)
            
        elif isinstance(stmt, ExpressionStmt):
            self._print_expr(stmt.expr, indent)
            
        elif isinstance(stmt, FunctionStmt):
            params_str = ", ".join(f"{name} : {self._type_to_str(typ)}" for name, typ in stmt.params)
            ret_str = self._type_to_str(stmt.return_type)
            print(f"{tab}Function: {stmt.name} ({params_str}) -> {ret_str}")
            print(f"{tab}  Body:")
            for substmt in stmt.body:
                self._print_stmt(substmt, indent + 2)
                
        elif isinstance(stmt, ReturnStmt):
            print(f"{tab}Return:")
            if stmt.value:
                self._print_expr(stmt.value, indent + 1)

    def _print_expr(self, expr: Expr, indent: int):
        tab = "  " * indent

        if isinstance(expr, NumberExpr):
            print(f"{tab}Num: {expr.value}")
            
        elif isinstance(expr, StringExpr):
            print(f"{tab}String: \"{expr.value}\"")
            
        elif isinstance(expr, VariableExpr):
            print(f"{tab}Var: {expr.name}")
            
        elif isinstance(expr, BinaryExpr):
            print(f"{tab}BinaryOp ({self._token_type_to_string(expr.op)}):")
            self._print_expr(expr.left, indent + 1)
            self._print_expr(expr.right, indent + 1)
            
        elif isinstance(expr, UnaryExpr):
            print(f"{tab}UnaryOp ({self._token_type_to_string(expr.op)}):")
            self._print_expr(expr.right, indent + 1)
            
        elif isinstance(expr, AssignExpr):
            print(f"{tab}Assign: {expr.name}")
            self._print_expr(expr.value, indent + 1)

        elif isinstance(expr, ArrayExpr):
            print(f"{tab}ArrayLiteral:")
            if expr.elements:
                for element in expr.elements:
                    self._print_expr(element, indent + 1)
            else:
                print(f"{tab}  (empty)")

        elif isinstance(expr, IndexExpr):
            print(f"{tab}IndexAccess:")
            print(f"{tab}  Array:")
            self._print_expr(expr.array, indent + 2)
            print(f"{tab}  Index:")
            self._print_expr(expr.index, indent + 2)

        elif isinstance(expr, IndexAssignExpr):
            print(f"{tab}IndexAssign:")
            print(f"{tab}  Array:")
            self._print_expr(expr.array, indent + 2)
            print(f"{tab}  Index:")
            self._print_expr(expr.index, indent + 2)
            print(f"{tab}  Value:")
            self._print_expr(expr.value, indent + 2)
            
        elif isinstance(expr, CallExpr):
            print(f"{tab}Call:")
            print(f"{tab}  Callee:")
            self._print_expr(expr.callee, indent + 2)
            if expr.arguments:
                print(f"{tab}  Arguments:")
                for arg in expr.arguments:
                    self._print_expr(arg, indent + 2)
            else:
                print(f"{tab}  Arguments: (none)")

    def _type_to_str(self, typ: DataType) -> str:
        if typ == DataType.NUMBER: return "number"
        if typ == DataType.STRING: return "string"
        if typ == DataType.BOOL: return "bool"
        if typ == DataType.NUMBER_ARRAY: return "number[]"
        if typ == DataType.STRING_ARRAY: return "string[]"
        if typ == DataType.BOOL_ARRAY: return "bool[]"
        if typ == DataType.EMPTY_ARRAY: return "[]"
        return "unknown"


    def _token_type_to_string(self, typ: TokenType) -> str:
        mapping = {
            TokenType.PLUS: "+", TokenType.MINUS: "-",
            TokenType.STAR: "*", TokenType.SLASH: "/",
            TokenType.EQEQ: "==", TokenType.LT: "<",
            TokenType.GT: ">", TokenType.AND: "&&",
            TokenType.OR: "||"
        }
        return mapping.get(typ, "?")