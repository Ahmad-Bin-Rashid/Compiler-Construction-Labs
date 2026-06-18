# Lab 12 — Operator Precedence Parser for Pascal

## Overview

This lab implements two core components of a bottom-up **Operator Precedence Parser** for the Pascal expression language, as described in the lab manual.

| File | Purpose |
|---|---|
| `leading_trailing.py` | Computes **LEADING** and **TRAILING** sets via fixed-point iteration |
| `op_prec_table.py` | Builds the **Operator Precedence Table** from those sets |
| `op_prec_parser.py` | **Parser driver** — tokenises Pascal expressions and runs the stack-based algorithm |

---

## Pascal Expression Grammar

The grammar covers Pascal's full expression hierarchy (arithmetic, boolean, and relational operators). It satisfies both operator grammar conditions: **no ε-productions** and **no adjacent non-terminals**.

```
E  ->  E relop R  |  R          (lowest precedence — relational)
R  ->  R addop T  |  T          (adding operators)
T  ->  T mulop F  |  F          (multiplying operators — highest)
F  ->  ( E )      |  id         (atoms / parenthesised sub-expressions)
```

### Terminal Categories

| Token | Pascal Operators |
|---|---|
| `relop` | `=`  `<>`  `<`  `>`  `<=`  `>=` |
| `addop` | `+`  `-`  `or`  `xor` |
| `mulop` | `*`  `/`  `div`  `mod`  `and`  `shl`  `shr` |
| `(` `)` | Parentheses |
| `id` | Identifiers and numeric literals |

---

## LEADING and TRAILING Sets

Computed by `leading_trailing.py` using the fixed-point closure rules from §3.4 of the lab manual.

| Non-Terminal | LEADING | TRAILING |
|---|---|---|
| `E` | `{ relop, addop, mulop, (, id }` | `{ relop, addop, mulop, ), id }` |
| `R` | `{ addop, mulop, (, id }` | `{ addop, mulop, ), id }` |
| `T` | `{ mulop, (, id }` | `{ mulop, ), id }` |
| `F` | `{ (, id }` | `{ ), id }` |

---

## Operator Precedence Table

Built by `op_prec_table.py`. Rows = top-of-stack terminal; Columns = current input terminal.

|        | relop | addop | mulop | `(` | `)` | id  | `$`  |
|--------|-------|-------|-------|-----|-----|-----|------|
| relop  | `.>`  | `<.`  | `<.`  | `<.`| `.>`| `<.`| `.>` |
| addop  | `.>`  | `.>`  | `<.`  | `<.`| `.>`| `<.`| `.>` |
| mulop  | `.>`  | `.>`  | `.>`  | `<.`| `.>`| `<.`| `.>` |
| `(`    | `<.`  | `<.`  | `<.`  | `<.`| `=.`| `<.`| ERR  |
| `)`    | `.>`  | `.>`  | `.>`  | ERR | `.>`| ERR | `.>` |
| id     | `.>`  | `.>`  | `.>`  | ERR | `.>`| ERR | `.>` |
| `$`    | `<.`  | `<.`  | `<.`  | `<.`| ERR | `<.`| acc  |

**Key:** `<.` = shift (yield), `=.` = shift (equal), `.>` = reduce, `acc` = accept, blank = error.

> No conflicts detected — the grammar is a valid operator-precedence grammar.

---

## Algorithm (§3.6 — Stack Driver)

```
push $ on stack
ip = 0
loop:
    a = topmost terminal on stack
    b = input[ip]
    rel = table[a][b]

    if a == $ and b == $:  ACCEPT
    if rel == <. or =.:    push b; ip++
    if rel == .>:          pop until top terminal has <. to last popped terminal; push E
    else:                  ERROR
```

---

## How to Run

### 1. LEADING / TRAILING Sets

```bash
python3 leading_trailing.py
```

### 2. Operator Precedence Table

```bash
python3 op_prec_table.py
```

### 3. Parser — command-line mode

```bash
python3 op_prec_parser.py "a + b * c"
python3 op_prec_parser.py "x = y + 1"
python3 op_prec_parser.py "a * (b + c)"
```

### 4. Parser — interactive mode

```bash
python3 op_prec_parser.py
```

Then type expressions at the `>` prompt. Type `quit` to exit.

---

## Example Traces

### `a + b * c`  — multiply before add (correct Pascal precedence)

```
STACK                            INPUT                            REL     ACTION
$ <. id → Shift id
$ → Reduce id → E
$ E <. addop → Shift addop
$ E addop <. id → Shift id
$ E addop → Reduce id → E
$ E addop E <. mulop → Shift mulop
$ E addop E mulop <. id → Shift id
$ E addop E mulop → Reduce id → E
$ E addop E .> $ → Reduce mulop → E
$ E .> $ → Reduce addop → E
$ E   $=$ ACCEPT
```

### `(a`  — unmatched parenthesis (error)

```
$ <. ( → Shift (
$ ( <. id → Shift id
$ ( → Reduce id → E
$ ( E   ERR — no relation for ((, $)   ERROR
```

---

## Known Limitations of Operator Precedence Parsing

- Cannot parse grammars with ε-productions or adjacent non-terminals.
- Does not track which exact production was reduced (only a generic `E` is pushed).
- Unary operators (e.g. unary `-`, `not`) require pre-processing of the token stream.
- Some structurally invalid inputs may be accepted (e.g. `a + + b`) because the parser only checks terminal relations, not the full syntactic structure.

---

## Post-Lab Questions

### Q1. Why does an operator precedence parser refuse to accept grammars with epsilon productions or grammars in which two non-terminals appear next to each other?

The entire mechanism of operator precedence parsing is built on **relations between pairs of consecutive terminals**. The parser scans the stack looking for the topmost terminal and compares it with the current input terminal to decide whether to shift or reduce.

- **Epsilon (ε) productions** mean a non-terminal can disappear, producing the empty string. This would allow two terminals that were originally separated by a non-terminal to suddenly become adjacent in an unpredictable way, making it impossible to pre-compute a stable precedence relation between them. The LEADING and TRAILING sets — and therefore the table — would be undefined or inconsistent.

- **Adjacent non-terminals** (e.g. `A → B C`) mean there is no terminal sitting between `B` and `C` to anchor a precedence relation. The parser skips non-terminals when scanning the stack, so it has no way to determine where the boundary between two consecutive handles lies. Without a terminal separator there is simply no entry to look up in the table.

In short: the table only stores terminal-vs-terminal relations, so the grammar *must* guarantee that every pair of adjacent grammar symbols is separated by at least one terminal.

---

### Q2. Why does the parser not need to record exactly which non-terminal is produced after a reduction?

After a reduction, the parser pushes a generic placeholder (we use `E`) instead of the actual non-terminal (`R`, `T`, `F`, etc.). This works because **all further parsing decisions are made purely on terminals**.

When the driver needs to pick a relation, it skips over any non-terminals on the stack and looks only at the topmost terminal. The identity of the non-terminal sitting above it is completely irrelevant — the next shift/reduce decision depends solely on which terminal is on top and which terminal is coming from the input.

The trade-off is that operator precedence parsers do not produce a labelled parse tree directly. They produce a *sequence of reductions*, which is enough information to evaluate an expression (e.g. call the right arithmetic operation at each step), but not enough to reconstruct the exact derivation tree. For a calculator or expression evaluator this is perfectly fine; for a full compiler one would attach a semantic action to each reduce step instead.

---

### Q3. In what sense is operator precedence parsing weaker than SLR(1)? Give an example of a grammar that is SLR(1) but not operator precedence.

**Operator precedence is strictly weaker** than SLR(1) in the following ways:

| Aspect | Operator Precedence | SLR(1) |
|---|---|---|
| Grammar class | Operator grammars only | Any unambiguous CFG (and some ambiguous ones) |
| Epsilon productions | Not allowed | Allowed |
| Adjacent non-terminals | Not allowed | Allowed |
| Conflict resolution | Only by precedence/associativity | Via LR item sets + FOLLOW sets |
| Parse tree | Not produced directly | Full parse tree available |

**Example — SLR(1) but NOT operator precedence:**

```
S  ->  A B
A  ->  a
B  ->  b
```

This grammar has the production `S → A B` where `A` and `B` are two adjacent non-terminals with **no terminal between them**. This immediately violates the operator grammar condition, so no operator precedence table can be built. However, the grammar is a simple, unambiguous CFG and is trivially SLR(1) (its LR(0) automaton has no conflicts).

Another classic example is any grammar with ε-productions, such as:

```
S  ->  a S b  |  ε
```

This is SLR(1) but fails the operator grammar test due to the ε-production.

---

### Q4. How are unary operators such as unary minus typically handled in an operator precedence parser?

Operator precedence parsers deal with **binary infix operators** naturally, but unary operators (prefix position, single operand) are trickier because the same symbol (e.g. `-`) can appear as both binary subtraction and unary negation, and the table can only store one relation per cell.

The standard approaches are:

1. **Lexer-level disambiguation (most common):** The tokeniser (lexer) distinguishes between the two uses by context. If a `-` follows an operator, an open parenthesis, or the start of input, it is emitted as a different token — say `uminus` — so the parser sees a completely separate terminal and can assign it its own column/row in the table with the appropriate (highest) precedence.

2. **Grammar transformation:** Introduce a dedicated production for the unary form, e.g.:
   ```
   F  ->  - F  |  ( E )  |  id
   ```
   Then `-` appearing before `F` gets its own precedence relation (via LEADING(F)) that is higher than the binary `-`. Care must be taken not to create conflicts with the binary rule.

3. **Pre-processing pass:** Before parsing, scan the token stream and replace every unary occurrence of `-` with a special sentinel token, then restore the original symbol during semantic action evaluation.

---

### Q5. If a parsing table cell contains more than one relation, the grammar is not operator precedence. Suggest two transformations that may sometimes resolve the conflict.

A conflict means two different rules (e.g. shift and reduce) apply to the same terminal pair. Two standard resolution strategies are:

1. **Grammar refactoring / disambiguation by stratification.**
   Introduce additional non-terminal levels so that each operator lives in exactly one level of the hierarchy. For example, if `+` appears in two different productions that interact and cause a conflict, split them into separate non-terminals (like the classic `E → R → T → F` stratification used in this lab). Each operator then has an unambiguous position in the hierarchy and the conflicting cell disappears.

2. **Operator precedence / associativity declarations (ad-hoc rule).**
   When two operators conflict because both try to claim the same handle, explicitly break the tie by assigning one a higher precedence or by declaring associativity:
   - If `a` and `b` are the same operator and the conflict is between `a <. b` and `a .> b`, declare the operator **left-associative** (force `.>`) or **right-associative** (force `<.`) and keep only the chosen relation, discarding the other.
   - If `a` and `b` are different operators at the same intended precedence level, raise or lower one of them to a different level to eliminate the ambiguity.

   This is how practical tools like `yacc`/`bison` handle operator conflicts — they let the grammar writer annotate operators with `%left`, `%right`, or `%nonassoc` directives which resolve the conflict by fiat rather than by grammar restructuring.

---
