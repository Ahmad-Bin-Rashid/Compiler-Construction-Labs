"""
Postfix (Reverse Polish Notation) expression evaluator with step-by-step output.

Algorithm:
  - Scan tokens left to right.
  - Push numbers onto a stack.
  - When an operator is encountered, pop two operands, apply the operator,
    and push the result back.
  - [] and {} tokens act as no-op grouping markers (ignored during evaluation
    but displayed as tokens).
"""

from tokenizer import Token, TokenType, tokenize


def _fmt(value):
    """Format a numeric value for display (drop .0 for whole numbers)."""
    if isinstance(value, float) and value == int(value):
        return str(int(value))
    return str(value)


def _apply_op(op_char, left, right):
    """Apply a binary arithmetic operator and return the result."""
    if op_char == '+':
        return left + right
    elif op_char == '-':
        return left - right
    elif op_char == '*':
        return left * right
    elif op_char == '/':
        if right == 0:
            raise ZeroDivisionError("Division by zero")
        return left / right
    else:
        raise SyntaxError(f"Unknown operator: {op_char}")


def evaluate_postfix(expression):
    """
    Tokenize and evaluate a postfix expression.

    Returns (result, steps) where steps is a list of step-description strings.
    """
    tokens = tokenize(expression)
    stack = []
    steps = []

    for tok in tokens:
        if tok.type == TokenType.EOF:
            break

        # Numbers – push onto stack
        if tok.type == TokenType.NUMBER:
            steps.append(f"Token: {_fmt(tok.value)}")
            stack.append(tok.value)
            continue

        # Empty brackets / braces – display but act as grouping markers (no-op)
        if tok.type in (TokenType.EMPTY_BRACKET, TokenType.EMPTY_BRACE):
            steps.append(f"Token: {tok.value}")
            continue

        # Operators
        if tok.type in (TokenType.PLUS, TokenType.MINUS,
                        TokenType.MULTIPLY, TokenType.DIVIDE):
            steps.append(f"Token: {tok.value}")

            if len(stack) < 2:
                raise SyntaxError(
                    f"Not enough operands for operator '{tok.value}'"
                )

            right = stack.pop()
            left = stack.pop()
            result = _apply_op(tok.value, left, right)

            op_name = {'+': '+', '-': '-', '*': '*', '/': '/'}[tok.value]
            steps.append(f"Applied operator: {op_name}")
            steps.append(
                f"Left: {_fmt(left)} Right: {_fmt(right)} Result: {_fmt(result)}"
            )

            stack.append(result)
            continue

        # Brackets used as grouping in infix-style sub-expressions inside
        # a predominantly postfix expression are not expected, but we
        # gracefully skip them with a note.
        steps.append(f"Token: {tok.value}")

    if len(stack) != 1:
        raise SyntaxError(
            f"Invalid postfix expression – stack has {len(stack)} values left"
        )

    return stack[0], steps
