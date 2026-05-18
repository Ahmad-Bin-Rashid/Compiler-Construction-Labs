# Lab 9 — Recursive Descent Parser for Pascal

**Compiler Construction · Spring 2026**

---

## Original Grammar

```
<program>      → program id ; <block> .
<block>        → <var_decl> <stmt_block>
<var_decl>     → var <decl_list> | ε
<decl_list>    → <decl> ; <decl_list> | <decl>
<decl>         → id : <type>
<type>         → integer | real
<stmt_block>   → begin <stmt_list> end
<stmt_list>    → <stmt> ; <stmt_list> | <stmt>
<stmt>         → <assign_stmt> | <if_stmt> | <while_stmt>
<assign_stmt>  → id := <expr>
<if_stmt>      → if <expr> then <stmt> else <stmt>
<while_stmt>   → while <expr> do <stmt>
<expr>         → <expr> + <term> | <expr> - <term> | <term>
<term>         → <term> * <factor> | <term> / <factor> | <factor>
<factor>       → ( <expr> ) | id | number
```

---

## Step 1 — Left-Recursion Removal

Only `<expr>` and `<term>` are directly left-recursive.

**Technique:** For `A → A α | β` replace with `A → β A'` and `A' → α A' | ε`

| Before                                                        | After                                                     |
| ------------------------------------------------------------- | --------------------------------------------------------- |
| `<expr> → <expr> + <term> \| <expr> - <term> \| <term>`       | `<expr>  → <term> <expr'>`                                |
|                                                               | `<expr'> → + <term> <expr'> \| - <term> <expr'> \| ε`     |
| `<term> → <term> * <factor> \| <term> / <factor> \| <factor>` | `<term>  → <factor> <term'>`                              |
|                                                               | `<term'> → * <factor> <term'> \| / <factor> <term'> \| ε` |

---

## Step 2 — Left Factoring

`<decl_list>` and `<stmt_list>` share a common prefix (`<decl>` / `<stmt>`) followed by an optional `; …`.

**Technique:** Factor the common prefix; introduce a tail non-terminal.

| Before                                         | After                              |
| ---------------------------------------------- | ---------------------------------- |
| `<decl_list> → <decl> ; <decl_list> \| <decl>` | `<decl_list> → <decl> <decl_rest>` |
|                                                | `<decl_rest> → ; <decl_list> \| ε` |
| `<stmt_list> → <stmt> ; <stmt_list> \| <stmt>` | `<stmt_list> → <stmt> <stmt_rest>` |
|                                                | `<stmt_rest> → ; <stmt_list> \| ε` |

### Final LL(1) Grammar

```
<program>      → program id ; <block> .
<block>        → <var_decl> <stmt_block>
<var_decl>     → var <decl_list> | ε
<decl_list>    → <decl> <decl_rest>
<decl_rest>    → ; <decl_list> | ε
<decl>         → id : <type>
<type>         → integer | real
<stmt_block>   → begin <stmt_list> end
<stmt_list>    → <stmt> <stmt_rest>
<stmt_rest>    → ; <stmt_list> | ε
<stmt>         → <assign_stmt> | <if_stmt> | <while_stmt>
<assign_stmt>  → id := <expr>
<if_stmt>      → if <expr> then <stmt> else <stmt>
<while_stmt>   → while <expr> do <stmt>
<expr>         → <term> <expr'>
<expr'>        → + <term> <expr'> | - <term> <expr'> | ε
<term>         → <factor> <term'>
<term'>        → * <factor> <term'> | / <factor> <term'> | ε
<factor>       → ( <expr> ) | id | number
```

---

## Step 3 — FIRST and FOLLOW Sets

> **FIRST(α):** terminals that can begin a string derived from α (ε included if α ⇒\* ε).  
> **FOLLOW(A):** terminals that can appear immediately to the right of A in any sentential form.

| Non-Terminal    | FIRST               | FOLLOW                                      |
| --------------- | ------------------- | ------------------------------------------- |
| `<program>`     | `{ program }`       | `{ $ }`                                     |
| `<block>`       | `{ var, begin }`    | `{ . }`                                     |
| `<var_decl>`    | `{ var, ε }`        | `{ begin }`                                 |
| `<decl_list>`   | `{ id }`            | `{ begin }`                                 |
| `<decl_rest>`   | `{ ;, ε }`          | `{ begin }`                                 |
| `<decl>`        | `{ id }`            | `{ ;, begin }`                              |
| `<type>`        | `{ integer, real }` | `{ ;, begin }`                              |
| `<stmt_block>`  | `{ begin }`         | `{ . }`                                     |
| `<stmt_list>`   | `{ id, if, while }` | `{ end }`                                   |
| `<stmt_rest>`   | `{ ;, ε }`          | `{ end }`                                   |
| `<stmt>`        | `{ id, if, while }` | `{ ;, end, else }`                          |
| `<assign_stmt>` | `{ id }`            | `{ ;, end, else }`                          |
| `<if_stmt>`     | `{ if }`            | `{ ;, end, else }`                          |
| `<while_stmt>`  | `{ while }`         | `{ ;, end, else }`                          |
| `<expr>`        | `{ (, id, number }` | `{ then, else, do, ;, end, ) }`             |
| `<expr'>`       | `{ +, -, ε }`       | `{ then, else, do, ;, end, ) }`             |
| `<term>`        | `{ (, id, number }` | `{ +, -, then, else, do, ;, end, ) }`       |
| `<term'>`       | `{ *, /, ε }`       | `{ +, -, then, else, do, ;, end, ) }`       |
| `<factor>`      | `{ (, id, number }` | `{ *, /, +, -, then, else, do, ;, end, ) }` |

---

## Step 4 — LL(1) Predictive Parsing Table

> **Rule:** For A → α: add A → α to M[A, a] for each a ∈ FIRST(α).  
> If ε ∈ FIRST(α): add A → α to M[A, b] for each b ∈ FOLLOW(A).

| NT \ Terminal   | `program`                  | `id`                   | `var`                       | `begin`                     | `end` | `integer`   | `real`   | `if`                                  | `then` | `else` | `while`                    | `do` | `;`               | `.` | `(`                  | `)` | `+`                  | `-`                  | `*`                    | `/`                    | `number`             |
| --------------- | -------------------------- | ---------------------- | --------------------------- | --------------------------- | ----- | ----------- | -------- | ------------------------------------- | ------ | ------ | -------------------------- | ---- | ----------------- | --- | -------------------- | --- | -------------------- | -------------------- | ---------------------- | ---------------------- | -------------------- |
| `<program>`     | → `program id ; <block> .` |                        |                             |                             |       |             |          |                                       |        |        |                            |      |                   |     |                      |     |                      |                      |                        |                        |                      |
| `<block>`       |                            |                        | → `<var_decl> <stmt_block>` | → `<var_decl> <stmt_block>` |       |             |          |                                       |        |        |                            |      |                   |     |                      |     |                      |                      |                        |                        |                      |
| `<var_decl>`    |                            |                        | → `var <decl_list>`         | → ε                         |       |             |          |                                       |        |        |                            |      |                   |     |                      |     |                      |                      |                        |                        |                      |
| `<decl_list>`   |                            | → `<decl> <decl_rest>` |                             |                             |       |             |          |                                       |        |        |                            |      |                   |     |                      |     |                      |                      |                        |                        |                      |
| `<decl_rest>`   |                            |                        |                             | → ε                         |       |             |          |                                       |        |        |                            |      | → `; <decl_list>` |     |                      |     |                      |                      |                        |                        |                      |
| `<decl>`        |                            | → `id : <type>`        |                             |                             |       |             |          |                                       |        |        |                            |      |                   |     |                      |     |                      |                      |                        |                        |                      |
| `<type>`        |                            |                        |                             |                             |       | → `integer` | → `real` |                                       |        |        |                            |      |                   |     |                      |     |                      |                      |                        |                        |                      |
| `<stmt_block>`  |                            |                        |                             | → `begin <stmt_list> end`   |       |             |          |                                       |        |        |                            |      |                   |     |                      |     |                      |                      |                        |                        |                      |
| `<stmt_list>`   |                            | → `<stmt> <stmt_rest>` |                             |                             |       |             |          | → `<stmt> <stmt_rest>`                |        |        | → `<stmt> <stmt_rest>`     |      |                   |     |                      |     |                      |                      |                        |                        |                      |
| `<stmt_rest>`   |                            |                        |                             |                             | → ε   |             |          |                                       |        |        |                            |      | → `; <stmt_list>` |     |                      |     |                      |                      |                        |                        |                      |
| `<stmt>`        |                            | → `<assign_stmt>`      |                             |                             |       |             |          | → `<if_stmt>`                         |        |        | → `<while_stmt>`           |      |                   |     |                      |     |                      |                      |                        |                        |                      |
| `<assign_stmt>` |                            | → `id := <expr>`       |                             |                             |       |             |          |                                       |        |        |                            |      |                   |     |                      |     |                      |                      |                        |                        |                      |
| `<if_stmt>`     |                            |                        |                             |                             |       |             |          | → `if <expr> then <stmt> else <stmt>` |        |        |                            |      |                   |     |                      |     |                      |                      |                        |                        |                      |
| `<while_stmt>`  |                            |                        |                             |                             |       |             |          |                                       |        |        | → `while <expr> do <stmt>` |      |                   |     |                      |     |                      |                      |                        |                        |                      |
| `<expr>`        |                            | → `<term> <expr'>`     |                             |                             |       |             |          |                                       |        |        |                            |      |                   |     | → `<term> <expr'>`   |     |                      |                      |                        |                        | → `<term> <expr'>`   |
| `<expr'>`       |                            |                        |                             |                             | → ε   |             |          |                                       | → ε    | → ε    |                            | → ε  | → ε               |     |                      | → ε | → `+ <term> <expr'>` | → `- <term> <expr'>` |                        |                        |                      |
| `<term>`        |                            | → `<factor> <term'>`   |                             |                             |       |             |          |                                       |        |        |                            |      |                   |     | → `<factor> <term'>` |     |                      |                      |                        |                        | → `<factor> <term'>` |
| `<term'>`       |                            |                        |                             |                             | → ε   |             |          |                                       | → ε    | → ε    |                            | → ε  | → ε               |     |                      | → ε | → ε                  | → ε                  | → `* <factor> <term'>` | → `/ <factor> <term'>` |                      |
| `<factor>`      |                            | → `id`                 |                             |                             |       |             |          |                                       |        |        |                            |      |                   |     | → `( <expr> )`       |     |                      |                      |                        |                        | → `number`           |

> No cell has more than one entry — the grammar is **LL(1)**. A recursive descent parser can be coded directly.

---

## How to Run

```bash
python recursive_descent_parser.py
```

See [`recursive_descent_parser.py`](./recursive_descent_parser.py)
