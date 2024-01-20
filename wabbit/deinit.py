from format import *
from model import *


def deinit_program(prog : Program) -> Program:
    return Program(deinit_statements(prog.statements))


def deinit_statements(stmts: Statements) -> Statements:
    new_stmts = []
    for stmt in stmts:
        new_stmt = deinit_statement(stmt)
        if isinstance(new_stmt, tuple):
            new_stmts.extend(new_stmt)
        else:
            new_stmts.append(new_stmt)
    return new_stmts


def deinit_statement(stmt: Statement) -> Statements:
    if isinstance(stmt, Variable):
        return (Declaration(stmt.name), Assignment(stmt.name, stmt.value))
    elif isinstance(stmt, If):
        return If(
            stmt.test,
            deinit_statements(stmt.consequence),
            deinit_statements(stmt.alternative),
        )
    elif isinstance(stmt, While):
        return While(
            stmt.test,
            deinit_statements(stmt.statements),
        )
    elif isinstance(stmt, Func):
        return Func(
            stmt.name,
            stmt.param,
            deinit_statements(stmt.body),
        )
    else:
        return stmt
