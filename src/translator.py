from ast_nodes import *
from token_type import TokenType
from llmr import OpCode, LLMRInstruction, LLMRProgram

class AstToLLMRTranslator:
    def __init__(self):
        self._program = LLMRProgram()
        self._temp_counter = 0
        self._label_counter = 0

    def translate(self, statements: list[Stmt]) -> LLMRProgram:
        for stmt in statements:
            self._translate_stmt(stmt)
        return self._program

    def _new_temp(self) -> str:
        name = f"t{self._temp_counter}"
        self._temp_counter += 1
        return name

    def _new_label(self) -> str:
        name = f"L{self._label_counter}"
        self._label_counter += 1
        return name

    def _emit(self, op: OpCode, result: str = "", arg1: str = "", arg2: str = ""):
        self._program.instructions.append(LLMRInstruction(op, result, arg1, arg2))

    def _translate_stmt(self, stmt: Stmt):
        if stmt is None: return

        if isinstance(stmt, VarStmt):
            if stmt.initializer:
                val = self._translate_expr(stmt.initializer)
                self._emit(OpCode.ASSIGN, stmt.name, val)
                
        elif isinstance(stmt, PrintStmt):
            val = self._translate_expr(stmt.expr)
            self._emit(OpCode.PRINT, "", val)
            
        elif isinstance(stmt, ExpressionStmt):
            self._translate_expr(stmt.expr)
            
        elif isinstance(stmt, BlockStmt):
            for child in stmt.statements:
                self._translate_stmt(child)
                
        elif isinstance(stmt, IfStmt):
            cond = self._translate_expr(stmt.condition)
            else_label = self._new_label()
            end_label = self._new_label()

            self._emit(OpCode.JMP_IF_FALSE, "", cond, else_label)
            self._translate_stmt(stmt.then_branch)
            self._emit(OpCode.JMP, "", end_label)
            
            self._emit(OpCode.LABEL, "", else_label)
            if stmt.else_branch:
                self._translate_stmt(stmt.else_branch)
            self._emit(OpCode.LABEL, "", end_label)
            
        elif isinstance(stmt, WhileStmt):
            start_label = self._new_label()
            end_label = self._new_label()

            self._emit(OpCode.LABEL, "", start_label)
            cond = self._translate_expr(stmt.condition)
            self._emit(OpCode.JMP_IF_FALSE, "", cond, end_label)
            
            self._translate_stmt(stmt.body)
            self._emit(OpCode.JMP, "", start_label)
            self._emit(OpCode.LABEL, "", end_label)
            
        elif isinstance(stmt, FunctionStmt):
            self._emit(OpCode.FUNC_START, "", stmt.name)
            for child in stmt.body:
                self._translate_stmt(child)
            self._emit(OpCode.FUNC_END)
            
        elif isinstance(stmt, ReturnStmt):
            if stmt.value:
                val = self._translate_expr(stmt.value)
                self._emit(OpCode.RET, "", val)
            else:
                self._emit(OpCode.RET)

    def _translate_expr(self, expr: Expr) -> str:
        if expr is None: return ""


        if isinstance(expr, NumberExpr):
            t = self._new_temp()
            val = str(expr.value)
            if val.endswith('.0'): 
                val = val[:-2]
            self._emit(OpCode.CONST, t, val)
            return t
            
        elif isinstance(expr, StringExpr):
            t = self._new_temp()
            self._emit(OpCode.CONST, t, f'"{expr.value}"')
            return t
            
        elif isinstance(expr, VariableExpr):
            return expr.name
            
        elif isinstance(expr, AssignExpr):
            val = self._translate_expr(expr.value)
            self._emit(OpCode.ASSIGN, expr.name, val)
            return expr.name
            
        elif isinstance(expr, UnaryExpr):
            right = self._translate_expr(expr.right)
            t = self._new_temp()
            if expr.op == TokenType.MINUS:
                self._emit(OpCode.SUB, t, "0", right)
            elif expr.op == TokenType.EXCL:
                self._emit(OpCode.NOT, t, right)
            return t
            
        elif isinstance(expr, BinaryExpr):
            left = self._translate_expr(expr.left)
            right = self._translate_expr(expr.right)
            t = self._new_temp()

            op_map = {
                TokenType.PLUS: OpCode.ADD, TokenType.MINUS: OpCode.SUB,
                TokenType.STAR: OpCode.MUL, TokenType.SLASH: OpCode.DIV,
                TokenType.EQEQ: OpCode.EQ, TokenType.NEQ: OpCode.NEQ,
                TokenType.LT: OpCode.LT, TokenType.LTEQ: OpCode.LTEQ,
                TokenType.GT: OpCode.GT, TokenType.GTEQ: OpCode.GTEQ,
                TokenType.AND: OpCode.AND, TokenType.OR: OpCode.OR
            }
            op = op_map.get(expr.op, OpCode.ADD)
            self._emit(op, t, left, right)
            return t
            
        elif isinstance(expr, CallExpr):
            arg_temps = [self._translate_expr(arg) for arg in expr.arguments]
            for arg_t in arg_temps:
                self._emit(OpCode.PARAM, "", arg_t)
                
            t = self._new_temp()
            func_name = expr.callee.name if isinstance(expr.callee, VariableExpr) else "Unknown"
            self._emit(OpCode.CALL, t, func_name, str(len(arg_temps)))
            return t
            
        return ""
