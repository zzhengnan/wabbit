# Wabbit
A Python-based compiler for the [Wabbit](https://dabeaz.com/wabbit.html) programming language, as part of David Beazley's [Write a Compiler](https://dabeaz.com/compiler.html) course.

The compiler will take Wabbit source code, run through a series of "passes" to generate LLVM code, which can then be further compiled using Clang to produce an executable.

## Compiler passes
The following passes are executed in order
1. Tokenizing: Turn Wabbit source code into tokens
1. Parsing: Construct an abstract syntax tree
1. Constant folding: Simplify algebraic calculations involving constants (e.g., `var x = 1 + 2;` gets turned into `var x = 3;`)
1. De-initialization: Separate variable assignment into a distinct declaration step (e.g., `var x = 3;` gets turned into `var x; x = 3;`)
1. Scope resolution: Identify whether a given variable has local or global scope
1. Un-scripting: Move "top-level" logic that's not part of a function into a catch-all function
1. Code generation: Generate LLVM code

## Example
Take the following program for instance.
```
$ cat foo.wb
// World's simplest Wabbit program
var x = 3;
print x;
```

The `wabbit` command will compile the program into LLVM code.
```
$ wabbit foo.wb
Compiled program saved to 'foo.wb.ll'

$ cat foo.wb.ll
@x = global i32 0

define i32 @main(i32 %.1) {
%_ = alloca i32
store i32 %.1, i32* %_
store i32 3, i32* @x
%.2 = load i32, i32* @x
call i32 (i32) @_print_int(i32 %.2)
ret i32 0
}

declare i32 @_print_int(i32 %x)
```

We can then use Clang to compile LLVM into an executable and run it.
```
$ clang foo.wb.ll runtime.c -o foo.out

$ ./foo.out
Out: 3
```

## Dev setup
Run the following command at the root of the repo to set up the dev environment.
```
$ pip install -e .['dev']
$ pre-commit install
```