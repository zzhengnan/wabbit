from .model import *

INDENTATION = ' ' * 4
EXPLICIT_TYPE = True
MATH_OP_SIGNS = {
    Add: '+',
    Sub: '-',
    Mul: '*',
    Div: '/',
}
RELATION_SIGNS = {
    Lt: '<',
    Gt: '>',
    Eq: '==',
}


def format_program(program: Program) -> str:
    # Format an entire program
    return format_statements(program.statements, level=0)


def format_statements(stmts: Statements, level: int) -> str:
    # Format a list of statements
    return '\n'.join(format_statement(stmt, level) for stmt in stmts)


def format_statement(stmt: Statement, level: int) -> str:
    indentation = INDENTATION * level
    if isinstance(stmt, Print):
        return f'{indentation}print {format_expression(stmt.value)};'
    elif isinstance(stmt, Variable):
        return f'{indentation}var {format_expression(stmt.name)} = {format_expression(stmt.value)};'
    elif isinstance(stmt, Declaration):
        if EXPLICIT_TYPE:
            if isinstance(stmt, GlobalVar):
                return f'{indentation}global {stmt.name.identifier};'
            elif isinstance(stmt, LocalVar):
                return f'{indentation}local {stmt.name.identifier};'
            else:
                f'{indentation}var {format_expression(stmt.name)};'
        return f'{indentation}var {format_expression(stmt.name)};'
    elif isinstance(stmt, Assignment):
        return f'{indentation}{format_expression(stmt.name)} = {format_expression(stmt.value)};'
    elif isinstance(stmt, If):
        code = f'{indentation}if {format_relation(stmt.test)} {{\n'
        code += f'{format_statements(stmt.consequence, level + 1)}\n'
        code += indentation + '} else {\n'
        code += f'{format_statements(stmt.alternative, level + 1)}\n'
        code += indentation + '}'
        return code
    elif isinstance(stmt, While):
        code = f'{indentation}while {format_relation(stmt.test)} {{\n'
        code += f'{format_statements(stmt.statements, level + 1)}\n'
        code += indentation + '}'
        return code
    elif isinstance(stmt, Func):
        if EXPLICIT_TYPE:
            code = f'func {stmt.name.identifier}({stmt.param.identifier}) {{\n'
        else:
            code = f'func {format_expression(stmt.name)}({format_expression(stmt.param)}) {{\n'
        code += f'{indentation}{format_statements(stmt.body, level + 1)}\n'
        code += f'{indentation}}}'
        return code
    elif isinstance(stmt, Return):
        return f'{indentation}return {format_expression(stmt.value)};'
    else:
        raise RuntimeError(f"Can't format {stmt}")


def format_expression(expr: Expression) -> str:
    if isinstance(expr, Name):
        if EXPLICIT_TYPE:
            if isinstance(expr, GlobalName):
                return f'global[{expr.identifier}]'
            elif isinstance(expr, LocalName):
                return f'local[{expr.identifier}]'
            else:
                return expr.identifier
        return expr.identifier
    elif isinstance(expr, Number):
        return str(expr.value)
    elif isinstance(expr, MathOp):
        sign = MATH_OP_SIGNS[type(expr)]
        return f'{format_expression(expr.left)} {sign} {format_expression(expr.right)}'
    elif isinstance(expr, Call):
        # return f'{format_expression(expr.name)}({format_expression(expr.arg)})'
        return f'{expr.name.identifier}({format_expression(expr.arg)})'
    else:
        raise RuntimeError(f"Can't format {expr}")


def format_relation(relation: Relation) -> str:
    sign = RELATION_SIGNS[type(relation)]
    return (
        f'{format_expression(relation.left)} {sign} {format_expression(relation.right)}'
    )
