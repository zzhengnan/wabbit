from wabbit.format import *
from wabbit.model import *


def test_script():
    program = Program(
        [
            Variable(Name('x'), Integer(10)),
            Assignment(Name('x'), Add(Name('x'), Integer(1))),
            Print(Sub(Div(Integer(23), Integer(45)), Name('x'))),
        ]
    )
    expected = """var x = 10;
x = x + 1;
print 23 / 45 - x;"""
    assert format_program(program) == expected


def test_control():
    program = Program(
        [
            Variable(Name('n'), Integer(0)),
            While(
                Lt(Name('n'), Integer(10)),
                [
                    If(
                        Eq(Name('n'), Integer(5)),
                        [
                            Variable(Name('x'), Mul(Name('n'), Integer(100))),
                            Variable(Name('y'), Div(Name('n'), Integer(100))),
                            Print(Name('x')),
                        ],
                        [Print(Name('n'))],
                    ),
                    Assignment(Name('n'), Add(Name('n'), Integer(1))),
                    Assignment(Name('m'), Sub(Integer(1), Name('m'))),
                ],
            ),
        ]
    )
    expected = """var n = 0;
while n < 10 {
    if n == 5 {
        var x = n * 100;
        var y = n / 100;
        print x;
    } else {
        print n;
    }
    n = n + 1;
    m = 1 - m;
}"""
    assert format_program(program) == expected


def test_function():
    expected = """func square(x) {
    var r = x * x;
    return r;
}
var result = square(4);
print result;"""
    program = Program(
        [
            Func(
                Name('square'),
                Name('x'),
                [
                    Variable(Name('r'), Mul(Name('x'), Name('x'))),
                    Return(Name('r')),
                ],
            ),
            Variable(Name('result'), Call(Name('square'), Integer(4))),
            Print(Name('result')),
        ]
    )
    assert format_program(program) == expected


class TestRelation:
    def test_lt(self):
        relation = Lt(Name('x'), Integer(3))
        expected = 'x < 3'
        assert format_relation(relation) == expected

    def test_gt(self):
        relation = Gt(Name('x'), Integer(3))
        expected = 'x > 3'
        assert format_relation(relation) == expected

    def test_eq(self):
        relation = Eq(Name('x'), Integer(3))
        expected = 'x == 3'
        assert format_relation(relation) == expected
