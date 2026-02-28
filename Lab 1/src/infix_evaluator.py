"""
Infix expression evaluator with step-by-step output.

Uses a recursive-descent parser that respects operator precedence:
  - Lowest precedence: + -
  - Higher precedence: * /
  - Highest precedence: unary -, parentheses/braces/brackets

Grouping symbols (), {}, and [] are treated equivalently.
"""

from tokenizer import Token, TokenType, tokenize


class InfixEvaluator:
    """Evaluate an infix expression with step-by-step tracing."""

    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0
        self.steps = []  # list of step description strings

    # ---- Helpers ----

    def current(self):
        """Return the current token."""
        return self.tokens[self.pos]

    def eat(self, expected_type=None):
        """Consume the current token, optionally checking its type."""
        tok = self.current()
        if expected_type and tok.type != expected_type:
            raise SyntaxError(
                f"Expected {expected_type} but got {tok.type} ('{tok.value}')"
            )
        self.pos += 1
        return tok

    def _log(self, msg):
        self.steps.append(msg)

    # ---- Recursive-descent grammar ----

    def parse(self):
        """Entry point – parse and evaluate the full expression."""
        result = self._expr()
        return result

    def _expr(self):
        """Handle + and - (lowest precedence)."""
        left = self._term()

        while self.current().type in (TokenType.PLUS, TokenType.MINUS):
            op_tok = self.eat()
            self._log(f"Token: {op_tok.value}")
            right = self._term()

            if op_tok.type == TokenType.PLUS:
                result = left + right
                self._log(f"Applied operator: +")
                self._log(f"Left: {_fmt(left)} Right: {_fmt(right)} Result: {_fmt(result)}")
            else:
                result = left - right
                self._log(f"Applied operator: -")
                self._log(f"Left: {_fmt(left)} Right: {_fmt(right)} Result: {_fmt(result)}")
            left = result
        return left

    def _term(self):
        """Handle * and / (higher precedence)."""
        left = self._factor()

        while self.current().type in (TokenType.MULTIPLY, TokenType.DIVIDE):
            op_tok = self.eat()
            self._log(f"Token: {op_tok.value}")
            right = self._factor()

            if op_tok.type == TokenType.MULTIPLY:
                result = left * right
                self._log(f"Applied operator: *")
                self._log(f"Left: {_fmt(left)} Right: {_fmt(right)} Result: {_fmt(result)}")
            else:
                if right == 0:
                    raise ZeroDivisionError("Division by zero")
                result = left / right
                self._log(f"Applied operator: /")
                self._log(f"Left: {_fmt(left)} Right: {_fmt(right)} Result: {_fmt(result)}")
            left = result
        return left

    def _factor(self):
        """Handle numbers, identifiers, unary minus, and grouping."""
        tok = self.current()

        # Unary minus
        if tok.type == TokenType.MINUS:
            self.eat()
            self._log(f"Token: -")
            val = self._factor()
            result = -val
            self._log(f"Applied unary operator: -")
            self._log(f"Operand: {_fmt(val)} Result: {_fmt(result)}")
            return result

        # Number
        if tok.type == TokenType.NUMBER:
            self.eat()
            self._log(f"Token: {_fmt(tok.value)}")
            return tok.value

        # Identifier (treated as variable – for now just returns 0 or could be extended)
        if tok.type == TokenType.IDENTIFIER:
            self.eat()
            self._log(f"Token: {tok.value}")
            raise NameError(f"Undefined variable '{tok.value}'")

        # Parentheses grouping
        if tok.type == TokenType.LPAREN:
            self.eat()
            self._log(f"Token: (")
            val = self._expr()
            self.eat(TokenType.RPAREN)
            self._log(f"Token: )")
            return val

        # Curly brace grouping
        if tok.type == TokenType.LBRACE:
            self.eat()
            self._log(f"Token: {{")
            val = self._expr()
            self.eat(TokenType.RBRACE)
            self._log(f"Token: }}")
            return val

        # Square bracket grouping
        if tok.type == TokenType.LBRACKET:
            self.eat()
            self._log(f"Token: [")
            val = self._expr()
            self.eat(TokenType.RBRACKET)
            self._log(f"Token: ]")
            return val

        raise SyntaxError(f"Unexpected token: {tok}")


def _fmt(value):
    """Format a numeric value for display (drop .0 for whole numbers)."""
    if isinstance(value, float) and value == int(value):
        return str(int(value))
    return str(value)


def evaluate_infix(expression):
    """
    Tokenize and evaluate an infix expression.
    Returns (result, steps) where steps is a list of step-description strings.
    """
    tokens = tokenize(expression)
    evaluator = InfixEvaluator(tokens)
    result = evaluator.parse()
    return result, evaluator.steps
