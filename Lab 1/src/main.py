"""
Expression Evaluator – Main Entry Point
========================================
Accepts a mathematical expression from the command line and evaluates it
as an infix, postfix, or prefix expression with step-by-step output.

Usage:
    python main.py "<expression>"
    python main.py --mode infix "<expression>"
    python main.py --mode postfix "<expression>"
    python main.py --mode prefix "<expression>"

If --mode is not specified, the program attempts to auto-detect the notation.
"""

import sys
import os

# Ensure the src directory is on the path so sibling modules can be imported
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from tokenizer import tokenize, TokenType
from infix_evaluator import evaluate_infix
from postfix_evaluator import evaluate_postfix
from prefix_evaluator import evaluate_prefix


def _fmt(value):
    """Format a numeric value for display."""
    if isinstance(value, float) and value == int(value):
        return str(int(value))
    return str(value)


# ------------------------------------------------------------------ #
# Auto-detection heuristic
# ------------------------------------------------------------------ #

def _is_operator_token(tok):
    """Return True if the token is an arithmetic operator."""
    return tok.type in (
        TokenType.PLUS, TokenType.MINUS,
        TokenType.MULTIPLY, TokenType.DIVIDE,
    )


def detect_mode(expression):
    """
    Heuristic to detect whether an expression is infix, postfix, or prefix.

    Rules (applied to tokens with grouping symbols filtered out):
      - If the first meaningful token is an operator → prefix
      - If the last meaningful token (before EOF) is an operator → postfix
      - Otherwise → infix
    """
    tokens = tokenize(expression)
    # Keep only numbers and operators for detection
    meaningful = [
        t for t in tokens
        if t.type in (
            TokenType.NUMBER, TokenType.PLUS, TokenType.MINUS,
            TokenType.MULTIPLY, TokenType.DIVIDE,
        )
    ]
    if not meaningful:
        return "infix"

    # Check for prefix: first token is an operator (and not a unary minus
    # before a number which is common in infix too, so we look for binary ops)
    first = meaningful[0]
    if first.type in (TokenType.MULTIPLY, TokenType.DIVIDE, TokenType.PLUS):
        return "prefix"
    # A leading minus could be unary infix OR prefix.  If the *second*
    # meaningful token is also an operator, lean toward prefix.
    if first.type == TokenType.MINUS and len(meaningful) > 1:
        if _is_operator_token(meaningful[1]):
            return "prefix"

    # Check for postfix: last meaningful token is an operator
    last = meaningful[-1]
    if _is_operator_token(last):
        return "postfix"

    return "infix"


# ------------------------------------------------------------------ #
# Interactive / menu-driven mode
# ------------------------------------------------------------------ #

def interactive_mode():
    """Run the evaluator in an interactive loop with a simple menu."""
    print("=" * 60)
    print("   Expression Evaluator with Step-by-Step Evaluation")
    print("=" * 60)

    while True:
        print("\nSelect evaluation mode:")
        print("  1. Infix   (e.g., 3 * (2 + 4) - [5 - 2])")
        print("  2. Postfix (e.g., 2 3 4 + * 5 2 - [] -)")
        print("  3. Prefix  (e.g., - * 3 + 2 4 - [] 5 2)")
        print("  4. Auto-detect")
        print("  0. Exit")
        choice = input("\nChoice [1/2/3/4/0]: ").strip()

        if choice == '0':
            print("Goodbye!")
            break

        mode_map = {'1': 'infix', '2': 'postfix', '3': 'prefix', '4': 'auto'}
        mode = mode_map.get(choice)
        if mode is None:
            print("Invalid choice. Please try again.")
            continue

        expr = input("Enter expression: ").strip()
        if not expr:
            print("Empty expression. Please try again.")
            continue

        run_evaluation(expr, mode)


# ------------------------------------------------------------------ #
# Core evaluation runner
# ------------------------------------------------------------------ #

def run_evaluation(expression, mode):
    """Evaluate *expression* in the given *mode* and print results."""
    if mode == 'auto':
        mode = detect_mode(expression)
        print(f"\nAuto-detected mode: {mode}")

    print(f'\nExpression: "{expression}"')
    print("-" * 50)

    try:
        if mode == 'infix':
            result, steps = evaluate_infix(expression)
        elif mode == 'postfix':
            result, steps = evaluate_postfix(expression)
        elif mode == 'prefix':
            result, steps = evaluate_prefix(expression)
        else:
            print(f"Unknown mode: {mode}")
            return

        for step in steps:
            print(step)

        print(f"\nResult: {_fmt(result)}")

    except (SyntaxError, ZeroDivisionError, NameError) as exc:
        print(f"Error: {exc}")


# ------------------------------------------------------------------ #
# CLI entry point
# ------------------------------------------------------------------ #

def main():
    """Parse command-line arguments and run the evaluator."""
    args = sys.argv[1:]

    # No arguments → interactive mode
    if not args:
        interactive_mode()
        return

    # Parse optional --mode flag
    mode = 'auto'
    expression = None

    i = 0
    while i < len(args):
        if args[i] in ('--mode', '-m') and i + 1 < len(args):
            mode = args[i + 1].lower()
            i += 2
        else:
            expression = args[i]
            i += 1

    if expression is None:
        print("Usage: python main.py [--mode infix|postfix|prefix|auto] \"<expression>\"")
        sys.exit(1)

    run_evaluation(expression, mode)


if __name__ == "__main__":
    main()
