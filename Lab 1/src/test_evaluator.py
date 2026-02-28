"""
Test suite for the Expression Evaluator.

Run with:
    python test_evaluator.py
"""

import sys
import os

# Ensure src directory is importable
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'src'))

from tokenizer import tokenize, TokenType
from infix_evaluator import evaluate_infix
from postfix_evaluator import evaluate_postfix
from prefix_evaluator import evaluate_prefix


# ------------------------------------------------------------------ #
# Helpers
# ------------------------------------------------------------------ #

passed = 0
failed = 0


def _fmt(value):
    if isinstance(value, float) and value == int(value):
        return int(value)
    return value


def assert_close(actual, expected, label, tol=1e-9):
    """Check that actual ≈ expected within a tolerance."""
    global passed, failed
    actual = _fmt(actual)
    expected = _fmt(expected)
    ok = abs(actual - expected) < tol
    status = "PASS" if ok else "FAIL"
    if not ok:
        failed += 1
        print(f"  [{status}] {label}:  expected {expected}, got {actual}")
    else:
        passed += 1
        print(f"  [{status}] {label}")


# ------------------------------------------------------------------ #
# Tokenizer tests
# ------------------------------------------------------------------ #

def test_tokenizer():
    print("\n=== Tokenizer Tests ===")

    tokens = tokenize("3 + 4")
    types = [t.type for t in tokens]
    assert types == [TokenType.NUMBER, TokenType.PLUS, TokenType.NUMBER, TokenType.EOF], \
        f"Unexpected types: {types}"
    print("  [PASS] Simple addition tokens")
    global passed
    passed += 1

    tokens = tokenize("3.14 * (2 + 1)")
    nums = [t.value for t in tokens if t.type == TokenType.NUMBER]
    assert nums == [3.14, 2, 1], f"Unexpected numbers: {nums}"
    print("  [PASS] Float and parentheses tokens")
    passed += 1

    tokens = tokenize("[] {}")
    types = [t.type for t in tokens if t.type != TokenType.EOF]
    assert types == [TokenType.EMPTY_BRACKET, TokenType.EMPTY_BRACE], \
        f"Unexpected types: {types}"
    print("  [PASS] Empty bracket/brace tokens")
    passed += 1

    tokens = tokenize("[5 - 2]")
    types = [t.type for t in tokens if t.type != TokenType.EOF]
    assert types == [
        TokenType.LBRACKET, TokenType.NUMBER, TokenType.MINUS,
        TokenType.NUMBER, TokenType.RBRACKET
    ], f"Unexpected types: {types}"
    print("  [PASS] Square bracket grouping tokens")
    passed += 1


# ------------------------------------------------------------------ #
# Infix evaluator tests
# ------------------------------------------------------------------ #

def test_infix():
    print("\n=== Infix Evaluator Tests ===")

    # Basic arithmetic
    r, _ = evaluate_infix("2 + 3")
    assert_close(r, 5, "2 + 3")

    r, _ = evaluate_infix("10 - 4")
    assert_close(r, 6, "10 - 4")

    r, _ = evaluate_infix("3 * 7")
    assert_close(r, 21, "3 * 7")

    r, _ = evaluate_infix("20 / 4")
    assert_close(r, 5, "20 / 4")

    # Operator precedence
    r, _ = evaluate_infix("2 + 3 * 4")
    assert_close(r, 14, "2 + 3 * 4 (precedence)")

    r, _ = evaluate_infix("(2 + 3) * 4")
    assert_close(r, 20, "(2 + 3) * 4")

    # Example from assignment
    r, _ = evaluate_infix("3 * (2 + 4) - [5 - 2]")
    assert_close(r, 15, "3 * (2 + 4) - [5 - 2]")

    # Curly braces
    r, _ = evaluate_infix("{2 + 3} * 4")
    assert_close(r, 20, "{2 + 3} * 4")

    # Nested grouping
    r, _ = evaluate_infix("((2 + 3) * (4 - 1))")
    assert_close(r, 15, "((2 + 3) * (4 - 1))")

    # Floating point
    r, _ = evaluate_infix("3.5 + 1.5")
    assert_close(r, 5.0, "3.5 + 1.5")

    # Division producing float
    r, _ = evaluate_infix("7 / 2")
    assert_close(r, 3.5, "7 / 2")

    # Complex expression
    r, _ = evaluate_infix("(10 + 2) * 3 - {8 / 4}")
    assert_close(r, 34, "(10 + 2) * 3 - {8 / 4}")


# ------------------------------------------------------------------ #
# Postfix evaluator tests
# ------------------------------------------------------------------ #

def test_postfix():
    print("\n=== Postfix Evaluator Tests ===")

    r, _ = evaluate_postfix("2 3 +")
    assert_close(r, 5, "2 3 +")

    r, _ = evaluate_postfix("5 3 -")
    assert_close(r, 2, "5 3 -")

    r, _ = evaluate_postfix("4 5 *")
    assert_close(r, 20, "4 5 *")

    r, _ = evaluate_postfix("20 4 /")
    assert_close(r, 5, "20 4 /")

    # Example from assignment
    r, _ = evaluate_postfix("2 3 4 + * 5 2 - [] -")
    assert_close(r, 11, "2 3 4 + * 5 2 - [] -")

    # More complex
    r, _ = evaluate_postfix("3 4 + 2 * 1 +")
    assert_close(r, 15, "3 4 + 2 * 1 +")

    # Float
    r, _ = evaluate_postfix("3.5 1.5 +")
    assert_close(r, 5.0, "3.5 1.5 +")


# ------------------------------------------------------------------ #
# Prefix evaluator tests
# ------------------------------------------------------------------ #

def test_prefix():
    print("\n=== Prefix Evaluator Tests ===")

    r, _ = evaluate_prefix("+ 2 3")
    assert_close(r, 5, "+ 2 3")

    r, _ = evaluate_prefix("- 5 3")
    assert_close(r, 2, "- 5 3")

    r, _ = evaluate_prefix("* 4 5")
    assert_close(r, 20, "* 4 5")

    r, _ = evaluate_prefix("/ 20 4")
    assert_close(r, 5, "/ 20 4")

    # Example from assignment
    r, _ = evaluate_prefix("- * 3 + 2 4 - [] 5 2")
    assert_close(r, 15, "- * 3 + 2 4 - [] 5 2")

    # Nested
    r, _ = evaluate_prefix("+ * 2 3 * 4 5")
    assert_close(r, 26, "+ * 2 3 * 4 5")

    # Float
    r, _ = evaluate_prefix("+ 3.5 1.5")
    assert_close(r, 5.0, "+ 3.5 1.5")


# ------------------------------------------------------------------ #
# Step-by-step output tests (verify steps are generated)
# ------------------------------------------------------------------ #

def test_steps():
    print("\n=== Step-by-Step Output Tests ===")
    global passed

    _, steps = evaluate_infix("3 * (2 + 4) - [5 - 2]")
    assert len(steps) > 0, "Expected infix steps"
    print(f"  [PASS] Infix generates {len(steps)} steps")
    passed += 1

    _, steps = evaluate_postfix("2 3 4 + * 5 2 - [] -")
    assert len(steps) > 0, "Expected postfix steps"
    print(f"  [PASS] Postfix generates {len(steps)} steps")
    passed += 1

    _, steps = evaluate_prefix("- * 3 + 2 4 - [] 5 2")
    assert len(steps) > 0, "Expected prefix steps"
    print(f"  [PASS] Prefix generates {len(steps)} steps")
    passed += 1


# ------------------------------------------------------------------ #
# Run all tests
# ------------------------------------------------------------------ #

if __name__ == "__main__":
    test_tokenizer()
    test_infix()
    test_postfix()
    test_prefix()
    test_steps()

    print("\n" + "=" * 50)
    total = passed + failed
    print(f"Results: {passed}/{total} passed, {failed} failed")
    if failed:
        sys.exit(1)
    else:
        print("All tests passed!")
        sys.exit(0)
