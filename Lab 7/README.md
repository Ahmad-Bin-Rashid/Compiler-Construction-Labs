# Lab 7: Constructing a Lexical Analyzer using Lex/Flex

## Objective

The objective of this lab is to design and implement a Lexical Analyzer (Lexer) using the compiler construction toolkit **Lex/Flex** to automatically generate code for scanning source tokens.

---

## Technical Overview

Lex/Flex converts regular expression patterns into a Deterministic Finite Automaton (DFA) state machine written in C. In this lab, we implemented a Lexer tailored for a subset of the **Pascal** programming language.

### Components & Features

1. **Case-Insensitive Scanner**: Configured using `%option caseless` to handle Pascal keywords regardless of letter casing.
2. **Token Definitions & Representation**:
   - **Keywords**: `program`, `var`, `integer`, `real`, `function`, `procedure`, `begin`, `end`, `if`, `then`, `else`, `while`, `do`, `array`, `of`, `not`.
   - **Operators**:
     - Assignment Operator (`:=`)
     - Relational Operators (`=`, `<>`, `<`, `<=`, `>`, `>=`)
     - Additive Operators (`+`, `-`, `or`)
     - Multiplicative Operators (`*`, `/`, `div`, `mod`, `and`)
   - **Punctuation & Delimiters**: `(`, `)`, `[`, `]`, `,`, `;`, `:`, `..`, `.`
   - **Identifiers (`ID`)**: Regular expression `[a-zA-Z][a-zA-Z0-9]*`
   - **Numbers (`NUM`)**: Supports integers, floating-point numbers, and exponential notation (e.g., `10`, `3.14`, `1.2e-5`).
3. **Comment & Whitespace Handling**:
   - Skips spaces, tabs, and carriage returns silently.
   - Multiline comment handling bounded by `{` and `}` with error detection for unterminated comments.
   - Tracks line numbers (`line_number`) for error reporting.

---

## File Structure

- `src/pascal_lexer.l`: Flex specification file containing token definitions, regular expressions, transition rules, and the main driver.
- `src/input.pas`: Sample Pascal input program used to test tokenization.

---

## Execution & Verification

### 1. Build Instructions

To generate the C scanner file using Flex and compile it using GCC:

```bash
cd "Lab 7/src"
flex pascal_lexer.l
gcc lex.yy.c -o lexer
```

### 2. Running the Lexer

Execute the compiled Lexer against the sample input:

```bash
./lexer input.pas
```

### 3. Expected Output

```text
Token: PROGRAM      | Lexeme: program
Token: IDENTIFIER   | Lexeme: test
Token: PUNCT        | Lexeme: ;
Token: VAR          | Lexeme: var
Token: IDENTIFIER   | Lexeme: x
Token: PUNCT        | Lexeme: ,
Token: IDENTIFIER   | Lexeme: y
Token: PUNCT        | Lexeme: :
Token: INTEGER      | Lexeme: integer
Token: PUNCT        | Lexeme: ;
...
```
