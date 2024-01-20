import pytest

from wabbit.model import *
from wabbit.tokenizer import *
from wabbit.parse import *


def parse_statement(source: str):
    p = Parser(tokenize(source))
    return p.parse_statement()


def test_declaration():
    assert parse_statement('var x int;') == Declaration(Name('x', Type.INTEGER))
    assert parse_statement('var x float;') == Declaration(Name('x', Type.FLOAT))

    with pytest.raises(TypeError, match='Variable declaration missing type annotation'):
        parse_statement('var x;')


def test_func():
    assert parse_statement('func f(a int) int { }') == Func(Name('f'), Name('a', Type.INTEGER), [], Type.INTEGER)
    assert parse_statement('func f(a float) float { }') == Func(Name('f'), Name('a', Type.FLOAT), [], Type.FLOAT)
    assert parse_statement('func f(a float) int { }') == Func(Name('f'), Name('a', Type.FLOAT), [], Type.INTEGER)
    assert parse_statement('func f(a float) int { return a; }') == Func(Name('f'), Name('a', Type.FLOAT), [Return(Name('a'))], Type.INTEGER)

    with pytest.raises(TypeError, match='Function parameter missing type annotation'):
        parse_statement('func f(a) int { }')

    with pytest.raises(TypeError, match='Function return value missing type annotation'):
        parse_statement('func f(a int) { }')


def test_variable():
    source = 'var x = 3;'
    p = Parser(tokenize(source))
    assert p.parse_statement() == Variable(Name('x', Type.INTEGER), Integer(3))


def test_assignment():
    source = 'x = 3;'
    p = Parser(tokenize(source))
    assert p.parse_statement() == Assignment(Name('x', Type.INTEGER), Integer(3))


def test_if():
    source = 'if 1 == 2 { } else { }'
    p = Parser(tokenize(source))
    assert p.parse_statement() == If(Eq(Integer(1), Integer(2)), [], [])


def test_while():
    source = 'while 1 == 1 { }'
    p = Parser(tokenize(source))
    assert p.parse_statement() == While(Eq(Integer(1), Integer(1)), [])


def test_return():
    source = 'return 3;'
    p = Parser(tokenize(source))
    assert p.parse_statement() == Return(Integer(3))


def test_statements():
    source = 'print 1; while 1==1 { print 2; }'
    p = Parser(tokenize(source))
    assert p.parse_statements() == [
        Print(Integer(1)),
        While(Eq(Integer(1), Integer(1)), [ Print(Integer(2)) ])
    ]

def test_term():
    source = 'print 1; print xyz; print (2); print f(xyz);'
    p = Parser(tokenize(source))
    assert p.parse_statements() == [
        Print(Integer(1)),
        Print(Name('xyz')),
        Print(Integer(2)),
        Print(Call(Name('f'), Name('xyz')))
    ]

def test_expr():
    source = 'print 1 + xyz;'
    p = Parser(tokenize(source))
    assert p.parse_statements() == [
        Print(Add(Integer(1), Name('xyz')))
    ]


class TestMathExpression:
    def test1(self):
        source = '1 + 2'
        actual = Parser(tokenize(source)).parse_expression()
        expected = Add(Integer(1), Integer(2))
        assert actual == expected

    def test2(self):
        source = '1 - 2'
        actual = Parser(tokenize(source)).parse_expression()
        expected = Sub(Integer(1), Integer(2))
        assert actual == expected

    def test3(self):
        source = '1 * 2'
        actual = Parser(tokenize(source)).parse_expression()
        expected = Mul(Integer(1), Integer(2))
        assert actual == expected

    def test4(self):
        source = '1 / 2'
        actual = Parser(tokenize(source)).parse_expression()
        expected = Div(Integer(1), Integer(2))
        assert actual == expected

    def test5(self):
        source = '(1 - 2) * (3 / 4)'
        actual = Parser(tokenize(source)).parse_expression()
        expected = Mul(
            Sub(Integer(1), Integer(2)),
            Div(Integer(3), Integer(4)),
        )
        assert actual == expected


class TestRelation:
    def test_lt(self):
        source = '1 < 2'
        actual = Parser(tokenize(source)).parse_relation()
        expected = Lt(Integer(1), Integer(2))
        assert actual == expected

    def test_gt(self):
        source = '1 > 2'
        actual = Parser(tokenize(source)).parse_relation()
        expected = Gt(Integer(1), Integer(2))
        assert actual == expected

    def test_eq(self):
        source = '1 == 2'
        actual = Parser(tokenize(source)).parse_relation()
        expected = Eq(Integer(1), Integer(2))
        assert actual == expected