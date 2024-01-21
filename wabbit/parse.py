from wabbit.model import *
from wabbit.tokenizer import *

MATH_NODES = {
    'ADD': Add,
    'SUB': Sub,
    'MUL': Mul,
    'DIV': Div,
}
RELATION_NODES = {
    'LT': Lt,
    'GT': Gt,
    'EQ': Eq,
}


class Parser:
    def __init__(self, tokens: list[Token]):
        self.tokens = tokens
        self.n = 0

    def expect(self, expected_type: str) -> Token:
        tok = self.tokens[self.n]
        if tok.toktype == expected_type:
            self.n += 1
            return tok
        else:
            raise SyntaxError(
                f'Expected {expected_type}; got {tok} instead. Current token is {self.current_token}'
            )

    @property
    def current_token(self) -> Token:
        return self.tokens[self.n]

    def peek(self, toktype: str) -> bool:
        # Look at the next token without consuming it
        return self.current_token.toktype == toktype

    def eof(self) -> bool:
        return self.n == len(self.tokens)

    def parse_statement(self):
        if self.peek('PRINT'):
            return self.parse_print()
        elif self.peek('VAR'):
            has_assignment = False
            for i in range(self.n + 1, len(self.tokens)):
                curr_token = self.tokens[i]
                if curr_token.toktype == 'SEMI':
                    break
                else:
                    if curr_token.toktype == 'ASSIGN':
                        has_assignment = True
                        break

            # Distinguish between `Variable` and `Declaration`
            if has_assignment:
                return self.parse_variable()
            return self.parse_declaration()
        elif self.peek('NAME'):
            return self.parse_assignment()
        elif self.peek('IF'):
            return self.parse_if()
        elif self.peek('WHILE'):
            return self.parse_while()
        elif self.peek('FUNC'):
            return self.parse_func()
        elif self.peek('RETURN'):
            return self.parse_return()
        else:
            raise SyntaxError(
                f'Expected a statement; current token is {self.current_token}'
            )

    def parse_statements(self) -> Statements:
        stmts = []
        while True:
            if self.eof() or self.peek('RBRACE'):
                return stmts
            stmt = self.parse_statement()
            stmts.append(stmt)

    def parse_expression(self) -> Expression:
        term1 = self.parse_term()
        for math_tok, math_node in MATH_NODES.items():
            if self.peek(math_tok):
                self.expect(math_tok)
                term2 = self.parse_term()
                return math_node(term1, term2)
        return term1

    def parse_term(self) -> Expression:
        # Parse a number, name, (value), (x + y), or f(arg)
        if self.peek('INTEGER'):
            return self.parse_integer()
        elif self.peek('FLOAT'):
            return self.parse_float()
        elif self.peek('NAME'):
            tok = self.expect('NAME')
            if self.peek('LPAREN'):
                # Func call
                self.expect('LPAREN')
                arg = self.parse_expression()
                self.expect('RPAREN')
                return Call(Name(tok.tokvalue), arg)
            return Name(tok.tokvalue)
        elif self.peek('LPAREN'):
            self.expect('LPAREN')
            expr = self.parse_expression()
            self.expect('RPAREN')
            return expr
        else:
            raise SyntaxError('Expected a term')

    def parse_integer(self) -> Integer:
        tok = self.expect('INTEGER')
        return Integer(int(tok.tokvalue))

    def parse_float(self) -> Float:
        tok = self.expect('FLOAT')
        return Float(float(tok.tokvalue))

    def parse_relation(self) -> Relation:
        # left relation right
        left = self.parse_term()
        for tok, relation in RELATION_NODES.items():
            if self.peek(tok):
                self.expect(tok)
                break
        right = self.parse_term()
        return relation(left, right)

    def parse_print(self) -> Print:
        # print expr;
        self.expect('PRINT')
        value = self.parse_expression()
        self.expect('SEMI')
        return Print(value)

    def parse_variable(self) -> Variable:
        # var x = expr;
        self.expect('VAR')
        name = self.expect('NAME')
        self.expect('ASSIGN')
        value = self.parse_expression()
        if isinstance(value, Integer):
            type = Type.INTEGER
        elif isinstance(value, Float):
            type = Type.FLOAT
        else:
            type = Type.UNSPECIFIED
        self.expect('SEMI')
        return Variable(Name(name.tokvalue, type), value)

    def parse_declaration(self) -> Declaration:
        # var x;
        self.expect('VAR')
        name = self.expect('NAME')
        # TODO: Add float
        if self.peek('INTEGER_TYPE'):
            _ = self.expect('INTEGER_TYPE')
            var_type = Type.INTEGER
        elif self.peek('FLOAT_TYPE'):
            _ = self.expect('FLOAT_TYPE')
            var_type = Type.FLOAT
        elif self.peek('SEMI'):
            raise TypeError('Variable declaration missing type annotation')
        else:
            raise TypeError(f'Unsupported type; current token is {self.current_token}')
        self.expect('SEMI')
        return Declaration(Name(name.tokvalue, var_type))

    def parse_assignment(self) -> Assignment:
        # x = expr;
        name = self.expect('NAME')
        self.expect('ASSIGN')
        value = self.parse_expression()
        if isinstance(value, Integer):
            type = Type.INTEGER
        elif isinstance(value, Float):
            type = Type.FLOAT
        else:
            type = Type.UNSPECIFIED
        self.expect('SEMI')
        return Assignment(Name(name.tokvalue, type), value)

    def parse_if(self) -> If:
        # if test { ... } else { ... }
        self.expect('IF')
        test = self.parse_relation()
        self.expect('LBRACE')
        consequence = self.parse_statements()
        self.expect('RBRACE')
        self.expect('ELSE')
        self.expect('LBRACE')
        alternative = self.parse_statements()
        self.expect('RBRACE')
        return If(test, consequence, alternative)

    def parse_while(self) -> While:
        # while test { ... }
        self.expect('WHILE')
        test = self.parse_relation()
        self.expect('LBRACE')
        body = self.parse_statements()
        self.expect('RBRACE')
        return While(test, body)

    def parse_func(self) -> Func:
        # func fname(param) { ... }
        self.expect('FUNC')
        func_name = self.expect('NAME')

        # Parameter name and type
        self.expect('LPAREN')
        param_name = self.expect('NAME')
        if self.peek('INTEGER_TYPE'):
            _ = self.expect('INTEGER_TYPE')
            param_type = Type.INTEGER
        elif self.peek('FLOAT_TYPE'):
            _ = self.expect('FLOAT_TYPE')
            param_type = Type.FLOAT
        elif self.peek('RPAREN'):
            raise TypeError('Function parameter missing type annotation')
        else:
            raise TypeError(
                f'Unsupported parameter type; current token is {self.current_token}'
            )
        self.expect('RPAREN')

        # Return type
        if self.peek('LBRACE'):
            raise TypeError('Function return value missing type annotation')
        elif self.peek('INTEGER_TYPE'):
            _ = self.expect('INTEGER_TYPE')
            return_type = Type.INTEGER
        elif self.peek('FLOAT_TYPE'):
            _ = self.expect('FLOAT_TYPE')
            return_type = Type.FLOAT
        else:
            raise TypeError(
                f'Unsupported return type; current token is {self.current_token}'
            )

        self.expect('LBRACE')
        body = self.parse_statements()
        self.expect('RBRACE')
        return Func(
            Name(func_name.tokvalue),
            Name(param_name.tokvalue, param_type),
            body,
            return_type,
        )

    def parse_return(self) -> Return:
        # return expr;
        self.expect('RETURN')
        value = self.parse_expression()
        self.expect('SEMI')
        return Return(value)


def parse_tokens(tokens: Tokens) -> Program:
    p = Parser(tokens)
    return Program(p.parse_statements())
