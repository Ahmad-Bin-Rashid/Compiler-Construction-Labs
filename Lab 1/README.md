# Expression Evaluator with Step-by-Step Evaluation

A Python program that evaluates mathematical expressions in **Infix**, **Postfix**, and **Prefix** notation with detailed step-by-step output.

## Features

- **Tokenizer** – Breaks expression strings into typed tokens (NUMBER, PLUS, MINUS, MULTIPLY, DIVIDE, parentheses, brackets, braces, EOF).
- **Infix evaluation** – Recursive-descent parser respecting operator precedence (`* /` before `+ -`) and grouping with `()`, `{}`, `[]`.
- **Postfix evaluation** – Stack-based left-to-right evaluation (Reverse Polish Notation).
- **Prefix evaluation** – Stack-based right-to-left evaluation (Polish Notation).
- **Step-by-step output** – Every token processed and every operator applied is printed with operands and intermediate results.
- **Auto-detection** – When the mode is not specified, the program heuristically detects the notation.
- **Interactive mode** – Run without arguments for a menu-driven interface.

## Project Structure

```
Lab 1/
├── README.md                  # This file
├── docs/
│   └── Lab1.docx              # Assignment specification
└── src/
    ├── main.py                # Entry point (CLI & interactive)
    ├── tokenizer.py           # Tokenizer – lexical analysis
    ├── infix_evaluator.py     # Infix expression evaluator
    ├── postfix_evaluator.py   # Postfix expression evaluator
    ├── prefix_evaluator.py    # Prefix expression evaluator
    └── test_evaluator.py      # Automated test suite (33 tests)
```

## Prerequisites

- **Python 3.6+** (no external packages required)

## How to Run

### Command-Line Usage

Navigate to the `src/` directory and run:

```bash
# Explicit mode
python main.py --mode infix   "3 * (2 + 4) - [5 - 2]"
python main.py --mode postfix "2 3 4 + * 5 2 - [] -"
python main.py --mode prefix  "- * 3 + 2 4 - [] 5 2"

# Auto-detect mode (omit --mode)
python main.py "3 * (2 + 4) - [5 - 2]"
```

### Interactive Mode

```bash
python main.py
```

This launches a menu where you can choose the evaluation mode and enter expressions interactively.

### Running Tests

```bash
cd src
python test_evaluator.py
```

All 33 tests should pass.

## Implementation Approach

### 1. Tokenizer (`tokenizer.py`)

The tokenizer scans the input string character by character and produces a list of `Token` objects. Each token carries a **type** (e.g., `NUMBER`, `PLUS`, `LPAREN`) and a **value** (e.g., `3.14`, `+`, `(`).

Special handling:
- `[]` as two adjacent characters is emitted as a single `EMPTY_BRACKET` token (used as a grouping marker in postfix/prefix).
- `{}` is similarly treated as `EMPTY_BRACE`.
- Floating-point numbers like `3.14` are recognized as a single `NUMBER` token.

### 2. Infix Evaluator (`infix_evaluator.py`)

Uses a **recursive-descent parser** with three grammar levels:

| Function    | Handles            | Precedence |
|-------------|---------------------|------------|
| `_expr()`   | `+`, `-`            | Lowest     |
| `_term()`   | `*`, `/`            | Higher     |
| `_factor()` | Numbers, `()` `{}` `[]`, unary `-` | Highest |

Each function logs tokens and intermediate results as they are processed.

### 3. Postfix Evaluator (`postfix_evaluator.py`)

Uses a **stack-based algorithm**:
1. Scan tokens left to right.
2. Push numbers onto the stack.
3. On an operator, pop two operands, compute the result, push it back.
4. `[]` and `{}` markers are displayed but do not affect computation.

### 4. Prefix Evaluator (`prefix_evaluator.py`)

Also stack-based, but tokens are processed **right to left**:
1. Reverse the token list.
2. Push numbers onto the stack.
3. On an operator, pop two operands (left first, then right), compute, push result.
4. Tokens are displayed in their original left-to-right order.

## Examples

### Infix

```
Expression: "3 * (2 + 4) - [5 - 2]"
Token: 3
Token: *
Token: (
Token: 2
Token: +
Token: 4
Applied operator: +
Left: 2 Right: 4 Result: 6
Token: )
Applied operator: *
Left: 3 Right: 6 Result: 18
Token: -
Token: [
Token: 5
Token: -
Token: 2
Applied operator: -
Left: 5 Right: 2 Result: 3
Token: ]
Applied operator: -
Left: 18 Right: 3 Result: 15
Result: 15
```

### Postfix

```
Expression: "2 3 4 + * 5 2 - [] -"
Token: 2
Token: 3
Token: 4
Token: +
Applied operator: +
Left: 3 Right: 4 Result: 7
Token: *
Applied operator: *
Left: 2 Right: 7 Result: 14
Token: 5
Token: 2
Token: -
Applied operator: -
Left: 5 Right: 2 Result: 3
Token: []
Token: -
Applied operator: -
Left: 14 Right: 3 Result: 11
Result: 11
```

### Prefix

```
Expression: "- * 3 + 2 4 - [] 5 2"
Token: -
Token: *
Token: 3
Token: +
Token: 2
Token: 4
Token: -
Token: []
Token: 5
Token: 2
Applied operator: -
Left: 5 Right: 2 Result: 3
Applied operator: +
Left: 2 Right: 4 Result: 6
Applied operator: *
Left: 3 Right: 6 Result: 18
Applied operator: -
Left: 18 Right: 3 Result: 15
Result: 15
```

## Supported Operators and Symbols

| Symbol | Description |
|--------|-------------|
| `+`    | Addition |
| `-`    | Subtraction (binary) or negation (unary, infix only) |
| `*`    | Multiplication |
| `/`    | Division |
| `()`   | Grouping (parentheses) |
| `{}`   | Grouping (curly braces) |
| `[]`   | Grouping (square brackets) |

## Constraints

- Input expressions must be valid mathematical expressions.
- Both integers and floating-point numbers are supported.
- Division by zero raises an error with a descriptive message.
