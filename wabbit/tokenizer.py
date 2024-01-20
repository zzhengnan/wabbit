from dataclasses import dataclass

SINGLE_CHAR_TOKENS = {
    '+': 'ADD',
    '*': 'MUL',
    '-': 'SUB',
    '/': 'DIV',
    '<': 'LT',
    '>': 'GT',
    '=': 'ASSIGN',
    ';': 'SEMI',
    '(': 'LPAREN',
    ')': 'RPAREN',
    '{': 'LBRACE',
    '}': 'RBRACE',
}
MULTI_CHAR_TOKENS = {
    'var': 'VAR',
    'print': 'PRINT',
    'if': 'IF',
    'else': 'ELSE',
    'while': 'WHILE',
    'func': 'FUNC',
    'return': 'RETURN',
    'int': 'INTEGER_TYPE',
    'float': 'FLOAT_TYPE',
}


@dataclass
class Token:
    toktype: str
    tokvalue: str


Tokens = list[Token]


def reset_curr_run(curr_run: str, tokens: Tokens) -> None:
    if curr_run is not None:
        if curr_run.isnumeric():
            toktype = 'INTEGER'
        elif '.' in curr_run:
            toktype = 'FLOAT'
        else:
            toktype = 'NAME'
        token = Token(toktype, curr_run)
        tokens.append(token)
    return None


def verbose(text: str) -> Tokens:
    curr_run = None
    i = 0
    tokens = []
    while i < len(text):
        curr_char = text[i]
        if curr_char in {' ', '\t', '\n'}:
            toktype = 'WHITESPACE'
        elif curr_char == '/':
            if text[i : i + 2] == '//':
                j = i + 2
                while j < len(text):
                    if text[j] == '\n':
                        break
                    j += 1
                token = Token('COMMENT', text[i : j + 1])
                tokens.append(token)
                i = j + 1
                continue
            else:
                # Deal with division
                toktype = 'DIV'
        elif curr_char in SINGLE_CHAR_TOKENS:
            # Special case: = vs. ==, < vs. <=, etc.
            if curr_char == '=' and text[i + 1] == '=':
                i += 2
                curr_run = reset_curr_run(curr_run, tokens)
                tokens.append(Token('EQ', '=='))
                continue
            toktype = SINGLE_CHAR_TOKENS[curr_char]
        elif curr_char == '.':
            if curr_run is not None and curr_run.isnumeric():
                curr_run += curr_char
            else:
                raise SyntaxError("Invalid syntax with '.'; it must follow a number")
            i += 1
            continue
        elif curr_char.isdigit():
            if curr_run is not None:
                curr_run += curr_char
            else:
                curr_run = curr_char
            i += 1
            continue
        elif curr_char.isalpha():
            if curr_run is not None:
                if curr_run.isnumeric():
                    raise SyntaxError(
                        f"Can't have letter {curr_char!r} follow number immediately"
                    )
                curr_run += curr_char
            else:
                curr_run = curr_char
            i += 1
            continue
        else:
            raise SyntaxError(f'Unrecognized {curr_char!r} at position {i}')
        i += 1

        curr_run = reset_curr_run(curr_run, tokens)
        token = Token(toktype, curr_char)
        tokens.append(token)

    reset_curr_run(curr_run, tokens)
    return tokens


def remove_whitespace(tokens: Tokens) -> Tokens:
    return [token for token in tokens if token.toktype not in {'WHITESPACE', 'COMMENT'}]


def identify_keywords(tokens: Tokens) -> Tokens:
    new_tokens = []
    for token in tokens:
        if token.tokvalue in MULTI_CHAR_TOKENS:
            toktype = MULTI_CHAR_TOKENS[token.tokvalue]
            new_token = Token(toktype, token.tokvalue)
            new_tokens.append(new_token)
        else:
            new_tokens.append(token)
    return new_tokens


def tokenize(text: str) -> list[Token]:
    tokens = verbose(text)
    tokens = remove_whitespace(tokens)
    tokens = identify_keywords(tokens)
    return tokens
