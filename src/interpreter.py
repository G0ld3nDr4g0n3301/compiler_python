from ast_nodes import *
from token_type import TokenType
from typing import Any

class ReturnException(Exception):
    def __init__(self, value: Any):
        self.value = value

class CallableObj:
    def __init__(self, declaration: FunctionStmt, closure: 'RuntimeEnvironment'):
        self.declaration = declaration
        self.closure = closure

class RuntimeEnvironment:
    def __init__(self, enclosing: 'RuntimeEnvironment' = None):
        self.enclosing = enclosing
        self._values = {}

    def define(self, name: str, value: Any):
        self._values[name] = value

    def assign(self, name: str, value: Any):
        if name in self._values:
            self._values[name] = value
            return
        if self.enclosing:
            self.enclosing.assign(name, value)
            return
        raise RuntimeError(f"Undefined variable '{name}'.")

    def get(self, name: str) -> Any:
        if name in self._values:
            return self._values[name]
        if self.enclosing:
            return self.enclosing.get(name)
        raise RuntimeError(f"Undefined variable '{name}'.")

class Interpreter:
    def __init__(self):
        self.environment = RuntimeEnvironment()

    def interpret(self, statements: list[Stmt]):
        try:
            for stmt in statements:
                self._execute(stmt)
        except Exception as e:
            print(f"[Runtime Error] {e}")

    def _execute(self, stmt: Stmt):
        if isinstance(stmt, VarStmt):
            value = 0.0
            if stmt.initializer:
                value = self._evaluate(stmt.initializer)
            elif stmt.type == DataType.STRING:
                value = ""
            elif stmt.type == DataType.BOOL:
                value = False
            elif stmt.type in (DataType.NUMBER_ARRAY, DataType.STRING_ARRAY, DataType.BOOL_ARRAY):
                value = []
            self.environment.define(stmt.name, value)

        elif isinstance(stmt, FunctionStmt):
            func_obj = CallableObj(stmt, self.environment)
            self.environment.define(stmt.name, func_obj)

        elif isinstance(stmt, ReturnStmt):
            value = 0.0
            if stmt.value:
                value = self._evaluate(stmt.value)
            raise ReturnException(value)

        elif isinstance(stmt, PrintStmt):
            val = self._evaluate(stmt.expr)
            print(self._stringify(val))

        elif isinstance(stmt, ExpressionStmt):
            self._evaluate(stmt.expr)

        elif isinstance(stmt, BlockStmt):
            previous_env = self.environment
            self.environment = RuntimeEnvironment(previous_env)
            try:
                for substmt in stmt.statements:
                    self._execute(substmt)
            finally:
                self.environment = previous_env

        elif isinstance(stmt, IfStmt):
            cond_val = self._evaluate(stmt.condition)
            if self._is_truthy(cond_val):
                self._execute(stmt.then_branch)
            elif stmt.else_branch:
                self._execute(stmt.else_branch)

        elif isinstance(stmt, WhileStmt):
            while self._is_truthy(self._evaluate(stmt.condition)):
                self._execute(stmt.body)

    def _evaluate(self, expr: Expr) -> Any:
        if isinstance(expr, NumberExpr):
            return expr.value
        elif isinstance(expr, StringExpr):
            return expr.value
        elif isinstance(expr, VariableExpr):
            return self.environment.get(expr.name)
        
        elif isinstance(expr, ArrayExpr):
            return [self._evaluate(el) for el in expr.elements]

        elif isinstance(expr, IndexExpr):
            arr = self._evaluate(expr.array)
            idx = self._evaluate(expr.index)
            
            if not isinstance(arr, list):
                raise RuntimeError("Target is not an array.")
            if not isinstance(idx, (int, float)):
                raise RuntimeError("Array index must be a number.")
            
            int_idx = int(idx)
            if int_idx != idx:
                raise RuntimeError(f"Array index must be an integer, got {idx}.")
            
            if int_idx < 0 or int_idx >= len(arr):
                raise RuntimeError(f"Index {int_idx} out of bounds for array of length {len(arr)}.")
            
            return arr[int_idx]

        elif isinstance(expr, IndexAssignExpr):
            arr = self._evaluate(expr.array)
            idx = self._evaluate(expr.index)
            val = self._evaluate(expr.value)
            
            if not isinstance(arr, list):
                raise RuntimeError("Target is not an array.")
            if not isinstance(idx, (int, float)):
                raise RuntimeError("Array index must be a number.")
            
            int_idx = int(idx)
            if int_idx != idx:
                raise RuntimeError(f"Array index must be an integer, got {idx}.")
            
            if int_idx < 0 or int_idx >= len(arr):
                raise RuntimeError(f"Index {int_idx} out of bounds for array of length {len(arr)}.")
            
            arr[int_idx] = val
            return val

        elif isinstance(expr, AssignExpr):
            val = self._evaluate(expr.value)
            self.environment.assign(expr.name, val)
            return val

        elif isinstance(expr, CallExpr):
            callee = self._evaluate(expr.callee)
            if not isinstance(callee, CallableObj):
                raise RuntimeError("Attempted to call a non-callable object.")
            
            args = [self._evaluate(a) for a in expr.arguments]
            
            prev_env = self.environment
            self.environment = RuntimeEnvironment(callee.closure)
            
            for i, (param_name, _) in enumerate(callee.declaration.params):
                self.environment.define(param_name, args[i])
                
            try:
                for stmt in callee.declaration.body:
                    self._execute(stmt)
            except ReturnException as ret:
                self.environment = prev_env
                return ret.value
            finally:
                self.environment = prev_env
                
            return 0.0

        elif isinstance(expr, UnaryExpr):
            right = self._evaluate(expr.right)
            if expr.op == TokenType.MINUS: return -float(right)
            if expr.op == TokenType.EXCL: return not self._is_truthy(right)

        elif isinstance(expr, BinaryExpr):
            if expr.op == TokenType.OR:
                left = self._evaluate(expr.left)
                if self._is_truthy(left): return True
                return self._is_truthy(self._evaluate(expr.right))
                
            if expr.op == TokenType.AND:
                left = self._evaluate(expr.left)
                if not self._is_truthy(left): return False
                return self._is_truthy(self._evaluate(expr.right))

            left = self._evaluate(expr.left)
            right = self._evaluate(expr.right)

            if expr.op == TokenType.PLUS: return left + right
            if expr.op == TokenType.MINUS: return float(left) - float(right)
            if expr.op == TokenType.STAR: return float(left) * float(right)
            if expr.op == TokenType.SLASH: return float(left) / float(right)
            
            if expr.op == TokenType.GT: return left > right
            if expr.op == TokenType.GTEQ: return left >= right
            if expr.op == TokenType.LT: return left < right
            if expr.op == TokenType.LTEQ: return left <= right
            
            if expr.op == TokenType.EQEQ: return left == right
            if expr.op == TokenType.NEQ: return left != right

        return 0.0

    def _is_truthy(self, val: Any) -> bool:
        if isinstance(val, bool): return val
        if isinstance(val, (int, float)): return val != 0.0
        if isinstance(val, str): return bool(val)
        if isinstance(val, list): return len(val) > 0
        return False

    def _stringify(self, val: Any) -> str:
        if isinstance(val, CallableObj):
            return f"<function {val.declaration.name}>"
        if isinstance(val, bool):
            return "true" if val else "false"
        if isinstance(val, (int, float)):
            if val == int(val): return str(int(val))
            return str(val)
        if isinstance(val, list):
            elements_str = ", ".join(self._stringify(item) for item in val)
            return f"[{elements_str}]"
        return str(val)