from ast_nodes import *

class DeadCodeEliminator:
    def optimize(self, statements: list[Stmt]) -> list[Stmt]:
        optimized = []
        for stmt in statements:
            opt = self._optimize_stmt(stmt)
            if opt:
                is_return = isinstance(opt, ReturnStmt)
                optimized.append(opt)
                if is_return:
                    break
        return optimized

    def _optimize_stmt(self, stmt: Stmt) -> Stmt | None:
        if stmt is None: return None

        if isinstance(stmt, BlockStmt):
            new_stmts = []
            for child in stmt.statements:
                opt = self._optimize_stmt(child)
                if opt:
                    is_return = isinstance(opt, ReturnStmt)
                    new_stmts.append(opt)
                    if is_return:
                        break
            stmt.statements = new_stmts
            return stmt

        elif isinstance(stmt, IfStmt):
            stmt.condition = self._optimize_expr(stmt.condition)
            stmt.then_branch = self._optimize_stmt(stmt.then_branch)
            if stmt.else_branch:
                stmt.else_branch = self._optimize_stmt(stmt.else_branch)

            if isinstance(stmt.condition, NumberExpr):
                if stmt.condition.value != 0.0:
                    return stmt.then_branch
                else:
                    return stmt.else_branch
            return stmt

        elif isinstance(stmt, WhileStmt):
            stmt.condition = self._optimize_expr(stmt.condition)
            stmt.body = self._optimize_stmt(stmt.body)

            if isinstance(stmt.condition, NumberExpr) and stmt.condition.value == 0.0:
                return None 
            return stmt

        elif isinstance(stmt, FunctionStmt):
            new_stmts = []
            for child in stmt.body:
                opt = self._optimize_stmt(child)
                if opt:
                    is_return = isinstance(opt, ReturnStmt)
                    new_stmts.append(opt)
                    if is_return:
                        break
            stmt.body = new_stmts
            return stmt

        elif isinstance(stmt, PrintStmt):
            stmt.expr = self._optimize_expr(stmt.expr)
            return stmt
        return stmt

    def _optimize_expr(self, expr: Expr) -> Expr:
        if isinstance(expr, BinaryExpr):
            if isinstance(expr.left, BinaryExpr) and expr.left.op in (TokenType.PLUS, TokenType.MINUS, TokenType.SLASH, TokenType.STAR):
                expr.left = self._optimize_expr(expr.left)
            if isinstance(expr.right, BinaryExpr) and expr.right.op in (TokenType.PLUS, TokenType.MINUS, TokenType.SLASH, TokenType.STAR):
                expr.right = self._optimize_expr(expr.right)
            if expr.op == TokenType.PLUS:
                if isinstance(expr.left, StringExpr) and isinstance(expr.right, StringExpr):
                    return StringExpr(value=expr.left.value + expr.right.value)
                elif isinstance(expr.left, NumberExpr) and isinstance(expr.right, NumberExpr):
                    return NumberExpr(value=expr.right.value + expr.left.value)
            elif expr.op == TokenType.MINUS:
                if isinstance(expr.left, NumberExpr) and isinstance(expr.right, NumberExpr):
                    return NumberExpr(value=expr.left.value - expr.right.value)
            elif expr.op == TokenType.SLASH:
                if isinstance(expr.left, NumberExpr) and isinstance(expr.right, NumberExpr):
                    return NumberExpr(value=expr.left.value / expr.right.value)
            elif expr.op == TokenType.STAR:
                if isinstance(expr.left, NumberExpr) and isinstance(expr.right, NumberExpr):
                    return NumberExpr(value=expr.left.value * expr.right.value)
        elif isinstance(expr, ArrayExpr):
            expr.elements = [self._optimize_expr(el) for el in expr.elements]
        elif isinstance(expr, IndexExpr):
            expr.array = self._optimize_expr(expr.array)
            expr.index = self._optimize_expr(expr.index)
        elif isinstance(expr, IndexAssignExpr):
            expr.array = self._optimize_expr(expr.array)
            expr.index = self._optimize_expr(expr.index)
            expr.value = self._optimize_expr(expr.value)
            
        return expr