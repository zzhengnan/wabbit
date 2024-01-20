from wabbit.tokenizer import Token, tokenize


def test1():
    source = '+ * < =='
    expected = [Token('ADD', '+'), Token('MUL', '*'), Token('LT', '<'), Token('EQ', '==')]
    assert tokenize(source) == expected


def test2():
    source = 'var x = 3;'
    expected = [Token('VAR', 'var'), Token('NAME', 'x'), Token('ASSIGN', '='), Token('INTEGER', '3'), Token('SEMI', ';')]
    assert tokenize(source) == expected


def test3():
    source = 'x = 3;'
    expected = [Token('NAME', 'x'), Token('ASSIGN', '='), Token('INTEGER', '3'), Token('SEMI', ';')]
    assert tokenize(source) == expected


def test4():
    source =  'if 1 == 2 { } else { }'
    expected = [
        Token('IF', 'if'), Token('INTEGER', '1'), Token('EQ', '=='), Token('INTEGER', '2'), Token('LBRACE', '{'), Token('RBRACE', '}'),
        Token('ELSE', 'else'), Token('LBRACE', '{'), Token('RBRACE', '}'),
    ]
    assert tokenize(source) == expected


def test5():
    source = 'while 1 == 1 { }'
    expected = [Token('WHILE', 'while'), Token('INTEGER', '1'), Token('EQ', '=='), Token('INTEGER', '1'), Token('LBRACE', '{'), Token('RBRACE', '}')]
    assert tokenize(source) == expected


def test6():
    source = 'func f(a) { }'
    expected = [
        Token('FUNC', 'func'), Token('NAME', 'f'), Token('LPAREN', '('), Token('NAME', 'a'), Token('RPAREN', ')'), Token('LBRACE', '{'), Token('RBRACE', '}')
    ]
    assert tokenize(source) == expected


def test7():
    source = 'return 3;'
    expected = [Token('RETURN', 'return'), Token('INTEGER', '3'), Token('SEMI', ';')]
    assert tokenize(source) == expected


def test8():
    source = '1 == 1'
    expected = [Token('INTEGER', '1'), Token('EQ', '=='), Token('INTEGER', '1')]
    assert tokenize(source) == expected


def test9():
    source = 'print 1; while 1==1 { print 2; }'
    expected = [
        Token('PRINT', 'print'), Token('INTEGER', '1'), Token('SEMI', ';'),
        Token('WHILE', 'while'), Token('INTEGER', '1'), Token('EQ', '=='), Token('INTEGER', '1'),
        Token('LBRACE', '{'), Token('PRINT', 'print'), Token('INTEGER', '2'), Token('SEMI', ';'), Token('RBRACE', '}')
    ]
    assert tokenize(source) == expected


def test10():
    source = 'print 1; print xyz; print (2); print f(xyz);'
    expected = [
        Token('PRINT', 'print'), Token('INTEGER', '1'), Token('SEMI', ';'),
        Token('PRINT', 'print'), Token('NAME', 'xyz'), Token('SEMI', ';'),
        Token('PRINT', 'print'), Token('LPAREN', '('), Token('INTEGER', '2'), Token('RPAREN', ')'), Token('SEMI', ';'),
        Token('PRINT', 'print'), Token('NAME', 'f'), Token('LPAREN', '('), Token('NAME', 'xyz'), Token('RPAREN', ')'), Token('SEMI', ';'),
    ]
    assert tokenize(source) == expected


def test11():
    source = 'print 1 + xyz;'
    expected = [
        Token('PRINT', 'print'), Token('INTEGER', '1'), Token('ADD', '+'), Token('NAME', 'xyz'), Token('SEMI', ';')
    ]
    assert tokenize(source) == expected


def test12():
    source = 'print 1;     // A comment\nvar x = 3;'
    expected = [
        Token('PRINT', 'print'), Token('INTEGER', '1'), Token('SEMI', ';'),
        Token('VAR', 'var'), Token('NAME', 'x'), Token('ASSIGN', '='), Token('INTEGER', '3'), Token('SEMI', ';')
    ]
    assert tokenize(source) == expected


def test13():
    source = '+ - * /'
    expected = [Token('ADD', '+'), Token('SUB', '-'), Token('MUL', '*'), Token('DIV', '/')]
    assert tokenize(source) == expected


def test_number():
    assert tokenize('1') == [Token('INTEGER', '1')]
    assert tokenize('12345') == [Token('INTEGER', '12345')]
    assert tokenize('1.0') == [Token('FLOAT', '1.0')]
    assert tokenize('123.0123') == [Token('FLOAT', '123.0123')]
    assert tokenize('123.') == [Token('FLOAT', '123.')]
    assert tokenize('123 45.67') == [Token('INTEGER', '123'), Token('FLOAT', '45.67')]


def test_comment():
    assert tokenize('//') == []
    assert tokenize('//A comment') == []
    assert tokenize('// A comment') == []
    assert tokenize('///A comment') == []
    assert tokenize('/// A comment') == []
    assert tokenize('x //A comment') == [Token('NAME', 'x')]
    assert tokenize('x//A comment') == [Token('NAME', 'x')]
    assert tokenize('x\n//A comment') == [Token('NAME', 'x')]
    assert tokenize('x + 1  // A comment') == [Token('NAME', 'x'), Token('ADD', '+'), Token('INTEGER', '1')]
    assert tokenize('/ //A comment') == [Token('DIV', '/')]
    assert tokenize('/3//A comment') == [Token('DIV', '/'), Token('INTEGER', '3')]


def test_relation():
        assert tokenize('1 < 2') == [Token('INTEGER', '1'), Token('LT', '<'), Token('INTEGER', '2')]
        assert tokenize('1 > 2') == [Token('INTEGER', '1'), Token('GT', '>'), Token('INTEGER', '2')]
        assert tokenize('1 == 2') == [Token('INTEGER', '1'), Token('EQ', '=='), Token('INTEGER', '2')]


def test18():
    source = 'var x;'
    expected = [Token('VAR', 'var'), Token('NAME', 'x'), Token('SEMI', ';')]
    assert tokenize(source) == expected


class TestTypeAnnotation:
    def test1(self):
        source = 'var x int;'
        expected = [Token('VAR', 'var'), Token('NAME', 'x'), Token('INTEGER_TYPE', 'int'), Token('SEMI', ';')]
        assert tokenize(source) == expected

    def test2(self):
        source = 'func foo(x int) int { }'
        expected = [
            Token('FUNC', 'func'), Token('NAME', 'foo'),
            Token('LPAREN', '('), Token('NAME', 'x'), Token('INTEGER_TYPE', 'int'), Token('RPAREN', ')'), Token('INTEGER_TYPE', 'int'),
            Token('LBRACE', '{'), Token('RBRACE', '}')]
        assert tokenize(source) == expected

    def test3(self):
        source = 'var x float;'
        expected = [Token('VAR', 'var'), Token('NAME', 'x'), Token('FLOAT_TYPE', 'float'), Token('SEMI', ';')]
        assert tokenize(source) == expected

    def test2(self):
        source = 'func foo(x float) float { }'
        expected = [
            Token('FUNC', 'func'), Token('NAME', 'foo'),
            Token('LPAREN', '('), Token('NAME', 'x'), Token('FLOAT_TYPE', 'float'), Token('RPAREN', ')'), Token('FLOAT_TYPE', 'float'),
            Token('LBRACE', '{'), Token('RBRACE', '}')]
        assert tokenize(source) == expected



def test_variable():
    assert tokenize('var x = 45;') == [Token('VAR', 'var'), Token('NAME', 'x'), Token('ASSIGN', '='), Token('INTEGER', '45'), Token('SEMI', ';')]
    assert tokenize('var x = 45.1;') == [Token('VAR', 'var'), Token('NAME', 'x'), Token('ASSIGN', '='), Token('FLOAT', '45.1'), Token('SEMI', ';')]
    assert tokenize('var x = (12 + 45.67);') == [
        Token('VAR', 'var'), Token('NAME', 'x'), Token('ASSIGN', '='),
        Token('LPAREN', '('), Token('INTEGER', '12'), Token('ADD', '+'), Token('FLOAT', '45.67'), Token('RPAREN', ')'), Token('SEMI', ';')
    ]
