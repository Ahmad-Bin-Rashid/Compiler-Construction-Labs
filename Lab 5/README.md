# Pascal Subset — Lexical Analyzer

### Compiler Design Lab

---

## Overview

This project implements a lexical analyzer (scanner) for a Pascal-like language using **three approaches** plus a **bonus compressed variant**. The scanner reads a source file, groups characters into lexemes, and produces a token stream of the form `<token-type, attribute-value>`.

Run all approaches at once:

```bash
python main.py program.pascal
```

---

## File Structure

```
.
├── main.py                    # Runner: executes all approaches, compares results
├── tokens.py                  # Shared: TokenType enum, Token dataclass, keywords, printer
├── approach1_state_based.py   # Approach 1: Direct-coded state machine
├── approach2_stateless.py     # Approach 2: Stateless functional dispatch
├── approach3_table_driven.py  # Approach 3: Transition table driven
├── bonus_compressed_table.py  # Bonus:     Compressed sparse table
└── program.pascal             # Sample input source file
```

---

## Token Categories

| Token Type | Pattern                     | Examples                      |
| ---------- | --------------------------- | ----------------------------- |
| KEYWORD    | Reserved words              | `if`, `while`, `int`, `float` |
| IDENTIFIER | `letter (letter \| digit)*` | `x`, `count`, `myVar`         |
| INTEGER    | `digit+`                    | `0`, `42`, `123`              |
| FLOAT      | `digit+ . digit+`           | `3.14`, `0.5`, `2.0`          |
| OPERATOR   | See operator table below    | `+`, `==`, `<=`, `!=`         |
| DELIMITER  | `( ) { } ; , [ ]`           | `{`, `;`, `(`                 |
| STRING     | `" .* "`                    | `"Hello, World!"`             |
| COMMENT    | `// ...` or `/* ... */`     | `// note`, `/* block */`      |

### Operators

| Token  | Lexeme | Token | Lexeme |
| ------ | ------ | ----- | ------ |
| PLUS   | `+`    | EQ    | `==`   |
| MINUS  | `-`    | NEQ   | `!=`   |
| STAR   | `*`    | LT    | `<`    |
| SLASH  | `/`    | GT    | `>`    |
| ASSIGN | `=`    | LTE   | `<=`   |
|        |        | GTE   | `>=`   |

---

## Approach 1 — State-Based (Direct Coded)

### How it works

The entire lexer is a single `while` loop inside `_next_token()`. A variable called `state` holds the current position in the automaton. Each iteration reads one character and uses `if/elif` chains to decide the next state — directly mirroring a drawn NFA/DFA state diagram.

### States

| State         | Meaning                                       |
| ------------- | --------------------------------------------- |
| `START`       | Initial state, beginning of every new token   |
| `IN_ID`       | Accumulating letters/digits for an identifier |
| `IN_INT`      | Accumulating digits for an integer            |
| `IN_FLOAT`    | After the `.` in a real number                |
| `IN_STRING`   | Inside a `"..."` string literal               |
| `IN_SLASH`    | Saw `/` — could be `/`, `//`, or `/*`         |
| `IN_LINE_CMT` | Inside a `//` line comment                    |
| `IN_BLK_CMT`  | Inside a `/* */` block comment                |
| `IN_BLK_END`  | Saw `*` inside block comment                  |
| `IN_NEQ`      | Saw `!` — expecting `=` for `!=`              |
| `IN_EQ`       | Saw `=` — could be `=` or `==`                |
| `IN_LT`       | Saw `<` — could be `<` or `<=`                |
| `IN_GT`       | Saw `>` — could be `>` or `>=`                |
| `DONE`        | Accepting state — token complete              |
| `ERROR`       | Illegal character or malformed token          |

### Retract (unget) mechanism

When the automaton reaches a state like `IN_ID` and reads a non-alphanumeric character, that character terminates the token but does not belong to it. The lexer calls `_unget()` to put the character back so the next call to `_next_token()` can process it correctly. This implements the **maximal munch** rule.

### Keyword resolution

Identifiers and keywords share the same NFA path. After the `IN_ID` state accepts, the lexer checks the matched string against the `KEYWORDS` set in `tokens.py`. If found, the token type is changed from `IDENTIFIER` to `KEYWORD`.

### Pros and Cons

| Pros                         | Cons                                                      |
| ---------------------------- | --------------------------------------------------------- |
| Easy to trace and debug      | Tedious to extend (new token = new states + new branches) |
| No extra data structures     | Logic and data are tightly coupled                        |
| Closely mirrors NFA diagrams | Hard to autogenerate from a grammar                       |

---

## Approach 2 — Stateless (Functional Dispatch)

### How it works

There is no shared `state` variable. Instead, `_next_token()` peeks at the first character of each new lexeme and immediately calls a dedicated scanning function. Each function is fully self-contained and reads only the characters it needs.

### Dispatch table

| First character seen | Function called      |
| -------------------- | -------------------- |
| Letter or `_`        | `_scan_identifier()` |
| Digit                | `_scan_number()`     |
| `"`                  | `_scan_string()`     |
| `/`                  | `_scan_slash()`      |
| `=`, `!`, `<`, `>`   | `_scan_relational()` |
| `+`, `-`, `*`        | `_scan_arithmetic()` |
| `(`, `)`, `{`, etc.  | `_scan_delimiter()`  |

### Per-scanner logic

**`_scan_identifier()`** — consumes letters and digits via a `while` loop, then checks the keyword table.

**`_scan_number()`** — consumes an integer part, then peeks two characters ahead: if the next is `.` and the one after is a digit, it continues to scan a float. Otherwise it returns an INTEGER.

**`_scan_slash()`** — uses `peek(1)` to look one character ahead without consuming it. Routes to line comment, block comment, or plain `/`.

**`_scan_relational()`** — reads the first character, then peeks at the next to decide between single and double-character operators (`<` vs `<=`, `=` vs `==`, etc.).

### Pros and Cons

| Pros                                   | Cons                                       |
| -------------------------------------- | ------------------------------------------ |
| Most readable code structure           | Dispatch logic duplicated across functions |
| Each scanner is independently testable | Harder to autogenerate                     |
| Easy to add a new token type           | Not as close to formal automaton theory    |

---

## Approach 3 — Transition Table Driven

### How it works

The DFA is encoded as a two-dimensional Python dictionary:

```
TRANSITION[state][char_class] → next_state
```

The driver loop is a **generic engine** — it never inspects character identity, only char class indices. This separates the _what_ (table data) from the _how_ (driver logic).

### Character Classes

Instead of 128 ASCII columns, the full alphabet is folded into 24 equivalence classes:

| Index | Class             | Characters                             |
| ----- | ----------------- | -------------------------------------- |
| 0     | LETTER            | `a-z`, `A-Z`, `_`                      |
| 1     | DIGIT             | `0-9`                                  |
| 2     | DOT               | `.`                                    |
| 3     | DQUOTE            | `"`                                    |
| 4–6   | PLUS/MINUS/STAR   | `+`, `-`, `*`                          |
| 7     | SLASH             | `/`                                    |
| 8–11  | EQ/BANG/LT/GT     | `=`, `!`, `<`, `>`                     |
| 12–19 | Delimiters        | `(`, `)`, `{`, `}`, `;`, `,`, `[`, `]` |
| 20–22 | NEWLINE/SPACE/EOF | whitespace and end-of-file             |
| 23    | OTHER             | anything else                          |

This reduces a full ASCII table from 128 columns to just 24.

### Retract logic

Two categories of retract states are defined:

- **`retract_always`**: `IN_ID`, `IN_INT`, `IN_FLOAT`, `A_SLASH` — whenever these transition to `DONE`, the last character is put back unconditionally.
- **`retract_if_not_eq`**: `A_EQ`, `A_LT`, `A_GT` — the last character is put back only if it is not `=` (since `==`, `<=`, `>=` consume both characters, while bare `=`, `<`, `>` should retract).

### Single-character accepting states

States 20–30 (PLUS_S, MINUS_S, etc.) represent single-character tokens. As soon as the driver transitions into one of these states, it breaks immediately without reading another character — avoiding the need to retract.

### Token resolution

After the loop exits, `_make_token(state, prev_state, lexeme)` maps the final `prev_state` to a `TokenType`. This keeps token-type logic out of the generic driver.

### Pros and Cons

| Pros                                           | Cons                                   |
| ---------------------------------------------- | -------------------------------------- |
| Driver loop is reusable — never changes        | Table construction is non-trivial      |
| Adding tokens only requires updating the table | Harder to read/debug than Approach 1   |
| Can be auto-generated from a regex spec        | Token resolution function still needed |

---

## Bonus — Compressed Transition Table

### Motivation

The full transition table has `states × char_classes = 24 × 24 = 576` cells. Inspection shows most rows are dominated by a single value (`DONE` or `ERR`). Storing every cell wastes memory.

### Compression technique: Default-row encoding

Each row is split into:

1. **`default[state]`** — the most frequently occurring next-state in that row (computed at construction time).
2. **`overrides[state]`** — a sparse dict of `{char_class: next_state}` for entries that differ from the default.

Lookup:

```python
def lookup(self, state, cc):
    if cc in self.overrides[state]:
        return self.overrides[state][cc]
    return self.default[state]
```

### Results on this grammar

| Metric                  | Value     |
| ----------------------- | --------- |
| States                  | 24        |
| Character classes       | 24        |
| Dense table cells       | 576       |
| Cells after compression | 63        |
| Memory reduction        | **89.1%** |

### Why it works

Most states in a lexer DFA are either "stay in this state for most inputs" (like `IN_ID` which loops on letters and digits, returning `DONE` for everything else) or "error for almost everything" (like `START` which has a valid transition for ~20 out of 24 classes). The default captures the dominant case; only the minority transitions need explicit storage.

---

## Comparison Summary

| Approach         | Architecture                        | Extensibility | Readability |
| ---------------- | ----------------------------------- | ------------- | ----------- |
| State-Based      | Explicit state variable + if/elif   | Low           | High        |
| Stateless        | First-char dispatch to sub-scanners | Medium        | Highest     |
| Table-Driven     | 2D table + generic driver loop      | High          | Medium      |
| Compressed Table | Sparse default+overrides + driver   | High          | Low         |

All four approaches produce **identical token streams** on the same input, verified by the comparison engine in `main.py`.

### Typical timing (on `program.pascal`, 323 chars, 20 lines)

| Approach                  | Time                                                     |
| ------------------------- | -------------------------------------------------------- |
| Approach 2 — Stateless    | ~0.15 ms (fastest — no table lookups)                    |
| Approach 1 — State-Based  | ~0.27 ms                                                 |
| Approach 3 — Table-Driven | ~0.30 ms                                                 |
| Bonus — Compressed Table  | ~0.33 ms (small overhead from dict lookup vs list index) |

---

## How to Run

```bash
# Navigate to the src directory
cd src

# Run all four approaches and compare
python3 main.py program.pascal

# Run a single approach
python3 approach1_state_based.py program.pascal
python3 approach2_stateless.py program.pascal
python3 approach3_table_driven.py program.pascal
python3 bonus_compressed_table.py program.pascal
```

---
