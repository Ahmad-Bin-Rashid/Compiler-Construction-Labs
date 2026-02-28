"""
Tokenizer module for the Expression Evaluator.
Breaks an expression string into a list of tokens.
"""


class TokenType:
    """Enumeration of all supported token types."""
    NUMBER = "NUMBER"
    IDENTIFIER = "IDENTIFIER"
    PLUS = "PLUS"
    MINUS = "MINUS"
    MULTIPLY = "MULTIPLY"
    DIVIDE = "DIVIDE"
    LPAREN = "LPAREN"      # (
    RPAREN = "RPAREN"      # )
    LBRACE = "LBRACE"      # {
    RBRACE = "RBRACE"      # }
    LBRACKET = "LBRACKET"  # [
    RBRACKET = "RBRACKET"  # ]
    EMPTY_BRACKET = "EMPTY_BRACKET"  # []
    EMPTY_BRACE = "EMPTY_BRACE"      # {}
    EOF = "EOF"


class Token:
    """Represents a single token with its type and value."""

    def __init__(self, token_type, value):
        self.type = token_type
        self.value = value

    def __repr__(self):
        return f"Token({self.type}, {self.value!r})"

    def __str__(self):
        return str(self.value)


# Mapping from single characters to token types
OPERATOR_MAP = {
    '+': TokenType.PLUS,
    '-': TokenType.MINUS,
    '*': TokenType.MULTIPLY,
    '/': TokenType.DIVIDE,
    '(': TokenType.LPAREN,
    ')': TokenType.RPAREN,
    '{': TokenType.LBRACE,
    '}': TokenType.RBRACE,
}


def tokenize(expression):
    """
    Break an expression string into a list of Token objects.

    Supports:
      - Integer and floating-point numbers
      - Identifiers (variable names starting with a-z/A-Z)
      - Arithmetic operators: + - * /
      - Grouping symbols: () {} []
      - Empty bracket/brace pairs used as grouping markers in postfix/prefix: [] {}

    Returns:
        list[Token]: The list of tokens (terminated by an EOF token).
    """
    tokens = []
    i = 0
    length = len(expression)

    while i < length:
        ch = expression[i]

        # Skip whitespace
        if ch.isspace():
            i += 1
            continue

        # Numbers (integers and floats)
        if ch.isdigit() or (ch == '.' and i + 1 < length and expression[i + 1].isdigit()):
            start = i
            has_dot = False
            while i < length and (expression[i].isdigit() or expression[i] == '.'):
                if expression[i] == '.':
                    if has_dot:
                        break  # second dot → stop
                    has_dot = True
                i += 1
            num_str = expression[start:i]
            value = float(num_str) if '.' in num_str else int(num_str)
            tokens.append(Token(TokenType.NUMBER, value))
            continue

        # Identifiers
        if ch.isalpha() or ch == '_':
            start = i
            while i < length and (expression[i].isalnum() or expression[i] == '_'):
                i += 1
            tokens.append(Token(TokenType.IDENTIFIER, expression[start:i]))
            continue

        # Square brackets – detect empty pair [] first
        if ch == '[':
            if i + 1 < length and expression[i + 1] == ']':
                tokens.append(Token(TokenType.EMPTY_BRACKET, "[]"))
                i += 2
                continue
            tokens.append(Token(TokenType.LBRACKET, '['))
            i += 1
            continue

        if ch == ']':
            tokens.append(Token(TokenType.RBRACKET, ']'))
            i += 1
            continue

        # Curly braces – detect empty pair {} first
        if ch == '{':
            if i + 1 < length and expression[i + 1] == '}':
                tokens.append(Token(TokenType.EMPTY_BRACE, "{}"))
                i += 2
                continue
            tokens.append(Token(TokenType.LBRACE, '{'))
            i += 1
            continue

        # Operators and other single-character tokens
        if ch in OPERATOR_MAP:
            tokens.append(Token(OPERATOR_MAP[ch], ch))
            i += 1
            continue

        # Unknown character – skip with a warning (could also raise)
        print(f"Warning: unexpected character '{ch}' at position {i}")
        i += 1

    tokens.append(Token(TokenType.EOF, None))
    return tokens


def print_tokens(tokens):
    """Print each token for debugging / display purposes."""
    for tok in tokens:
        if tok.type != TokenType.EOF:
            print(f"  Token({tok.type}, {tok.value!r})")
