# Compiler Construction Labs

A comprehensive repository of lab tasks, implementations, algorithms, and documentation for the **Compiler Construction** course (Semester 6).

---

## 📌 Repository Overview

This repository covers key phases of compiler design and construction, spanning lexical analysis, syntactic analysis (top-down and bottom-up parsing), state machine theory, and symbol table management.

| Lab / Module                                                                                    | Topic                       | Core Technologies / Tools | Key Implementations                                              |
| :---------------------------------------------------------------------------------------------- | :-------------------------- | :------------------------ | :--------------------------------------------------------------- |
| **[Lab 1](https://github.com/Ahmad-Bin-Rashid/Compiler-Construction-Labs/tree/main/Lab%201)**   | Expression Evaluator        | Python                    | Infix, Postfix, & Prefix evaluation with step-by-step trace      |
| **[Lab 2](https://github.com/Ahmad-Bin-Rashid/Compiler-Construction-Labs/tree/main/Lab%202)**   | Input Buffering             | Python, Multi-threading   | Double buffering I/O system with asynchronous thread refilling   |
| **[Lab 4](https://github.com/Ahmad-Bin-Rashid/Compiler-Construction-Labs/tree/main/Lab%204)**   | Regular Expressions & NFAs  | JFLAP, Regex              | Pascal subset token regular expressions and NFA state diagrams   |
| **[Lab 5](https://github.com/Ahmad-Bin-Rashid/Compiler-Construction-Labs/tree/main/Lab%205)**   | Lexical Analyzer (Manual)   | Python                    | Hand-written Pascal scanner across 3 architectural approaches    |
| **[Lab 7](https://github.com/Ahmad-Bin-Rashid/Compiler-Construction-Labs/tree/main/Lab%207)**   | Lexical Analyzer with Flex  | C, Flex                   | Lexer generated using Flex specification for Pascal subset       |
| **[Lab 9](https://github.com/Ahmad-Bin-Rashid/Compiler-Construction-Labs/tree/main/Lab%209)**   | Recursive Descent Parsing   | Python                    | Top-down LL(1) recursive descent parser for Pascal               |
| **[Lab 10](https://github.com/Ahmad-Bin-Rashid/Compiler-Construction-Labs/tree/main/Lab%2010)** | LL(1) Predictive Parsing    | Python                    | Non-recursive table-driven predictive parser with explicit stack |
| **[Lab 12](https://github.com/Ahmad-Bin-Rashid/Compiler-Construction-Labs/tree/main/Lab%2012)** | Operator Precedence Parsing | Python                    | LEADING/TRAILING sets computation, precedence matrix & parser    |
| **[Lab 13](https://github.com/Ahmad-Bin-Rashid/Compiler-Construction-Labs/tree/main/Lab%2013)** | Symbol Table Manager        | Python                    | Scoped hash-table symbol manager & semantic analyzer integration |

---

## 🛠️ Requirements & Tools

- **Python 3.9+** (Standard Library for Python-based parsers and scripts)
- **C Compiler (GCC / Clang)** (For compiling Flex-generated C scanners)
- **Flex (Fast Lexical Analyzer Generator)** (For Lab 7 lexer building)
- **JFLAP / MS Word** (For reviewing documentation & NFA diagrams)

---

## 🚀 Quick Start & How to Use

### 1. Python Parsers & Tools (Lab 1, 5, 9, 10, 12, 13)

Most lab tools require only standard Python:

```bash
# Example: Run the LL(1) non-recursive predictive parser
python "Lab 10/ll1_parser.py"

# Example: Run Symbol Table tests
python "Lab 13/src/symbol_table.py"
```

### 2. Flex / C Lexical Analyzer (Lab 7)

Generate and compile the Lexer using Flex and GCC:

```bash
cd "Lab 7/src"
flex pascal_lexer.l
gcc lex.yy.c -o lexer
./lexer input.pas
```

---

## 📁 Workspace Directory Structure

```text
CC Lab/
├── Lab 1/       # Step-by-step Infix/Postfix/Prefix Expression Evaluator
├── Lab 2/       # Multi-threaded Double Buffering System for I/O
├── Lab 4/       # Regex and NFA State Diagrams for Pascal subset
├── Lab 5/       # Hand-crafted Pascal Lexical Analyzer (Python)
├── Lab 7/       # Flex/Lex Pascal Lexical Analyzer Specification (C/Flex)
├── Lab 9/       # Recursive Descent Parser implementation
├── Lab 10/      # Non-recursive LL(1) Table-driven Parser
├── Lab 12/      # Operator Precedence Parser & LEADING/TRAILING sets
├── Lab 13/      # Scoped Symbol Table Manager & Parser Integration
└── README.md    # Repository root documentation
```

---

## 📜 License

This repository is intended for **educational and academic use only**.
