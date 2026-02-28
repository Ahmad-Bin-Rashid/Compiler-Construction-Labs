"""
Prefix (Polish Notation) expression evaluator with step-by-step output.

Algorithm:
  - Scan tokens from RIGHT to LEFT.
  - Push numbers onto a stack.
  - When an operator is encountered, pop two operands (note: order is
    preserved because we scan right-to-left), apply the operator,
    and push the result back.
  - [] and {} tokens act as no-op grouping markers.

Display:
  - Tokens are displayed in their original left-to-right order so the
    step-by-step output reads naturally.
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


def evaluate_prefix(expression):
    """
    Tokenize and evaluate a prefix expression.

    Returns (result, steps) where steps is a list of step-description strings.
    """
    tokens = tokenize(expression)
    # Remove the trailing EOF token
    tokens = [t for t in tokens if t.type != TokenType.EOF]

    steps = []
    stack = []

    # Display all tokens left-to-right first
    for tok in tokens:
        steps.append(f"Token: {tok.value}")

    # Evaluate right-to-left
    for tok in reversed(tokens):
        # Numbers – push
        if tok.type == TokenType.NUMBER:
            stack.append(tok.value)
            continue

        # Empty brackets / braces – grouping markers, skip
        if tok.type in (TokenType.EMPTY_BRACKET, TokenType.EMPTY_BRACE):
            continue

        # Operators
        if tok.type in (TokenType.PLUS, TokenType.MINUS,
                        TokenType.MULTIPLY, TokenType.DIVIDE):
            if len(stack) < 2:
                raise SyntaxError(
                    f"Not enough operands for operator '{tok.value}'"
                )

            left = stack.pop()
            right = stack.pop()
            result = _apply_op(tok.value, left, right)

            steps.append(f"Applied operator: {tok.value}")
            steps.append(
                f"Left: {_fmt(left)} Right: {_fmt(right)} Result: {_fmt(result)}"
            )
            stack.append(result)
            continue

    if len(stack) != 1:
        raise SyntaxError(
            f"Invalid prefix expression – stack has {len(stack)} values left"
        )

    return stack[0], steps
