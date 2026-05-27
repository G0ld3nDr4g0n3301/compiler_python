from ast_nodes import *
from token_type import TokenType
from dataclasses import dataclass, field
from typing import List, Optional, Dict

@dataclass
class VariableInfo:
    type: DataType
    declared: bool = True
    initialized: bool = False
    used: bool = False
    is_function: bool = False
    param_types: List[DataType] = field(default_factory=list)
    return_type: Optional[DataType] = None

class SemanticEnvironment:
    def __init__(self, parent: Optional['SemanticEnvironment'] = None):
        self.parent = parent
        self._variables: Dict[str, VariableInfo] = {}

    def define_variable(self, name: str, var_type: DataType, initialized: bool = False) -> bool:
        if name in self._variables:
            return False
        self._variables[name] = VariableInfo(type=var_type, initialized=initialized)
        return True

    def lookup(self, name: str) -> Optional[VariableInfo]:
        if name in self._variables:
            return self._variables[name]
        if self.parent:
            return self.parent.lookup(name)
        return None

    def is_defined(self, name: str) -> bool:
        return self.lookup(name) is not None

    def mark_used(self, name: str):
        info = self.lookup(name)
        if info:
            info.used = True

    def collect_unused(self, warnings: List[str]):
        for name, info in self._variables.items():
            if info.declared and not info.used:
                warnings.append(f"Warning: variable '{name}' declared but never used.")

class SemanticAnalyzer:
    def __init__(self):
        self._root_env = SemanticEnvironment()
        self._current_env = self._root_env
        self.warnings: List[str] = []
        
        self._current_function_return_type: DataType = DataType.NUMBER
        self._in_function = False
        self._has_return = False

    def analyze(self, statements: List[Stmt]):
        for stmt in statements:
            self._visit_statement(stmt)
        self._root_env.collect_unused(self.warnings)

    def _visit_statement(self, stmt: Stmt):
        if isinstance(stmt, VarStmt):
            initialized = stmt.initializer is not None
            if initialized:
                init_type = self._visit_expression(stmt.initializer)
                if init_type != stmt.type:
                    is_empty_array_assignment = (
                        init_type == DataType.EMPTY_ARRAY and 
                        stmt.type in (DataType.NUMBER_ARRAY, DataType.STRING_ARRAY, DataType.BOOL_ARRAY)
                    )
                    if not is_empty_array_assignment:
                        self._add_error(f"Type mismatch: cannot initialize variable '{stmt.name}' with value of different type.")
            if not self._current_env.define_variable(stmt.name, stmt.type, initialized):
                self._add_error(f"Variable '{stmt.name}' is already defined in this scope.")

        elif isinstance(stmt, FunctionStmt):
            p_types = [p[1] for p in stmt.params]
            if not self._current_env.define_variable(stmt.name, stmt.return_type, True):
                self._add_error(f"Name '{stmt.name}' is already defined.")
            else:
                info = self._current_env.lookup(stmt.name)
                info.is_function = True
                info.param_types = p_types
                info.return_type = stmt.return_type

            new_env = SemanticEnvironment(self._current_env)
            old_env = self._current_env
            self._current_env = new_env

            for param_name, param_type in stmt.params:
                self._current_env.define_variable(param_name, param_type, True)

            old_in_func = self._in_function
            old_ret_type = self._current_function_return_type
            old_has_ret = self._has_return

            self._in_function = True
            self._current_function_return_type = stmt.return_type
            self._has_return = False

            for substmt in stmt.body:
                self._visit_statement(substmt)

            if not self._has_return:
                self._add_error(f"Function '{stmt.name}' must return a value of correct type.")

            self._in_function = old_in_func
            self._current_function_return_type = old_ret_type
            self._has_return = old_has_ret
            
            self._current_env.collect_unused(self.warnings)
            self._current_env = old_env

        elif isinstance(stmt, ReturnStmt):
            if not self._in_function:
                self._add_error("Return statement outside of a function.")
                return
            actual_type = DataType.NUMBER
            if stmt.value:
                actual_type = self._visit_expression(stmt.value)
            
            if actual_type != self._current_function_return_type:
                is_empty_array_assignment = (
                    actual_type == DataType.EMPTY_ARRAY and 
                    self._current_function_return_type in (DataType.NUMBER_ARRAY, DataType.STRING_ARRAY, DataType.BOOL_ARRAY)
                )
                if not is_empty_array_assignment:
                    self._add_error("Return type mismatch. Expected correct type.")
            self._has_return = True

        elif isinstance(stmt, PrintStmt):
            self._visit_expression(stmt.expr)

        elif isinstance(stmt, ExpressionStmt):
            self._visit_expression(stmt.expr)

        elif isinstance(stmt, BlockStmt):
            new_env = SemanticEnvironment(self._current_env)
            old_env = self._current_env
            self._current_env = new_env
            for substmt in stmt.statements:
                self._visit_statement(substmt)
            self._current_env.collect_unused(self.warnings)
            self._current_env = old_env

        elif isinstance(stmt, IfStmt):
            self._visit_expression(stmt.condition)
            self._visit_statement(stmt.then_branch)
            if stmt.else_branch:
                self._visit_statement(stmt.else_branch)

        elif isinstance(stmt, WhileStmt):
            self._visit_expression(stmt.condition)
            self._visit_statement(stmt.body)


    def _visit_expression(self, expr: Expr) -> DataType:
        if isinstance(expr, NumberExpr): return DataType.NUMBER
        elif isinstance(expr, StringExpr): return DataType.STRING
        
        elif isinstance(expr, ArrayExpr):
            if not expr.elements:
                return DataType.EMPTY_ARRAY
            
            first_type = self._visit_expression(expr.elements[0])
            for idx, element in enumerate(expr.elements[1:], start=1):
                t = self._visit_expression(element)
                if t != first_type:
                    self._add_error(f"Array elements must be of the same type. Element at index {idx} has different type.")
            
            if first_type == DataType.NUMBER:
                return DataType.NUMBER_ARRAY
            elif first_type == DataType.STRING:
                return DataType.STRING_ARRAY
            elif first_type == DataType.BOOL:
                return DataType.BOOL_ARRAY
            return DataType.NUMBER_ARRAY

        elif isinstance(expr, IndexExpr):
            arr_type = self._visit_expression(expr.array)
            idx_type = self._visit_expression(expr.index)
            
            if idx_type != DataType.NUMBER:
                self._add_error("Array index must be a number.")
            
            if arr_type == DataType.NUMBER_ARRAY:
                return DataType.NUMBER
            elif arr_type == DataType.STRING_ARRAY:
                return DataType.STRING
            elif arr_type == DataType.BOOL_ARRAY:
                return DataType.BOOL
            else:
                self._add_error("Cannot index into non-array type.")
                return DataType.NUMBER

        elif isinstance(expr, IndexAssignExpr):
            arr_type = self._visit_expression(expr.array)
            idx_type = self._visit_expression(expr.index)
            val_type = self._visit_expression(expr.value)
            
            if idx_type != DataType.NUMBER:
                self._add_error("Array index must be a number.")
                
            expected_val_type = None
            if arr_type == DataType.NUMBER_ARRAY:
                expected_val_type = DataType.NUMBER
            elif arr_type == DataType.STRING_ARRAY:
                expected_val_type = DataType.STRING
            elif arr_type == DataType.BOOL_ARRAY:
                expected_val_type = DataType.BOOL
            else:
                self._add_error("Cannot assign index of non-array type.")
                
            if expected_val_type and val_type != expected_val_type:
                self._add_error(f"Type mismatch: cannot assign value of type {val_type.name} to array element of type {expected_val_type.name}.")
                
            return val_type

        elif isinstance(expr, CallExpr):
            self._visit_expression(expr.callee)
            if isinstance(expr.callee, VariableExpr):
                info = self._current_env.lookup(expr.callee.name)
                if not info or not info.is_function:
                    self._add_error(f"Attempted to call a non-function '{expr.callee.name}'.")
                    return DataType.NUMBER
                
                if len(info.param_types) != len(expr.arguments):
                    self._add_error(f"Function '{expr.callee.name}' expects {len(info.param_types)} arguments.")
                else:
                    for i, arg in enumerate(expr.arguments):
                        arg_type = self._visit_expression(arg)
                        if arg_type != info.param_types[i]:
                            self._add_error("Argument type mismatch in function call.")
                return info.return_type
            return DataType.NUMBER

        elif isinstance(expr, VariableExpr):
            if not self._current_env.is_defined(expr.name):
                self._add_error(f"Variable '{expr.name}' is not defined.")
                return DataType.NUMBER
            else:
                self._current_env.mark_used(expr.name)
                info = self._current_env.lookup(expr.name)
                return info.type if info else DataType.NUMBER

        elif isinstance(expr, AssignExpr):
            val_type = self._visit_expression(expr.value)
            if not self._current_env.is_defined(expr.name):
                self._add_error(f"Variable '{expr.name}' is not defined.")
                return val_type
            info = self._current_env.lookup(expr.name)
            if info:
                is_empty_array_assignment = (
                    val_type == DataType.EMPTY_ARRAY and 
                    info.type in (DataType.NUMBER_ARRAY, DataType.STRING_ARRAY, DataType.BOOL_ARRAY)
                )
                if info.type != val_type and not is_empty_array_assignment:
                    self._add_error(f"Type mismatch: cannot assign to variable '{expr.name}'.")
            return val_type

        elif isinstance(expr, UnaryExpr):
            operand_type = self._visit_expression(expr.right)
            if expr.op == TokenType.MINUS and operand_type != DataType.NUMBER:
                self._add_error("Unary '-' requires number operand.")
            if expr.op == TokenType.EXCL and operand_type != DataType.BOOL:
                self._add_error("Logical '!' requires bool operand.")
            return DataType.NUMBER if expr.op == TokenType.MINUS else DataType.BOOL

        elif isinstance(expr, BinaryExpr):
            left_type = self._visit_expression(expr.left)
            right_type = self._visit_expression(expr.right)
            
            if expr.op in (TokenType.PLUS, TokenType.MINUS, TokenType.STAR, TokenType.SLASH):
                if expr.op == TokenType.PLUS and left_type == DataType.STRING and right_type == DataType.STRING:
                    return DataType.STRING
                if left_type != DataType.NUMBER or right_type != DataType.NUMBER:
                    self._add_error("Math operators require number operands.")
                return DataType.NUMBER
                
            elif expr.op in (TokenType.EQEQ, TokenType.NEQ, TokenType.LT, TokenType.LTEQ, TokenType.GT, TokenType.GTEQ):
                return DataType.BOOL
                
            elif expr.op in (TokenType.AND, TokenType.OR):
                if left_type != DataType.BOOL or right_type != DataType.BOOL:
                    self._add_error("Logical operators require bool operands.")
                return DataType.BOOL

        return DataType.NUMBER

    def _add_error(self, msg: str):
        self.warnings.append(f"[Error] {msg}")