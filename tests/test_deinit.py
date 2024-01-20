from wabbit.deinit import *
from wabbit.model import *


def test_script():
    # var x = 10;
    # print 23 * 45 + x;
    prog = Program(
        [
            Variable(Name('x', Type.INTEGER), Integer(10)),
            Print(Add(Mul(Integer(23), Integer(45)), Name('x', Type.INTEGER))),
        ]
    )

    # var x int;
    # x = 10;
    # print 23 * 45 + x;
    expected = Program(
        [
            Declaration(Name('x', Type.INTEGER)),
            Assignment(Name('x', Type.INTEGER), Integer(10)),
            Print(Add(Mul(Integer(23), Integer(45)), Name('x', Type.INTEGER))),
        ]
    )

    assert deinit_program(prog) == expected


def test_control():
    # var n = 0;
    # while n < 10 {
    #     if n == 5 {
    #         var x = 3 * 100;
    #         print x;
    #     } else {
    #         print n;
    #     }
    #     n = 100 + 1;
    # }
    prog = Program(
        [
            Variable(Name('n'), Integer(0)),
            While(
                Lt(Name('n'), Integer(10)),
                [
                    If(
                        Eq(Name('n'), Integer(5)),
                        [
                            Variable(Name('x'), Mul(Integer(3), Integer(100))),
                            Print(Name('x')),
                        ],
                        [Print(Name('n'))],
                    ),
                    Assignment(Name('n'), Add(Integer(100), Integer(1))),
                ],
            ),
        ]
    )

    # var n;
    # n = 0;
    # while n < 10 {
    #     if n == 5 {
    #         var x;
    #         x = 3 * 100;
    #         print x;
    #     } else {
    #         print n;
    #     }
    #     n = 100 + 1;
    # }
    expected = Program(
        [
            Declaration(Name('n')),
            Assignment(Name('n'), Integer(0)),
            While(
                Lt(Name('n'), Integer(10)),
                [
                    If(
                        Eq(Name('n'), Integer(5)),
                        [
                            Declaration(Name('x')),
                            Assignment(Name('x'), Mul(Integer(3), Integer(100))),
                            Print(Name('x')),
                        ],
                        [Print(Name('n'))],
                    ),
                    Assignment(Name('n'), Add(Integer(100), Integer(1))),
                ],
            ),
        ]
    )

    assert deinit_program(prog) == expected


def test_func():
    # func square(x) {
    #     var r = x * x;
    #     return r;
    # }
    # var result = square(4);
    # print result;
    prog = Program(
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

    # func square(x) {
    #     var r;
    #     r = x * x;
    #     return r;
    # }
    # var result;
    # result = square(4);
    # print result;
    expected = Program(
        [
            Func(
                Name('square'),
                Name('x'),
                [
                    Declaration(Name('r')),
                    Assignment(Name('r'), Mul(Name('x'), Name('x'))),
                    Return(Name('r')),
                ],
            ),
            Declaration(Name('result')),
            Assignment(Name('result'), Call(Name('square'), Integer(4))),
            Print(Name('result')),
        ]
    )

    assert deinit_program(prog) == expected
