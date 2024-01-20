from dataclasses import dataclass
from enum import Enum


class Type(Enum):
    INTEGER = 1
    FLOAT = 2
    UNSPECIFIED = 3


# `Expression`s represent values
class Expression: pass

# `Statement`s represent actions
class Statement: pass

Statements = list[Statement]


# `Relation`s are used in if/while tests
class Relation: pass


# Expressions
@dataclass
class Name(Expression):
    identifier: str
    type: Type = Type.UNSPECIFIED

class GlobalName(Name): pass
class LocalName(Name): pass


@dataclass
class Integer(Expression):
    value: int


@dataclass
class Float(Expression):
    value: float

Number = Integer | Float


@dataclass
class Add(Expression):
    left: Expression
    right: Expression


@dataclass
class Mul(Expression):
    left: Expression
    right: Expression


@dataclass
class Sub(Expression):
    left: Expression
    right: Expression


@dataclass
class Div(Expression):
    left: Expression
    right: Expression


MathOp = Add | Sub | Mul | Div


# Statements
@dataclass
class Print(Statement):
    value: Expression


@dataclass
class Variable(Statement):
    # Declare a variable for the first time and assign a value
    # E.g., var x = 3;
    name: Name
    value: Expression


@dataclass
class Declaration(Statement):
    # Declare a variable for the first time without assigning a value
    # E.g., var x;
    name: Name

class GlobalVar(Declaration): pass
class LocalVar(Declaration): pass


@dataclass
class Assignment(Statement):
    # Assign new value to existing variable
    # E.g., x = 4;
    name: Name
    value: Expression


@dataclass
class If(Statement):
    test: Relation
    consequence: Statements
    alternative: Statements


@dataclass
class While(Statement):
    test: Relation
    statements: Statements


@dataclass
class Func(Statement):
    name: Name
    param: Name
    body: Statements
    return_type: Type = Type.UNSPECIFIED


@dataclass
class Return(Statement):
    value: Expression


@dataclass
class Call(Expression):
    name: Name
    arg: Expression


# Relations
@dataclass
class Eq(Relation):
    # left == right
    left: Expression
    right: Expression


@dataclass
class Lt(Relation):
    # left < right
    left: Expression
    right: Expression


@dataclass
class Gt(Relation):
    # left > right
    left: Expression
    right: Expression


@dataclass
class Program:
    statements: Statements