# Week 4: Regular Expressions & NFA State Diagram Design

## CC Lab - Compiler Construction · Lexical Analysis

Design of regular expressions and NFA state diagrams for all token categories defined in the Pascal subset grammar.

## Learning Objectives

- Identify all token categories in the Pascal subset
- Write formal regular expressions for each token class
- Design NFA state diagrams that recognize each token
- Understand the relationship between regex, NFA, and lexical analysis

## Project Structure

```
Lab 4/
├── README.md                       # This documentation
├── docs/
│   ├── jflap.docx                  # Lab report with detailed diagrams
│   └── Subset of Pascal.pdf        # Pascal subset grammar reference (A.3 & A.4)
└── JFlap Diagrams/
    ├── pascal_identifier.jff       # NFA — Identifier (id)
    ├── pascal_num.jff              # NFA — Numeric Constant (num)
    ├── pascal_assignop.jff         # NFA — Assignment Operator (assignop)
    ├── pascal_relop.jff            # NFA — Relational Operators (relop)
    ├── pascal_addop.jff            # NFA — Additive Operators (addop)
    ├── pascal_mulop.jff            # NFA — Multiplicative Operators (mulop)
    ├── pascal_comment.jff          # NFA — Comment
    └── pascal_whitespace.jff       # NFA — Whitespace
```

## Prerequisites

- **JFLAP** (Java Formal Languages and Automata Package) to open `.jff` diagram files

---

## Section 1 — Token Identification

The Pascal subset defines the following token categories, derived from sections A.3 and A.4 of the appendix. Each token is the atomic unit produced by the lexical analyzer and passed to the parser.

| # | Token Name | Category | Lexemes / Examples |
|---|------------|----------|--------------------|
| 1 | `id` | Identifier | `x`, `y`, `gcd`, `example`, `result1` |
| 2 | `num` | Numeric Constant | `0`, `42`, `3.14`, `2.5E10`, `1.0E-3` |
| 3 | `assignop` | Assignment Operator | `:=` |
| 4 | `relop` | Relational Operator | `=`  `<>`  `<`  `<=`  `>=`  `>` |
| 5 | `addop` | Additive Operator | `+`  `-`  `or` |
| 6 | `mulop` | Multiplicative Operator | `*`  `/`  `div`  `mod`  `and` |
| 7 | `keyword` | Reserved Word | `program`, `var`, `begin`, `end`, `if`, `then`, `else`, `while`, `do`, `function`, `procedure`, `array`, `of`, `integer`, `real`, `not` |
| 8 | `comment` | Comment (ignored) | `{ this is a comment }` |
| 9 | `delimiters` | Punctuation / Delimiters | `(` `)` `[` `]` `;` `:` `,` `.` |

> **Note:** Keywords are a subset of identifiers — they match the same pattern as `id` but are reserved. The lexical analyzer checks if a matched identifier belongs to the keyword list. There is also no syntactic distinction between a simple variable and a parameterless function call (both use `factor → id`).

---

## Section 2 — Regular Expressions

Using the notation from Section 3.3 of the textbook. Primitives are defined first, then composed.

| Token | Regular Expression | Description |
|-------|--------------------|-------------|
| `letter` | `[a-zA-Z]` | Any upper or lowercase alphabetic character |
| `digit` | `[0-9]` | Any single decimal digit |
| `digits` | `digit · digit*` | One or more digits (`digit+`) |
| `id` | `letter · (letter \| digit)*` | Starts with letter, followed by zero or more letters or digits |
| `num` | `digits (. digits)? (E [+\|-]? digits)?` | Integer or real: optional fractional part, optional exponent |
| `assignop` | `:=` | Colon followed immediately by equals sign |
| `relop` | `= \| <> \| < \| <= \| >= \| >` | Six relational/comparison operators |
| `addop` | `+ \| - \| or` | Addition, subtraction, or logical OR |
| `mulop` | `* \| / \| div \| mod \| and` | Multiplication, division, integer div/mod, logical AND |
| `comment` | `{ [^}]* }` | Any sequence of non-closing-brace chars surrounded by `{` `}` |
| `whitespace` | `( blank \| newline \| tab )+` | Ignored by lexer (required around keywords) |

---

## Section 3 — NFA State Diagrams

Each NFA below recognizes one token category. States are represented as circles: the **blue** state is the start state, **green** double-ring states are accepting states, and plain blue circles are intermediate states. Transition labels on arrows denote the input character class.

### 3.1 — `id` (Identifier / Keyword)

**RE:** `letter · (letter | digit)*`

```
          letter          letter | digit
  ┌───┐ ────────► ╔═══╗ ◄────────────┐
  │q₀ │           ║q₁ ║ ─────────────┘
  └───┘           ╚═══╝
 START            ACCEPT → check keyword table
```

- **q₀** = start state
- **q₁** = accepting state

### 3.2 — `num` (Numeric Constant — Integer & Real)

**RE:** `digit+ (. digit+)? (E [+|-]? digit+)?`

```
        digit         .          digit         E
  ┌───┐ ───► ╔═══╗ ───► ┌───┐ ───► ╔═══╗ ───► ┌───┐
  │q₀ │      ║q₁ ║      │q₂ │      ║q₃ ║      │q₄ │
  └───┘      ╚═══╝      └───┘      ╚═══╝      └───┘
              ↺digit                 ↺digit     │  \
                                     │           │  + | -
                                     │ E         ▼
                                     └────► ┌───┐
                                            │q₅ │
                                            └───┘
                                              │ digit
                                              ▼
                                            ╔═══╗
                                            ║q₆ ║
                                            ╚═══╝
                                             ↺digit
```

| State | Role |
|-------|------|
| q₀ | start |
| q₁, q₃, q₆ | accepting |
| q₂, q₄, q₅ | intermediate |

### 3.3 — `assignop` (Assignment Operator `:=`)

**RE:** `:=`

```
          :            =
  ┌───┐ ───► ┌───┐ ───► ╔═══╗
  │q₀ │      │q₁ │      ║q₂ ║
  └───┘      └───┘      ╚═══╝
 START                  ACCEPT
```

- **q₀** = start
- **q₂** = accept (after `:=` seen)

### 3.4 — `relop` (Relational Operators `= <> < <= > >=`)

**RE:** `= | <> | < | <= | > | >=`

```
              =
  ┌───┐ ──────────► ╔═══╗  (=)
  │q₀ │             ║q₁ ║
  │   │             ╚═══╝
  │   │    <                     =
  │   │ ──────────► ╔═══╗ ──────────► ╔═══╗  (<=)
  │   │             ║q₂ ║             ║q₄ ║
  │   │             ╚═══╝             ╚═══╝
  │   │              │
  │   │              │ >
  │   │              ▼
  │   │             ╔═══╗  (<>)
  │   │             ║q₃ ║
  │   │             ╚═══╝
  │   │    >                     =
  │   │ ──────────► ╔═══╗ ──────────► ╔═══╗  (>=)
  └───┘             ║q₅ ║             ║q₆ ║
                    ╚═══╝             ╚═══╝
```

| State | Accepts |
|-------|---------|
| q₁ | `=` |
| q₂ | `<` |
| q₃ | `<>` |
| q₄ | `<=` |
| q₅ | `>` |
| q₆ | `>=` |

### 3.5 — `addop` (Additive Operators `+ − or`)

**RE:** `+ | - | or`

```
              +
  ┌───┐ ──────────► ╔═══╗  (+)
  │q₀ │             ║q₁ ║
  │   │             ╚═══╝
  │   │    -
  │   │ ──────────► ╔═══╗  (−)
  │   │             ║q₂ ║
  │   │             ╚═══╝
  │   │    o            r
  │   │ ──────────► ┌───┐ ──────────► ╔═══╗  (or)
  └───┘             │q₃ │             ║q₄ ║
                    └───┘             ╚═══╝
```

- **q₀** = start
- **q₁** (+), **q₂** (−), **q₄** (or) = accepting

### 3.6 — `mulop` (Multiplicative Operators `* / div mod and`)

**RE:** `* | / | div | mod | and`

```
              *
  ┌───┐ ──────────► ╔═══╗  (*)
  │q₀ │             ║q₁ ║
  │   │             ╚═══╝
  │   │    /
  │   │ ──────────► ╔═══╗  (/)
  │   │             ║q₂ ║
  │   │             ╚═══╝
  │   │    d      i      v
  │   │ ───► q₃ ───► q₄ ───► ╔═══╗  (div)
  │   │                       ║q₅ ║
  │   │                       ╚═══╝
  │   │    m      o      d
  │   │ ───► q₆ ───► q₇ ───► ╔═══╗  (mod)
  │   │                       ║q₈ ║
  │   │                       ╚═══╝
  │   │    a      n      d
  │   │ ───► q₉ ───► q₁₀ ──► ╔═══╗  (and)
  └───┘                       ║q₁₁║
                              ╚═══╝
```

- **q₀** = start
- **q₁** (\*), **q₂** (/), **q₅** (div), **q₈** (mod), **q₁₁** (and) = accepting

### 3.7 — `comment` (`{ … }`)

**RE:** `{ [^}]* }`

```
          {          [^}]         }
  ┌───┐ ───► ┌───┐ ◄────┐  ───► ╔═══╗
  │q₀ │      │q₁ │ ─────┘       ║q₂ ║
  └───┘      └───┘              ╚═══╝
 START                         ACCEPT (discard)
```

- **q₀** = start
- **q₂** = accept (token discarded)

---

## Section 4 — Written Explanation of Regex & NFA Design

### 1 · Identifier (`id`)

**Regex:** `letter · (letter | digit)*`

An identifier must begin with a letter — this is captured by the mandatory first `letter` in the regex. After that, zero or more letters or digits may follow, expressed by the Kleene closure `(letter | digit)*`.

**NFA design:** The start state q₀ transitions to accepting state q₁ on any letter. State q₁ has a self-loop accepting any letter or digit, allowing identifiers of arbitrary length. Since q₁ is the only accepting state, the NFA accepts as soon as it encounters a character that is neither a letter nor a digit. The lexer then checks whether the matched string is a reserved keyword.

### 2 · Numeric Constant (`num`)

**Regex:** `digit+ (. digit+)? (E [+|-]? digit+)?`

Numbers include integers and reals. The regex has three parts: a mandatory integer part (`digit+`), an optional fractional part (`. digit+`), and an optional scientific exponent part (`E [+|-]? digit+`).

**NFA design:** The NFA has three accepting states: q₁ (integer), q₃ (real with fraction), and q₆ (number with exponent). From both q₁ and q₃ an `E` transitions to q₄ (exponent start). q₄ optionally accepts a sign (`+` or `−`) via q₅, or transitions directly to q₆ on a digit — this models the optional sign character. q₆ self-loops on digits. This structure correctly implements the grammar rule for `optional_fraction` and `optional_exponent` from section A.4.

### 3 · Assignment Operator (`assignop`)

**Regex:** `:=`

This is a simple two-character token. The NFA is a linear chain of three states: q₀ →(on `:`) → q₁ →(on `=`) → q₂ (accept). It is crucial that the lexer correctly distinguishes `:=` from the standalone `:` (colon delimiter). This is handled by looking ahead — the lexer only accepts the token when both characters are seen.

### 4 · Relational Operators (`relop`)

**Regex:** `= | <> | < | <= | > | >=`

The NFA is a branching structure from a single start state q₀. Six paths are available:

- **q₀ →(=)→ q₁** (accept): The single equals sign.
- **q₀ →(<)→ q₂** (accept): Less-than alone. q₂ can further branch:
  - **q₂ →(>)→ q₃** (accept): Not-equal `<>`.
  - **q₂ →(=)→ q₄** (accept): Less-than-or-equal `<=`.
- **q₀ →(>)→ q₅** (accept): Greater-than alone. q₅ can branch:
  - **q₅ →(=)→ q₆** (accept): Greater-than-or-equal `>=`.

States q₂ and q₅ are simultaneously accepting states (for bare `<` and `>`) and intermediate states (for two-character relops). The lexer uses **maximal munch** — it prefers the longest possible token, so it looks ahead one character before deciding.

### 5 · Additive Operators (`addop`)

**Regex:** `+ | − | or`

**NFA design:** Three paths branch from q₀. Single-character operators `+` and `−` each have a direct transition to their own accepting states (q₁ and q₂). The keyword `or` requires two transitions: q₀ →(o)→ q₃ →(r)→ q₄ (accept). Note that the `o` character in `or` is shared with no other token starting character in this category, so there is no ambiguity. However, the lexer must be careful not to confuse `or` with an identifier starting with "or…" — this is resolved by checking for a word boundary (non-letter, non-digit) after the match.

### 6 · Multiplicative Operators (`mulop`)

**Regex:** `* | / | div | mod | and`

**NFA design:** Five paths branch from q₀. The single-character symbols `*` and `/` transition immediately to accepting states q₁ and q₂. The three keyword operators each require a three-state linear chain:

- **div:** q₀→(d)→q₃→(i)→q₄→(v)→q₅ ✓
- **mod:** q₀→(m)→q₆→(o)→q₇→(d)→q₈ ✓
- **and:** q₀→(a)→q₉→(n)→q₁₀→(d)→q₁₁ ✓

A key observation: the first characters `d`, `m`, and `a` are all distinct, so the NFA can determine the correct branch immediately at q₀ without ε-transitions. This makes it efficient — effectively a DFA for this token class.

### 7 · Comment

**Regex:** `{ [^}]* }`

Comments are enclosed in curly braces and may not nest (the spec states they may not contain a `{` character). The NFA has a simple three-state structure: q₀ →({)→ q₁ →(})→ q₂ (accept). State q₁ has a self-loop on any character except `}` (the complement class `[^}]`), allowing arbitrarily long comment bodies. The token is accepted but immediately discarded by the lexer — it produces no output to the parser.

### 8 · General Design Principles

- **Maximal Munch:** When multiple tokens could match at a position, the lexer always selects the longest possible match. This resolves ambiguity between `<` and `<=`, or between a keyword and an identifier prefix.
- **Keyword vs. Identifier:** Keywords share the same NFA as identifiers. After a match in the identifier NFA, the lexer consults a symbol table pre-loaded with all reserved words to determine the correct token type.
- **NFA → DFA:** Each NFA can be converted to a DFA via the subset construction algorithm. For most of these token NFAs, the NFA is already deterministic (no ε-transitions, no ambiguous branches on the same input symbol), making the conversion trivial.
- **Error handling:** Any character that does not begin a valid token triggers an error state. The lexer calls the error-printing routine and halts or attempts to recover.

---

## Reference — Transition Tables (δ functions)

### Table 1 — Identifier NFA (δ)

| State | letter | digit | other | Accept? |
|-------|--------|-------|-------|---------|
| q₀ (start) | q₁ | — | error | No |
| q₁ | q₁ | q₁ | — | ✓ Yes |

### Table 2 — Number NFA (δ)

| State | digit | `.` | E | `+` / `−` | other | Accept? |
|-------|-------|-----|---|-----------|-------|---------|
| q₀ | q₁ | — | — | — | err | No |
| q₁ | q₁ | q₂ | q₄ | — | — | ✓ |
| q₂ | q₃ | — | — | — | err | No |
| q₃ | q₃ | — | q₄ | — | — | ✓ |
| q₄ | q₆ | — | — | q₅ | err | No |
| q₅ | q₆ | — | — | — | err | No |
| q₆ | q₆ | — | — | — | — | ✓ |

### Table 3 — relop NFA (δ)

| State | `=` | `<` | `>` | other | Accept? |
|-------|-----|-----|-----|-------|---------|
| q₀ | q₁ | q₂ | q₅ | err | No |
| q₁ | — | — | — | — | ✓ (`=`) |
| q₂ | q₄ | — | q₃ | — | ✓ (`<`) |
| q₃ | — | — | — | — | ✓ (`<>`) |
| q₄ | — | — | — | — | ✓ (`<=`) |
| q₅ | q₆ | — | — | — | ✓ (`>`) |
| q₆ | — | — | — | — | ✓ (`>=`) |
