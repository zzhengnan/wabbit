from wabbit.foldconstants import *
from wabbit.model import *


class TestFoldExpressionAdd:
    def test_integer_literals(self):
        # 3 + 4 -> 7
        expr = Add(Integer(3), Integer(4))
        expected = Integer(7)
        assert fold_expression(expr) == expected

    def test_with_name(self):
        # 3 + x -> 3 + x
        expr = Add(Integer(3), Name('x'))
        expected = Add(Integer(3), Name('x'))
        assert fold_expression(expr) == expected

    def test_nested_integer_literals(self):
        # (3 + 4) + (1 + 2) -> 10
        expr = Add(Add(Integer(3), Integer(4)), Add(Integer(1), Integer(2)))
        expected = Integer(10)
        assert fold_expression(expr) == expected

    def test_nested_with_name(self):
        # (3 + 4) + x -> 7 + x
        expr = Add(Add(Integer(3), Integer(4)), Name('x'))
        expected = Add(Integer(7), Name('x'))
        assert fold_expression(expr) == expected


class TestFoldExpressionMul:
    def test_integer_literals(self):
        # 3 * 4 -> 12
        expr = Mul(Integer(3), Integer(4))
        expected = Integer(12)
        assert fold_expression(expr) == expected

    def test_with_name(self):
        # 3 * x -> 3 * x
        expr = Mul(Integer(3), Name('x'))
        expected = Mul(Integer(3), Name('x'))
        assert fold_expression(expr) == expected

    def test_nested_integer_literals(self):
        # (3 * 4) * (1 * 2) -> 24
        expr = Mul(Mul(Integer(3), Integer(4)), Mul(Integer(1), Integer(2)))
        expected = Integer(24)
        assert fold_expression(expr) == expected

    def test_nested_with_name(self):
        # (3 * 4) * x -> 12 * x
        expr = Mul(Mul(Integer(3), Integer(4)), Name('x'))
        expected = Mul(Integer(12), Name('x'))
        assert fold_expression(expr) == expected


class TestFoldExpressionMixedAddAndMul:
    def test_integer_literals(self):
        # 3 * 4 + 5 -> 17
        expr = Add(Mul(Integer(3), Integer(4)), Integer(5))
        expected = Integer(17)
        assert fold_expression(expr) == expected

    def test_with_name(self):
        # x + 3 * 4 -> x + 12
        expr = Add(Name('x'), Mul(Integer(3), Integer(4)))
        expected = Add(Name('x'), Integer(12))
        assert fold_expression(expr) == expected

    def test_nested_integer_literals(self):
        # (3 * 4) + (1 + 2) -> 15
        expr = Add(Mul(Integer(3), Integer(4)), Add(Integer(1), Integer(2)))
        expected = Integer(15)
        assert fold_expression(expr) == expected

    def test_nested_with_name(self):
        # (3 * 4) + x * (1 + 2) -> 12 + x * 3
        expr = Add(
            Mul(Integer(3), Integer(4)), Mul(Name('x'), Add(Integer(1), Integer(2)))
        )
        expected = Add(Integer(12), Mul(Name('x'), Integer(3)))
        assert fold_expression(expr) == expected


class TestFoldExpressionMixedAll:
    def test_nested_integer_literals(self):
        # (4 / 3) * (1 + 2) -> 3
        expr = Mul(Div(Integer(4), Integer(3)), Add(Integer(1), Integer(2)))
        expected = Integer(3)
        assert fold_expression(expr) == expected

    def test_nested_with_name(self):
        # (3 + 4) / x -> 7 / x
        expr = Div(Add(Integer(3), Integer(4)), Name('x'))
        expected = Div(Integer(7), Name('x'))
        assert fold_expression(expr) == expected


class TestFoldExpressionFuncCall:
    def test_integer_literals(self):
        # foo(3 * 4 + 5) -> foo(17)
        expr = Call(Name('foo'), Add(Mul(Integer(3), Integer(4)), Integer(5)))
        expected = Call(Name('foo'), Integer(17))
        assert fold_expression(expr) == expected

    def test_nested_integer_literals(self):
        # foo((3 * 4) + (1 + 2)) -> foo(15)
        expr = Call(
            Name('foo'), Add(Mul(Integer(3), Integer(4)), Add(Integer(1), Integer(2)))
        )
        expected = Call(Name('foo'), Integer(15))
        assert fold_expression(expr) == expected


class TestFoldExpressionOthers:
    def test_Name(self):
        expr = Name('x')
        expected = Name('x')
        assert fold_expression(expr) == expected

    def test_Integer(self):
        expr = Integer(3)
        expected = Integer(3)
        assert fold_expression(expr) == expected


class TestFoldRelation:
    def test_fold_right_side(self):
        # 3 == 1 + 2 -> 3 == 3
        relation = Eq(Integer(3), Add(Integer(1), Integer(2)))
        expected = Eq(Integer(3), Integer(3))
        assert fold_relation(relation) == expected

    def test_fold_left_side(self):
        # 1 + 2 < 3 -> 3 < 3
        relation = Lt(Add(Integer(1), Integer(2)), Integer(3))
        expected = Lt(Integer(3), Integer(3))
        assert fold_relation(relation) == expected

    def test_fold_both_sides(self):
        # (1 + 2) * 3 == 2 + (1 * 6) -> 9 == 8
        relation = Eq(
            Mul(Add(Integer(1), Integer(2)), Integer(3)),
            Add(Integer(2), Mul(Integer(1), Integer(6))),
        )
        expected = Eq(Integer(9), Integer(8))
        assert fold_relation(relation) == expected


class TestFoldStatement:
    def test_If(self):
        # if n == 5 {
        #     var x = 3 * 100 + 1;
        #     print x;
        # } else {
        #     print x + 1 + (3 * 4);
        # }
        stmt = If(
            Eq(Name('n'), Integer(5)),
            [
                Variable(Name('x'), Add(Mul(Integer(3), Integer(100)), Integer(1))),
                Print(Name('x')),
            ],
            [Print(Add(Name('x'), Add(Integer(1), Mul(Integer(3), Integer(4)))))],
        )

        # if n == 5 {
        #     var x = 301;
        #     print x;
        # } else {
        #     print x + 13;
        # }
        expected = If(
            Eq(Name('n'), Integer(5)),
            [Variable(Name('x'), Integer(301)), Print(Name('x'))],
            [Print(Add(Name('x'), Integer(13)))],
        )

        assert fold_statement(stmt) == expected

    def test_While(self):
        # while n < 10 {
        #     var x = 3 * 100 + 1;
        #     print x + 1 + (3 * 4);
        # }
        stmt = While(
            Lt(Name('n'), Integer(10)),
            [
                Variable(Name('x'), Add(Mul(Integer(3), Integer(100)), Integer(1))),
                Print(Add(Name('x'), Add(Integer(1), Mul(Integer(3), Integer(4))))),
            ],
        )

        # while n < 10 {
        #     var x = 301;
        #     print x + 13;
        # }
        expected = While(
            Lt(Name('n'), Integer(10)),
            [
                Variable(Name('x'), Integer(301)),
                Print(Add(Name('x'), Integer(13))),
            ],
        )

        assert fold_statement(stmt) == expected

    def test_Func(self):
        # func square(x) {
        #     var r = x * (3 + 1);
        #     var p = 12 + 3;
        #     return 3 * 4 + 1;
        # }
        stmt = Func(
            Name('square'),
            Name('x'),
            [
                Variable(Name('r'), Mul(Name('x'), Add(Integer(3), Integer(1)))),
                Variable(Name('p'), Add(Integer(12), Integer(3))),
                Return((Add(Mul(Integer(3), Integer(4)), Integer(1)))),
            ],
        )

        # func square(x) {
        #     var r = x * 4;
        #     var p = 15;
        #     return 13;
        # }
        expected = Func(
            Name('square'),
            Name('x'),
            [
                Variable(Name('r'), Mul(Name('x'), Integer(4))),
                Variable(Name('p'), Integer(15)),
                Return(Integer(13)),
            ],
        )

        assert fold_statement(stmt) == expected

    def test_Variable(self):
        # var x = 3 + 1;
        stmt = Variable(Name('x'), Add(Integer(3), Integer(1)))
        expected = Variable(Name('x'), Integer(4))
        assert fold_statement(stmt) == expected

    def test_Declaration(self):
        # var x;
        stmt = Declaration(Name('x'))
        expected = Declaration(Name('x'))
        assert fold_statement(stmt) == expected


def test_script():
    # var x = 10;
    # x = x + 1;
    # print 23 * 45 + x;
    prog = Program(
        [
            Variable(Name('x'), Integer(10)),
            Assignment(Name('x'), Add(Name('x'), Integer(1))),
            Print(Add(Mul(Integer(23), Integer(45)), Name('x'))),
        ]
    )

    # var x = 10;
    # x = x + 1;
    # print 1035 + x;
    expected = Program(
        [
            Variable(Name('x'), Integer(10)),
            Assignment(Name('x'), Add(Name('x'), Integer(1))),
            Print(Add(Integer(1035), Name('x'))),
        ]
    )

    assert fold_program(prog) == expected


def test_control():
    # var n = 0;
    # while n < 10 {
    #     if n == 5 {
    #         var x = 3 * 100 + 1;
    #         print x;
    #     } else {
    #         print 3 + 2;
    #     }
    #     n = 100 + (2 * 8);
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
                            Variable(
                                Name('x'),
                                Add(Mul(Integer(3), Integer(100)), Integer(1)),
                            ),
                            Print(Name('x')),
                        ],
                        [Print(Add(Integer(3), Integer(2)))],
                    ),
                    Assignment(
                        Name('n'), Add(Integer(100), Mul(Integer(2), Integer(8)))
                    ),
                ],
            ),
        ]
    )

    # var n = 0;
    # while n < 10 {
    #     if n == 5 {
    #         var x = 301;
    #         print x;
    #     } else {
    #         print 5;
    #     }
    #     n = 116;
    # }
    expected = Program(
        [
            Variable(Name('n'), Integer(0)),
            While(
                Lt(Name('n'), Integer(10)),
                [
                    If(
                        Eq(Name('n'), Integer(5)),
                        [Variable(Name('x'), Integer(301)), Print(Name('x'))],
                        [Print(Integer(5))],
                    ),
                    Assignment(Name('n'), Integer(116)),
                ],
            ),
        ]
    )

    assert fold_program(prog) == expected


def test_func():
    # func square(x) {
    #     var r = x * x;
    #     var p = 3 * 4;
    #     return r;
    # }
    # var result = square(4) + (3 * 4);
    # print 100 + 200;
    prog = Program(
        [
            Func(
                Name('square'),
                Name('x'),
                [
                    Variable(Name('r'), Mul(Name('x'), Name('x'))),
                    Variable(Name('p'), Mul(Integer(3), Integer(4))),
                    Return(Name('r')),
                ],
            ),
            Variable(
                Name('result'),
                Add(Call(Name('square'), Integer(4)), Mul(Integer(3), Integer(4))),
            ),
            Print(Add(Integer(100), Integer(200))),
        ]
    )

    # func square(x) {
    #     var r = x * x;
    #     var p = 12;
    #     return r;
    # }
    # var result = square(4) + 12;
    # print 300;
    expected = Program(
        [
            Func(
                Name('square'),
                Name('x'),
                [
                    Variable(Name('r'), Mul(Name('x'), Name('x'))),
                    Variable(Name('p'), Integer(12)),
                    Return(Name('r')),
                ],
            ),
            Variable(
                Name('result'), Add(Call(Name('square'), Integer(4)), Integer(12))
            ),
            Print(Integer(300)),
        ]
    )

    assert fold_program(prog) == expected
