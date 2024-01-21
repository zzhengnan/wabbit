import argparse

from wabbit.deinit import *
from wabbit.foldconstants import *
from wabbit.format import *
from wabbit.llvm import *
from wabbit.model import *
from wabbit.parse import *
from wabbit.resolve import *
from wabbit.tokenizer import *
from wabbit.unscript import *


def cli() -> argparse.Namespace:
    """Command line interface."""
    parser = argparse.ArgumentParser(allow_abbrev=False)
    parser.add_argument('FILENAME')
    parser.add_argument(
        '--tokenize',
        action='store_const',
        const=True,
        default=False,
    )
    parser.add_argument(
        '--parse',
        action='store_const',
        const=True,
        default=False,
    )
    parser.add_argument(
        '--fold',
        action='store_const',
        const=True,
        default=False,
    )
    parser.add_argument(
        '--deinit',
        action='store_const',
        const=True,
        default=False,
    )
    parser.add_argument(
        '--resolve',
        action='store_const',
        const=True,
        default=False,
    )
    parser.add_argument(
        '--unscript',
        action='store_const',
        const=True,
        default=False,
    )
    parser.add_argument(
        '--llvm',
        action='store_const',
        const=True,
        default=False,
    )
    return parser.parse_args()


def compile(
    fname: str,
    show_tokenize: bool = False,
    show_parse: bool = True,
    show_foldconstant: bool = False,
    show_deinit: bool = False,
    show_resolve: bool = False,
    show_unscript: bool = True,
    show_llvm: bool = True,
) -> tuple[Program, str]:
    with open(fname) as f:
        source = f.read()
    tokens = tokenize(source)
    if show_tokenize:
        print(tokens)
        return

    prog = parse_tokens(tokens)
    if show_parse:
        print(format_program(prog))
        return

    prog = fold_program(prog)
    if show_foldconstant:
        print(format_program(prog))
        return

    prog = deinit_program(prog)
    if show_deinit:
        print(format_program(prog))
        return

    prog = resolve_scopes(prog)
    if show_resolve:
        print(format_program(prog))
        return

    prog = unscript_toplevel(prog)
    if show_unscript:
        print(format_program(prog))
        return

    prog_ll = generate_llvm(prog)
    if show_llvm:
        print(prog_ll)
        return

    out_name = f'{fname}.ll'
    with open(out_name, 'w') as f:
        f.write(prog_ll)
    print(f'Compiled program saved to {out_name!r}')
    return prog, prog_ll


def main() -> None:
    args = cli()
    compile(
        args.FILENAME,
        args.tokenize,
        args.parse,
        args.fold,
        args.deinit,
        args.resolve,
        args.unscript,
        args.llvm,
    )


if __name__ == '__main__':
    main()
