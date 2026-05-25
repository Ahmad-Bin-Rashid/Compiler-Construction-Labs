"""
leading_trailing.py
===================
Computes LEADING and TRAILING sets for the Pascal expression operator grammar.

Grammar (operator grammar — no epsilon, no adjacent non-terminals):
    E  ->  E relop R  |  R
    R  ->  R addop T  |  T
    T  ->  T mulop F  |  F
    F  ->  ( E )      |  id

Terminal categories:
    relop :  =  <>  <  >  <=  >=
    addop :  +  -  or  xor
    mulop :  *  /  div  mod  and  shl  shr
    (  )  id
"""

# ---------------------------------------------------------------------------
# Grammar definition
# ---------------------------------------------------------------------------

# Productions: { NonTerminal: [ [sym, sym, ...], ... ] }
# Upper-case = non-terminal, lower-case/special = terminal
GRAMMAR = {
    'E': [['E', 'relop', 'R'], ['R']],
    'R': [['R', 'addop', 'T'], ['T']],
    'T': [['T', 'mulop', 'F'], ['F']],
    'F': [['(', 'E', ')'],     ['id']],
}

NON_TERMINALS = set(GRAMMAR.keys())
START = 'E'


def is_terminal(sym: str) -> bool:
    return sym not in NON_TERMINALS


# ---------------------------------------------------------------------------
# LEADING  (Section 3.4, Rules 1-3 of the lab manual)
# ---------------------------------------------------------------------------

def compute_leading(grammar: dict) -> dict:
    """
    LEADING(A) = set of terminals t such that A =>* t... or A =>* B t...
    Rules applied to the FIRST (and optionally second) symbol of each production:
      R1: A -> a ...       => a in LEADING(A)
      R2: A -> B a ...     => a in LEADING(A)
      R3: A -> B ...       => LEADING(B) ⊆ LEADING(A)
    """
    leading = {nt: set() for nt in grammar}
    changed = True
    while changed:
        changed = False
        for A, productions in grammar.items():
            for prod in productions:
                s0 = prod[0]
                if is_terminal(s0):                    # R1
                    if s0 not in leading[A]:
                        leading[A].add(s0); changed = True
                else:                                   # s0 is non-terminal
                    for t in leading[s0]:              # R3
                        if t not in leading[A]:
                            leading[A].add(t); changed = True
                    if len(prod) > 1 and is_terminal(prod[1]):  # R2
                        t = prod[1]
                        if t not in leading[A]:
                            leading[A].add(t); changed = True
    return leading


# ---------------------------------------------------------------------------
# TRAILING  (Section 3.4, Rules 1-3 of the lab manual, mirror of LEADING)
# ---------------------------------------------------------------------------

def compute_trailing(grammar: dict) -> dict:
    """
    TRAILING(A) = set of terminals t such that A =>* ...t or A =>* ...t B
    Rules applied to the LAST (and optionally second-last) symbol of each production:
      R1: A -> ... a       => a in TRAILING(A)
      R2: A -> ... a B     => a in TRAILING(A)
      R3: A -> ... B       => TRAILING(B) ⊆ TRAILING(A)
    """
    trailing = {nt: set() for nt in grammar}
    changed = True
    while changed:
        changed = False
        for A, productions in grammar.items():
            for prod in productions:
                s_last = prod[-1]
                if is_terminal(s_last):                # R1
                    if s_last not in trailing[A]:
                        trailing[A].add(s_last); changed = True
                else:                                  # s_last is non-terminal
                    for t in trailing[s_last]:         # R3
                        if t not in trailing[A]:
                            trailing[A].add(t); changed = True
                    if len(prod) > 1 and is_terminal(prod[-2]):  # R2
                        t = prod[-2]
                        if t not in trailing[A]:
                            trailing[A].add(t); changed = True
    return trailing


# ---------------------------------------------------------------------------
# Pretty-print helper
# ---------------------------------------------------------------------------

def _fmt(s: set) -> str:
    order = ['relop', 'addop', 'mulop', '(', ')', 'id', '$']
    ordered = [x for x in order if x in s] + sorted(s - set(order))
    return '{' + ', '.join(ordered) + '}'


def print_sets(leading: dict, trailing: dict) -> None:
    nts = ['E', 'R', 'T', 'F']
    col = 14
    print("\n" + "=" * 60)
    print("  LEADING and TRAILING Sets  —  Pascal Expression Grammar")
    print("=" * 60)
    print(f"{'Non-Terminal':<{col}}  {'LEADING':<30}  TRAILING")
    print("-" * 60)
    for nt in nts:
        print(f"{nt:<{col}}  {_fmt(leading[nt]):<30}  {_fmt(trailing[nt])}")
    print("=" * 60 + "\n")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

if __name__ == '__main__':
    leading  = compute_leading(GRAMMAR)
    trailing = compute_trailing(GRAMMAR)
    print_sets(leading, trailing)
