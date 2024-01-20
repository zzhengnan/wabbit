from typing import Self
from .model import *


class Scope:
    def __init__(self, parent_scope=None):
        self.parent_scope = parent_scope
        self.var_names = set()  # Known variables in current scope

    def __repr__(self):
        return f'Scope(var_names={self.var_names}, parent_scope={self.parent_scope})'

    def declare(self, var_name: str) -> None:
        """Declare new variable in current scope."""
        if var_name in self.var_names:
            raise RuntimeError(f"{var_name!r} is already defined")
        self.var_names.add(var_name)

    def lookup(self, var_name: str) -> str:
        """Look up scope of given variable."""
        if var_name in self.var_names:
            return 'local' if self.parent_scope else 'global'
        elif self.parent_scope:
            return self.parent_scope.lookup(var_name)
        else:
            return 'undefined'

    def new_scope(self) -> Self:
        """Make new scope nested inside current scope."""
        return Scope(parent_scope=self)


def resolve_scopes(prog : Program) -> Program:
    global_scope = Scope()
    return Program(resolve_statements(prog.statements, global_scope))


def resolve_statements(stmts: Statements, scope: Scope) -> Statements:
    return [resolve_statement(stmt, scope) for stmt in stmts]


def resolve_statement(stmt: Statement, scope: Scope) -> Statement:
    if isinstance(stmt, Print):
        return Print(resolve_expression(stmt.value, scope))
    elif isinstance(stmt, Variable):
        return stmt
    elif isinstance(stmt, Declaration):
        var_name = stmt.name.identifier
        scope.declare(var_name)
        where = scope.lookup(var_name)
        return LocalVar(stmt.name) if where == 'local' else GlobalVar(stmt.name)
    elif isinstance(stmt, Assignment):
        return Assignment(
            resolve_expression(stmt.name, scope),
            resolve_expression(stmt.value, scope),
        )
    elif isinstance(stmt, If):
        return If(
            # stmt.test,
            resolve_relation(stmt.test, scope),
            resolve_statements(stmt.consequence, scope.new_scope()),
            resolve_statements(stmt.alternative, scope.new_scope()),
        )
    elif isinstance(stmt, While):
        return While(
            # stmt.test,
            resolve_relation(stmt.test, scope),
            resolve_statements(stmt.statements, scope.new_scope()),
        )
    elif isinstance(stmt, Func):
        func_scope = scope.new_scope()
        func_scope.var_names.add(stmt.param.identifier)  # Add func param to local scope
        return Func(
            stmt.name,
            resolve_expression(stmt.param, func_scope),
            resolve_statements(stmt.body, func_scope)
        )
    elif isinstance(stmt, Return):
        return Return(resolve_expression(stmt.value, scope))
    else:
        raise RuntimeError(f"Can't resolve {stmt}")


def resolve_expression(expr: Expression, scope: Scope) -> Expression:
    if isinstance(expr, Name):
        var_name = expr.identifier
        where = scope.lookup(var_name)
        return LocalName(var_name) if where == 'local' else GlobalName(var_name)
    elif isinstance(expr, Number):
        return expr
    elif isinstance(expr, MathOp):
        return type(expr)(resolve_expression(expr.left, scope), resolve_expression(expr.right, scope))
    elif isinstance(expr, Call):
        return Call(
            resolve_expression(expr.name, scope),
            resolve_expression(expr.arg, scope),
        )
    else:
        raise RuntimeError(f"Can't resolve {expr}")


def resolve_relation(relation: Relation, scope: Scope) -> Relation:
    return type(relation)(
        left=resolve_expression(relation.left, scope),
        right=resolve_expression(relation.right, scope),
    )