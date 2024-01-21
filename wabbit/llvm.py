from wabbit.model import *

_needs_print = False

# Generate a unique name like ".1", ".2", ".3", etc.
_n = 0


def gensym() -> str:
    global _n
    _n += 1
    return f'.{_n}'


LLVM_MATH_INSTRUCTIONS = {
    Add: 'add',
    Sub: 'sub',
    Mul: 'mul',
    Div: 'sdiv',
}
LLVM_COMPARISON_INSTRUCTIONS = {
    Eq: 'eq',
    Lt: 'slt',
    Gt: 'sgt',
}


def generate_llvm(prog: Program) -> str:
    code = '\n'.join(generate_statements(prog.statements))
    if _needs_print:
        code += '\n\ndeclare i32 @_print_int(i32 %x)'
    return code


def generate_statements(stmts: Statements) -> list[str]:
    return [generate_statement(stmt) for stmt in stmts]


def generate_statement(stmt: Statement) -> str:
    if isinstance(stmt, Print):
        # print val -> call i32 (i32) @_print_int(i32 {val})
        global _needs_print
        _needs_print = True
        value_instr, value_var = generate_expression(stmt.value)
        return value_instr + f'call i32 (i32) @_print_int(i32 {value_var})\n'
    elif isinstance(stmt, Declaration):
        name = stmt.name.identifier
        if isinstance(stmt, GlobalVar):
            # global name -> @name = global i32 0
            return f'@{name} = global i32 0'
        elif isinstance(stmt, LocalVar):
            # local name -> %name = alloca i32
            return f'%{name} = alloca i32'
        else:
            raise RuntimeError(f"Can't generate {stmt}")
    elif isinstance(stmt, Assignment):
        name = stmt.name.identifier
        value_instr, value_var = generate_expression(stmt.value)
        if isinstance(stmt.name, GlobalName):
            return value_instr + f'store i32 {value_var}, i32* @{name}'
        elif isinstance(stmt.name, LocalName):
            return value_instr + f'store i32 {value_var}, i32* %{name}'
        else:
            raise RuntimeError(f"Can't generate {stmt}")
    elif isinstance(stmt, If):
        L_consequence = gensym()
        L_alternative = gensym()
        L_out = gensym()
        code, test_var = generate_relation(stmt.test)
        code += f'br i1 {test_var}, label %{L_consequence}, label %{L_alternative}\n'
        code += f'\n{L_consequence}:\n'
        code += '\n'.join(generate_statements(stmt.consequence))
        code += f'br label %{L_out}\n'
        code += f'\n{L_alternative}:\n'
        code += '\n'.join(generate_statements(stmt.alternative))
        code += f'br label %{L_out}\n'
        # L_out has no content so subsequent statements after while loop can execute
        code += f'\n{L_out}:\n'
        return code
    elif isinstance(stmt, While):
        L_test = gensym()
        L_body = gensym()
        L_out = gensym()
        code = f'br label %{L_test}\n'
        test_instr, test_var = generate_relation(stmt.test)
        code += f'\n{L_test}:\n'
        code += test_instr
        code += f'br i1 {test_var}, label %{L_body}, label %{L_out}\n'
        code += f'\n{L_body}:\n'
        code += '\n'.join(generate_statements(stmt.statements)) + '\n'
        code += f'br label %{L_test}\n'
        # L_out has no content so subsequent statements after while loop can execute
        code += f'\n{L_out}:'
        return code
    elif isinstance(stmt, Func):
        # func fname(arg) {body} ->
        # define i32 @fname(i32 %.0) {
        #     %arg = alloca i32
        #     store i32 %.0, i32* %arg
        #     {body}
        #     ret i32 0
        # }
        func_name = stmt.name.identifier
        param_name = stmt.param.identifier
        param_name_signature = gensym()
        code = f'\ndefine i32 @{func_name}(i32 %{param_name_signature}) {{\n'
        code += f'%{param_name} = alloca i32\n'
        code += f'store i32 %{param_name_signature}, i32* %{param_name}\n'
        code += '\n'.join(generate_statements(stmt.body))
        # Functions must return something
        code += 'ret i32 0\n'
        code += '}'
        return code
    elif isinstance(stmt, Return):
        # return val; -> ret i32 {val}
        value_instr, value_var = generate_expression(stmt.value)
        return value_instr + f'ret i32 {value_var}\n'
    else:
        raise RuntimeError(f"Can't generate {stmt}")


def generate_expression(expr: Expression) -> tuple[str, str]:
    if isinstance(expr, Name):
        name = expr.identifier
        var_name = gensym()
        if isinstance(expr, GlobalName):
            # global[name] -> %{gensym} = load i32, i32* @name
            return f'%{var_name} = load i32, i32* @{name}\n', f'%{var_name}'
        elif isinstance(expr, LocalName):
            # local[name] -> %{gensym} = load i32, i32* %name
            return f'%{var_name} = load i32, i32* %{name}\n', f'%{var_name}'
        else:
            raise RuntimeError(f"Can't generate {expr}")
    elif isinstance(expr, Number):
        # return str(expr.value), str(expr.value)
        return '', str(expr.value)
    elif isinstance(expr, MathOp):
        left_instr, left_var = generate_expression(expr.left)
        right_instr, right_var = generate_expression(expr.right)
        final_var = gensym()
        code = left_instr + right_instr
        math_instr = LLVM_MATH_INSTRUCTIONS[type(expr)]
        code += f'%{final_var} = {math_instr} i32 {left_var}, {right_var}\n'
        return code, f'%{final_var}'
    elif isinstance(expr, Call):
        # fname(arg) -> %{gensym} = call i32 (i32) @fname(i32 {arg})
        fname = expr.name.identifier
        arg_instr, arg_var = generate_expression(expr.arg)
        return_var = gensym()
        return (
            arg_instr + f'%{return_var} = call i32 (i32) @{fname}(i32 {arg_var})\n',
            f'%{return_var}',
        )
    else:
        raise RuntimeError(f"Can't generate {expr}")


def generate_relation(relation: Relation) -> str:
    left_instr, left_var = generate_expression(relation.left)
    right_instr, right_var = generate_expression(relation.right)
    final_var = gensym()
    code = left_instr + right_instr
    comparison_sign = LLVM_COMPARISON_INSTRUCTIONS[type(relation)]
    return (
        code + f'%{final_var} = icmp {comparison_sign} i32 {left_var}, {right_var}\n',
        f'%{final_var}',
    )
