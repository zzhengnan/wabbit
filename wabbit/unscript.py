from .model import *


def unscript_toplevel(prog: Program) -> Program:
    stmts = []
    main_body = []
    for stmt in prog.statements:
        if isinstance(stmt, GlobalVar | Func):
            stmts.append(stmt)
        else:
            main_body.append(stmt)
    main_func = Func(Name('main'), Name('_'), main_body)
    stmts.append(main_func)
    return Program(stmts)