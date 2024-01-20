from operator import add, sub, mul, floordiv
from format import *
from model import *


MATH_OP_OPERATORS = {
    Add: add,
    Sub: sub,
    Mul: mul,
    Div: floordiv
}


def fold_program(prog: Program) -> Program:
    return Program(fold_statements(prog.statements))


def fold_statements(stmts: Statements) -> Statements:
    return [fold_statement(stmt) for stmt in stmts]


def fold_statement(stmt: Statement) -> Statement:
    if isinstance(stmt, Print):
        return Print(fold_expression(stmt.value))
    elif isinstance(stmt, Variable):
        return Variable(stmt.name, fold_expression(stmt.value))
    elif isinstance(stmt, Declaration):
        return stmt
    elif isinstance(stmt, Assignment):
        return Assignment(stmt.name, fold_expression(stmt.value))
    elif isinstance(stmt, If):
        return If(
            fold_relation(stmt.test),
            fold_statements(stmt.consequence),
            fold_statements(stmt.alternative)
        )
    elif isinstance(stmt, While):
        return While(stmt.test, fold_statements(stmt.statements))
    elif isinstance(stmt, Func):
        return Func(stmt.name, stmt.param, fold_statements(stmt.body))
    elif isinstance(stmt, Return):
        return Return(fold_expression(stmt.value))
    else:
        raise RuntimeError(f"Can't fold {stmt}")


def fold_expression(expr: Expression) -> Expression:
    if isinstance(expr, Name):
        return expr
    elif isinstance(expr, Number):
        return expr
    elif isinstance(expr, MathOp):
        operator = MATH_OP_OPERATORS[type(expr)]
        left = fold_expression(expr.left)
        right = fold_expression(expr.right)
        if isinstance(left, Number) and isinstance(right, Number):
            new = type(left)(operator(left.value, right.value))
            return new
        return type(expr)(left, right)
    elif isinstance(expr, Call):
        arg = fold_expression(expr.arg)
        return Call(expr.name, arg)
    else:
        raise RuntimeError(f"Can't fold {expr}")


def fold_relation(relation: Relation) -> Relation:
    return type(relation)(
        left=fold_expression(relation.left),
        right=fold_expression(relation.right),
    )
