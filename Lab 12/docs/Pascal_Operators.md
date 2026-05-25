# Operator Precedence / Relation Table for Pascal Operators

## Operator Precedence Table

Higher precedence operators are evaluated first.

| Precedence Level | Operators                       | Associativity |
| ---------------- | ------------------------------- | ------------- |
| 1 (Highest)      | `( )`                           | Left to Right |
| 2                | `not`                           | Right to Left |
| 3                | `*`, `/`, `div`, `mod`, `and`   | Left to Right |
| 4                | `+`, `-`, `or`                  | Left to Right |
| 5                | `=`, `<>`, `<`, `<=`, `>`, `>=` | Left to Right |
| 6 (Lowest)       | `:=`                            | Right to Left |

---

# Operator Relation Table

Legend:

* `<` → lower precedence
* `>` → higher precedence
* `=` → same precedence

| Operators                       | Relation                      |
| ------------------------------- | ----------------------------- |
| `( )` > all                     | Highest precedence            |
| `not` > `* / div mod and`       | `not` evaluated first         |
| `* / div mod and` > `+ - or`    | Multiplication level higher   |
| `+ - or` > relational operators | Addition level higher         |
| relational operators > `:=`     | Comparisons before assignment |
| `* = / = div = mod = and`       | Same precedence               |
| `+ = - = or`                    | Same precedence               |
| `= = <> = < = <= = > = >=`      | Same precedence               |

---

# Compact Precedence Form

```text
( )

not

*   /   div   mod   and

+   -   or

=   <>   <   <=   >   >=

:=
```

---

# Example

```pascal
x := a + b * c >= d
```

Evaluation order:

1. `b * c`
2. `a + (b * c)`
3. `(a + b * c) >= d`
4. `x := result`


# Pascal Operator Precedence Relation Table

```
Legend:
<.  → yields precedence
.>  → takes precedence
=.  → equal precedence
acc → accept
```

|     | +  | -  | *  | /  | div | mod | and | or | not | =  | <> | <  | <= | >  | >= | := | (  | )  | id | $   |
| --- | -- | -- | -- | -- | --- | --- | --- | -- | --- | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- | --- |
| +   | .> | .> | <. | <. | <.  | <.  | <.  | .> | <.  | .> | .> | .> | .> | .> | .> | .> | <. | .> | <. | .>  |
| -   | .> | .> | <. | <. | <.  | <.  | <.  | .> | <.  | .> | .> | .> | .> | .> | .> | .> | <. | .> | <. | .>  |
| *   | .> | .> | .> | .> | .>  | .>  | .>  | .> | <.  | .> | .> | .> | .> | .> | .> | .> | <. | .> | <. | .>  |
| /   | .> | .> | .> | .> | .>  | .>  | .>  | .> | <.  | .> | .> | .> | .> | .> | .> | .> | <. | .> | <. | .>  |
| div | .> | .> | .> | .> | .>  | .>  | .>  | .> | <.  | .> | .> | .> | .> | .> | .> | .> | <. | .> | <. | .>  |
| mod | .> | .> | .> | .> | .>  | .>  | .>  | .> | <.  | .> | .> | .> | .> | .> | .> | .> | <. | .> | <. | .>  |
| and | .> | .> | .> | .> | .>  | .>  | .>  | .> | <.  | .> | .> | .> | .> | .> | .> | .> | <. | .> | <. | .>  |
| or  | <. | <. | <. | <. | <.  | <.  | <.  | .> | <.  | .> | .> | .> | .> | .> | .> | .> | <. | .> | <. | .>  |
| not | <. | <. | <. | <. | <.  | <.  | <.  | <. | <.  | <. | <. | <. | <. | <. | <. | <. | <. | .> | <. | .>  |
| =   | <. | <. | <. | <. | <.  | <.  | <.  | <. | <.  | .> | .> | .> | .> | .> | .> | .> | <. | .> | <. | .>  |
| <>  | <. | <. | <. | <. | <.  | <.  | <.  | <. | <.  | .> | .> | .> | .> | .> | .> | .> | <. | .> | <. | .>  |
| <   | <. | <. | <. | <. | <.  | <.  | <.  | <. | <.  | .> | .> | .> | .> | .> | .> | .> | <. | .> | <. | .>  |
| <=  | <. | <. | <. | <. | <.  | <.  | <.  | <. | <.  | .> | .> | .> | .> | .> | .> | .> | <. | .> | <. | .>  |
| >   | <. | <. | <. | <. | <.  | <.  | <.  | <. | <.  | .> | .> | .> | .> | .> | .> | .> | <. | .> | <. | .>  |
| >=  | <. | <. | <. | <. | <.  | <.  | <.  | <. | <.  | .> | .> | .> | .> | .> | .> | .> | <. | .> | <. | .>  |
| :=  | <. | <. | <. | <. | <.  | <.  | <.  | <. | <.  | <. | <. | <. | <. | <. | <. | .> | <. | .> | <. | .>  |
| (   | <. | <. | <. | <. | <.  | <.  | <.  | <. | <.  | <. | <. | <. | <. | <. | <. | <. | <. | =. | <. |     |
| )   | .> | .> | .> | .> | .>  | .>  | .>  | .> |     | .> | .> | .> | .> | .> | .> | .> |    | .> |    | .>  |
| id  | .> | .> | .> | .> | .>  | .>  | .>  | .> |     | .> | .> | .> | .> | .> | .> | .> |    | .> |    | .>  |
| $   | <. | <. | <. | <. | <.  | <.  | <.  | <. | <.  | <. | <. | <. | <. | <. | <. | <. | <. |    | <. | acc |

```
```
