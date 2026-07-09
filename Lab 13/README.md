# Lab 13 — Symbol Table Manager

**Compiler Construction · Spring 2026**

---

## Project Structure

```
Lab 13/
├── src/
│   ├── symbol_table.py      # Tasks 1, 2, 4 — hash table, scope manager, pretty-print
│   └── pascal_parser.py     # Task 3 — parser integrated with symbol table
├── test/
│   ├── test1_valid_arith.pas
│   ├── test2_valid_control.pas
│   ├── test3_dup_decl.pas
│   ├── test4_undecl_id.pas
│   └── test5_multi_errors.pas
├── docs/
│   └── report.md                # Task 5 — test report
└── README.md                # this file
```

---

## Requirements

- **Python 3.9+** (uses `list[...]` type hints)
- No third-party packages required — only the Python standard library.

---

## Running the Code

### Run standalone symbol table unit tests (Tasks 1 & 2)

```bash
python src/symbol_table.py
```

This exercises:

- 10 inserts across three scopes
- 5 lookups (including cross-scope and misses)
- 3 deletes
- Duplicate declaration detection
- Pretty-printed scope dumps on `endScope`

### Run the integrated Pascal parser (Task 3 + built-in tests)

```bash
python src/pascal_parser.py
```

Runs seven built-in test cases (valid and invalid programs) and prints
the symbol-table trace and scope dumps for each.

### Parse a specific `.pas` file

```bash
python src/pascal_parser.py test/test1_valid_arith.pas
```

Enable verbose parse-trace output with `--verbose` or `-v`:

```bash
python src/pascal_parser.py test/test3_dup_decl.pas --verbose
```

### Run all `.pas` test files

```bash
for f in test/*.pas; do python src/pascal_parser.py "$f"; done
```

---

## What Each Source File Does

### `src/symbol_table.py`

| Component                               | Task | Description                                              |
| --------------------------------------- | ---- | -------------------------------------------------------- |
| `_hash(name)`                           | 1    | djb2 hash function, returns index in `[0, 211)`          |
| `Entry`                                 | 1    | Linked-list node: `name, kind, type_, scope_level, line` |
| `HashTable`                             | 1    | Fixed-size array of 211 slots, separate chaining         |
| `HashTable.insert`                      | 1    | Add entry; reject duplicate in current scope             |
| `HashTable.lookup_current`              | 1    | Search only this scope's table                           |
| `HashTable.delete`                      | 1    | Remove entry from this scope                             |
| `HashTable.print_table`                 | 1    | Debug dump of all entries                                |
| `SymbolTableManager`                    | 2    | Stack of `HashTable` objects                             |
| `SymbolTableManager.begin_scope`        | 2    | Push new empty table                                     |
| `SymbolTableManager.end_scope`          | 2    | Pop + pretty-print                                       |
| `SymbolTableManager.lookup`             | 2    | Search current → parent scopes                           |
| `SymbolTableManager.pretty_print_scope` | 4    | ASCII-table output                                       |

### `src/pascal_parser.py`

Extends the Lab-9 recursive-descent parser with symbol-table calls:

| Parser point                | Symbol-table action                                     |
| --------------------------- | ------------------------------------------------------- |
| `program id ;`              | `insert(id, KIND_FUNC, TYPE_INT, line)` in global scope |
| `var id : type`             | `insert(id, kind, type, line)` — error on duplicate     |
| `id := expr` (LHS)          | `lookup(id)` — error if undeclared                      |
| `factor → id` (RHS)         | `lookup(id)` — error if undeclared                      |
| Enter `parse_program` block | `begin_scope()`                                         |
| Exit `parse_program` block  | `end_scope()`                                           |

---

## Errors Detected

| Error                 | Message format                                          | Example                                                     |
| --------------------- | ------------------------------------------------------- | ----------------------------------------------------------- |
| Duplicate declaration | `ERROR line N: duplicate declaration 'X' in this scope` | `ERROR line 7: duplicate declaration 'count' in this scope` |
| Undeclared identifier | `ERROR line N: undeclared identifier 'X'`               | `ERROR line 9: undeclared identifier 'ghost'`               |

---

## Design Decisions

1. **djb2 hash** with prime table size 211 for low collision probability.
2. **Design A (stack of tables)**: one `HashTable` per scope, linked via `parent`
   pointers. Easy to print per-scope dumps on `endScope`.
3. **Separate chaining**: each slot is the head of a singly-linked `Entry` list.
4. **Line-number tracking in the lexer**: the tokenizer tags every token with its
   source line number, enabling precise error messages.
5. **Parser error recovery**: single-token panic mode; parsing continues after
   an error to report further diagnostics in the same run.
