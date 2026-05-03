# Shared token definitions and utilities

from enum import Enum, auto
from dataclasses import dataclass
from typing import Optional, Any


#  Token Types
class TokenType(Enum):
    # Literals
    INTEGER    = auto()
    FLOAT      = auto()
    STRING     = auto()

    # Identifier / Keywords
    IDENTIFIER = auto()
    KEYWORD    = auto()

    # Operators
    PLUS       = auto()
    MINUS      = auto()
    STAR       = auto()
    SLASH      = auto()
    ASSIGN     = auto()
    EQ         = auto()   # ==
    NEQ        = auto()   # !=
    LT         = auto()   # <
    GT         = auto()   # >
    LTE        = auto()   # <=
    GTE        = auto()   # >=

    # Delimiters
    LPAREN     = auto()
    RPAREN     = auto()
    LBRACE     = auto()
    RBRACE     = auto()
    SEMICOLON  = auto()
    COMMA      = auto()
    LBRACKET   = auto()
    RBRACKET   = auto()

    # Comments
    COMMENT    = auto()

    # Special
    EOF        = auto()
    ERROR      = auto()


#  Reserved Keywords
KEYWORDS = {
    'if', 'else', 'while', 'for', 'int', 'float',
    'string', 'return', 'void', 'true', 'false',
    'and', 'or', 'not', 'do', 'begin', 'end',
    'var', 'program', 'procedure', 'function',
    'array', 'of', 'integer', 'real', 'boolean',
    'then', 'mod', 'div',
}


#  Token dataclass
@dataclass
class Token:
    type:    TokenType
    lexeme:  str
    value:   Any
    line:    int
    column:  int

    def display_value(self) -> str:
        if self.type in (TokenType.INTEGER, TokenType.FLOAT):
            return str(self.value)
        if self.type == TokenType.STRING:
            return self.lexeme
        return '-'

    def type_name(self) -> str:
        return self.type.name


#  Pretty-print a token stream
def print_token_stream(tokens: list, approach_name: str):
    errors = [t for t in tokens if t.type == TokenType.ERROR]
    visible = [t for t in tokens if t.type not in (TokenType.EOF,)]

    W_LINE, W_TYPE, W_LEX, W_VAL = 6, 18, 30, 16
    total_width = W_LINE + W_TYPE + W_LEX + W_VAL + 9

    border   = '─' * total_width
    thick    = '═' * total_width

    print(f'\n{"═"*total_width}')
    print(f'  APPROACH: {approach_name}')
    print(f'{"═"*total_width}')
    print(f'  Token Stream:')
    print(border)

    header = (f"{'Line':>{W_LINE}} │ {'Token Type':<{W_TYPE}} │ "
              f"{'Lexeme':<{W_LEX}} │ {'Value':>{W_VAL}}")
    print(header)
    print(border)

    for tok in visible:
        lexeme_display = tok.lexeme
        if len(lexeme_display) > W_LEX - 2:
            lexeme_display = lexeme_display[:W_LEX - 5] + '...'
        row = (f"  {tok.line:>{W_LINE-2}} │ {tok.type_name():<{W_TYPE}} │ "
               f"{lexeme_display:<{W_LEX}} │ {tok.display_value():>{W_VAL}}")
        print(row)

    print(border)
    print(f'  Total Tokens : {len(visible)}')
    print(f'  Lexical Errors: {len(errors)}')
    print(thick)
