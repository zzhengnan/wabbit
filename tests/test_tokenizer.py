from wabbit.tokenizer import Token, tokenize


def test_signs():
    source = '+ - * / < =='
    expected = [Token('ADD', '+'), Token('SUB', '-'), Token('MUL', '*'), Token('DIV', '/'), Token('LT', '<'), Token('EQ', '==')]
    assert tokenize(source) == expected


def test_assignment():
    assert tokenize('x = 3;') == [Token('NAME', 'x'), Token('ASSIGN', '='), Token('INTEGER', '3'), Token('SEMI', ';')]


def test_if():
    assert tokenize('if 1 == 2 { } else { }') == [
        Token('IF', 'if'), Token('INTEGER', '1'), Token('EQ', '=='), Token('INTEGER', '2'), Token('LBRACE', '{'), Token('RBRACE', '}'),
        Token('ELSE', 'else'), Token('LBRACE', '{'), Token('RBRACE', '}'),
    ]


def test_while():
    assert tokenize('while 1 == 1 { }') == [Token('WHILE', 'while'), Token('INTEGER', '1'), Token('EQ', '=='), Token('INTEGER', '1'), Token('LBRACE', '{'), Token('RBRACE', '}')]


def test_return():
    assert tokenize('return 3;') == [Token('RETURN', 'return'), Token('INTEGER', '3'), Token('SEMI', ';')]


def test_mixed():
    assert tokenize('print 1; while 1==1 { print 2; }') == [
        Token('PRINT', 'print'), Token('INTEGER', '1'), Token('SEMI', ';'),
        Token('WHILE', 'while'), Token('INTEGER', '1'), Token('EQ', '=='), Token('INTEGER', '1'),
        Token('LBRACE', '{'), Token('PRINT', 'print'), Token('INTEGER', '2'), Token('SEMI', ';'), Token('RBRACE', '}')
    ]
    assert tokenize('print 1;     // A comment\nvar x = 3;') == [
        Token('PRINT', 'print'), Token('INTEGER', '1'), Token('SEMI', ';'),
        Token('VAR', 'var'), Token('NAME', 'x'), Token('ASSIGN', '='), Token('INTEGER', '3'), Token('SEMI', ';')
    ]


def test_print():
    assert tokenize('print 1; print xyz; print (2); print f(xyz);') == [
        Token('PRINT', 'print'), Token('INTEGER', '1'), Token('SEMI', ';'),
        Token('PRINT', 'print'), Token('NAME', 'xyz'), Token('SEMI', ';'),
        Token('PRINT', 'print'), Token('LPAREN', '('), Token('INTEGER', '2'), Token('RPAREN', ')'), Token('SEMI', ';'),
        Token('PRINT', 'print'), Token('NAME', 'f'), Token('LPAREN', '('), Token('NAME', 'xyz'), Token('RPAREN', ')'), Token('SEMI', ';'),
    ]
    assert tokenize('print 1 + xyz;') == [
        Token('PRINT', 'print'), Token('INTEGER', '1'), Token('ADD', '+'), Token('NAME', 'xyz'), Token('SEMI', ';')
    ]


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


def test_declaration():
    assert tokenize('var x;') == [Token('VAR', 'var'), Token('NAME', 'x'), Token('SEMI', ';')]
    assert tokenize('var x int;') == [Token('VAR', 'var'), Token('NAME', 'x'), Token('INTEGER_TYPE', 'int'), Token('SEMI', ';')]
    assert tokenize('var x float;') == [Token('VAR', 'var'), Token('NAME', 'x'), Token('FLOAT_TYPE', 'float'), Token('SEMI', ';')]


def test_func():
    assert tokenize('func foo(x int) int { }') == [
        Token('FUNC', 'func'), Token('NAME', 'foo'),
        Token('LPAREN', '('), Token('NAME', 'x'), Token('INTEGER_TYPE', 'int'), Token('RPAREN', ')'), Token('INTEGER_TYPE', 'int'),
        Token('LBRACE', '{'), Token('RBRACE', '}')
    ]
    assert tokenize('func foo(x float) float { }') == [
        Token('FUNC', 'func'), Token('NAME', 'foo'),
        Token('LPAREN', '('), Token('NAME', 'x'), Token('FLOAT_TYPE', 'float'), Token('RPAREN', ')'), Token('FLOAT_TYPE', 'float'),
        Token('LBRACE', '{'), Token('RBRACE', '}')]
    assert tokenize('func f(a) { }') == [
        Token('FUNC', 'func'), Token('NAME', 'f'), Token('LPAREN', '('), Token('NAME', 'a'), Token('RPAREN', ')'), Token('LBRACE', '{'), Token('RBRACE', '}')
    ]


def test_variable():
    assert tokenize('var x = 45;') == [Token('VAR', 'var'), Token('NAME', 'x'), Token('ASSIGN', '='), Token('INTEGER', '45'), Token('SEMI', ';')]
    assert tokenize('var x = 45.1;') == [Token('VAR', 'var'), Token('NAME', 'x'), Token('ASSIGN', '='), Token('FLOAT', '45.1'), Token('SEMI', ';')]
    assert tokenize('var x = (12 + 45.67);') == [
        Token('VAR', 'var'), Token('NAME', 'x'), Token('ASSIGN', '='),
        Token('LPAREN', '('), Token('INTEGER', '12'), Token('ADD', '+'), Token('FLOAT', '45.67'), Token('RPAREN', ')'), Token('SEMI', ';')
    ]
