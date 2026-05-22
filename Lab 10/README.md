# LL(1) Non-Recursive Predictive Parser for Pascal

**Lab 11 — Compiler Construction, Spring 2026**

---

## Overview

This project implements a **non-recursive (table-driven) LL(1) predictive parser** for a Pascal-like language entirely in Python. Unlike the recursive descent parser from Lab 10 — which uses the program call stack implicitly — this parser maintains an **explicit stack** and drives all parsing decisions through a pre-computed two-dimensional **parsing table**.

---

## How to Run

```bash
python ll1_parser.py
```

No external dependencies are required (Python 3.9+ standard library only).

---

## What the Program Does

When executed, the program carries out four sequential steps:

### Step 1 — Compute FIRST Sets

The FIRST set of a grammar symbol `X` is the set of terminals that can appear as the **first token** of any string derived from `X`. If `X` can derive the empty string, then `eps` is also in `FIRST(X)`.

The program computes these automatically using the iterative fixed-point algorithm:

```
For each production A -> Y1 Y2 ... Yk:
  add FIRST(Y1) - {eps} to FIRST(A)
  if eps in FIRST(Y1): add FIRST(Y2) - {eps} to FIRST(A)
  ...
  if eps in FIRST(Y1..Yk): add eps to FIRST(A)
```

### Step 2 — Compute FOLLOW Sets

The FOLLOW set of a non-terminal `A` is the set of terminals that can appear **immediately after** `A` in some sentential form.

Rules applied:
1. `$` ∈ FOLLOW(start symbol)
2. For `A -> α B β`: add `FIRST(β) - {eps}` to `FOLLOW(B)`
3. For `A -> α B` or `A -> α B β` where `eps ∈ FIRST(β)`: add `FOLLOW(A)` to `FOLLOW(B)`

### Step 3 — Build the LL(1) Parsing Table

For each production `A -> α`:
1. For each terminal `a ∈ FIRST(α)`: add `A -> α` to `M[A, a]`
2. If `eps ∈ FIRST(α)`: for each terminal `b ∈ FOLLOW(A)`: add `A -> α` to `M[A, b]`

The program also checks for **conflicts** (cells with more than one entry). A conflict means the grammar is not LL(1). The Pascal grammar used here is conflict-free.

### Step 4 — Parse Input Strings (Step-by-Step Trace)

The non-recursive parsing algorithm (from Section 3.7 of the manual):

```
Initialise: stack = [$ , START]
Repeat:
  X = top of stack
  a = current input token
  if X == a == $:        ACCEPT
  elif X is terminal:    if X == a: pop, advance; else ERROR
  elif X is non-terminal:
    if M[X, a] exists:   pop X, push RHS of M[X,a] (reversed)
    else:                ERROR
```

Every step is printed as a row in a trace table with four columns:

| Column | Contents |
|---|---|
| **Stack** | Current stack contents (bottom `$` on left, top on right) |
| **Input** | Remaining input tokens |
| **Output** | Production applied (if expanding a non-terminal) |
| **Action** | `Initial`, `Match 'x'`, `Expand`, `[ACCEPT]`, or `[ERROR]` |

---

## Grammar

The grammar is for a simplified Pascal language. It has been prepared (left-recursion removed, left-factored) to satisfy the LL(1) property:

```
PROGRAM    -> program id ; BLOCK .
BLOCK      -> VAR_DECL STMT_BLOCK
VAR_DECL   -> var DECL_LIST | eps
DECL_LIST  -> DECL DECL_REST
DECL_REST  -> ; DECL_LIST | eps
DECL       -> id : TYPE
TYPE       -> integer | real
STMT_BLOCK -> begin STMT_LIST end
STMT_LIST  -> STMT STMT_REST
STMT_REST  -> ; STMT_LIST | eps
STMT       -> ASSIGN_STMT | IF_STMT | WHILE_STMT
ASSIGN_STMT-> id := EXPR
IF_STMT    -> if EXPR then STMT else STMT
WHILE_STMT -> while EXPR do STMT
EXPR       -> TERM EXPRP
EXPRP      -> + TERM EXPRP | - TERM EXPRP | eps
TERM       -> FACTOR TERMP
TERMP      -> * FACTOR TERMP | / FACTOR TERMP | eps
FACTOR     -> ( EXPR ) | id | number
```

---

## Sample Output

### FIRST and FOLLOW 

```
========================================================================
  FIRST and FOLLOW Sets
========================================================================
  Non-Terminal       FIRST                            FOLLOW
  --------------------------------------------------------------------
  PROGRAM            { id, integer, number, ... }     { $ }
  EXPR               { (, id, number }                { ), $, ;, do, else, end, then }
  EXPRP              { +, -, eps }                    { ), $, ;, do, else, end, then }
  FACTOR             { (, id, number }                { *, +, -, /, ), $, ... }
  ...
```

### Parsing Table 

```
  Non-Terminal  |        id        |        +        |  ...
  --------------+-----------------+-----------------+------
  EXPR          | EXPR->TERM EXPRP|                 |  ...
  EXPRP         |                 | EXPRP->+ TERM.. |  ...
  FACTOR        |  FACTOR->id     |                 |  ...
```

### Step-by-Step Trace (Test 4 — no variables)

```
Stack                                 Input                             Output                        Action
----------------------------------------------------------------------------------------------------------
$ PROGRAM                             program id ; begin id := number . $                            Initial
$ . BLOCK ; id program                program id ; begin id := number . $  PROGRAM -> program id ; BLOCK .  Expand
...
$ . STMT_BLOCK                        begin id := number end . $            VAR_DECL -> eps          Expand
...
$                                     $                                                              *** ACCEPT ***
```

---

## Test Cases

| # | Description | Expected |
|---|---|---|
| 1 | Simple variable declaration + assignment | PASS |
| 2 | If-else with arithmetic | PASS |
| 3 | While loop | PASS |
| 4 | No `var` section (epsilon VAR_DECL) | PASS |
| 5 | Nested parenthesised expression | PASS |
| 6 | Missing `:=` (intentional syntax error) | FAIL (correctly detected) |

---

## Key Differences from Recursive Descent Parser (Lab 10)

| Aspect | Recursive Descent (Lab 10) | LL(1) Table-Driven (Lab 11) |
|---|---|---|
| Stack | Implicit (call stack) | Explicit (Python list) |
| Grammar coupling | One function per non-terminal | Single generic parse loop |
| Table | None needed | Pre-computed M[NT, Terminal] |
| FIRST/FOLLOW | Computed mentally by author | Computed automatically |
| Portability | Grammar is hard-wired in code | Change grammar → new table |
| Trace format | Print inside each function | Uniform table printed per step |

---

## Code Structure

```
ll1_parser.py
  Section 1 — Grammar definition (GRAMMAR list, NON_TERMINALS, TERMINALS)
  Section 2 — compute_first()         FIRST set algorithm
  Section 3 — compute_follow()        FOLLOW set algorithm
  Section 4 — build_parse_table()     Table construction + conflict check
  Section 5 — tokenize()              Lexer (regex-based)
  Section 6 — parse()                 Stack-driven LL(1) algorithm + trace
  Section 7 — print_first_follow()    Display helpers
              print_parse_table()
  Section 8 — run_test() / main()     Test driver
```

---

