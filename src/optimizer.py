from ast_nodes import *

class DeadCodeEliminator:
    def optimize(self, statements: list[Stmt]) -> list[Stmt]:
        optimized =[]
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
            new_stmts =[]
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
                return None  # Цикл никогда не выполнится
            return stmt

        elif isinstance(stmt, FunctionStmt):
            new_stmts =[]
            for child in stmt.body:
                opt = self._optimize_stmt(child)
                if opt:
                    is_return = isinstance(opt, ReturnStmt)
                    new_stmts.append(opt)
                    if is_return:
                        break
            stmt.body = new_stmts
            return stmt

        return stmt

    def _optimize_expr(self, expr: Expr) -> Expr:
        # Для простоты возвращаем как есть.
        # Сюда можно добавить Constant Folding (например 2+2 -> 4)
        return expr
