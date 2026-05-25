"""
op_prec_table.py
================
Builds and displays the Operator Precedence Table for the Pascal expression
grammar defined in leading_trailing.py.

The four production-based rules (lab manual §3.4) plus boundary rules are
applied automatically from LEADING / TRAILING.

Relation codes:
    '<.'  —  yields precedence (shift)
    '=.'  —  same precedence   (shift)
    '.>'  —  takes precedence  (reduce)
    'acc' —  accept
    None  —  error
"""

from leading_trailing import (
    GRAMMAR, NON_TERMINALS, START,
    is_terminal, compute_leading, compute_trailing,
)

# ---------------------------------------------------------------------------
# Terminal display order
# ---------------------------------------------------------------------------
TERM_ORDER = ['relop', 'addop', 'mulop', '(', ')', 'id', '$']


def all_terminals(grammar: dict) -> list:
    terms = set()
    for prods in grammar.values():
        for prod in prods:
            for sym in prod:
                if is_terminal(sym):
                    terms.add(sym)
    terms.add('$')
    return [t for t in TERM_ORDER if t in terms]


# ---------------------------------------------------------------------------
# Table builder
# ---------------------------------------------------------------------------

def build_table(grammar: dict, leading: dict, trailing: dict,
                start: str = 'E') -> tuple[dict, list]:
    """
    Returns (table, terminals_list).
    table[a][b] is one of '<.', '=.', '.>', 'acc', or None (error).
    """
    terminals = all_terminals(grammar)
    table = {a: {b: None for b in terminals} for a in terminals}
    conflicts = []

    def set_rel(a: str, b: str, rel: str):
        existing = table[a][b]
        if existing is not None and existing != rel:
            conflicts.append(f"  CONFLICT ({a}, {b}): {existing!r} vs {rel!r}")
        else:
            table[a][b] = rel

    # --- Production-based rules ---
    for A, productions in grammar.items():
        for prod in productions:
            for i, xi in enumerate(prod):
                if i + 1 >= len(prod):
                    continue
                xi1 = prod[i + 1]

                # Rule 15: Xi and Xi+1 both terminal => Xi =. Xi+1
                if is_terminal(xi) and is_terminal(xi1):
                    set_rel(xi, xi1, '=.')

                # Rule 17: Xi terminal, Xi+1 non-terminal => Xi <. b  ∀b ∈ LEADING(Xi+1)
                if is_terminal(xi) and not is_terminal(xi1):
                    for b in leading[xi1]:
                        set_rel(xi, b, '<.')

                # Rule 18: Xi non-terminal, Xi+1 terminal => a .> Xi+1  ∀a ∈ TRAILING(Xi)
                if not is_terminal(xi) and is_terminal(xi1):
                    for a in trailing[xi]:
                        set_rel(a, xi1, '.>')

                # Rule 16: Xi-1 and Xi+1 both terminal, Xi non-terminal => Xi-1 =. Xi+1
                if i > 0:
                    xi_prev = prod[i - 1]
                    if not is_terminal(xi) and is_terminal(xi_prev) and is_terminal(xi1):
                        set_rel(xi_prev, xi1, '=.')

    # --- Boundary rules ---
    for b in leading[start]:
        set_rel('$', b, '<.')
    for a in trailing[start]:
        set_rel(a, '$', '.>')
    table['$']['$'] = 'acc'

    return table, terminals, conflicts


# ---------------------------------------------------------------------------
# Pretty-print
# ---------------------------------------------------------------------------

REL_DISPLAY = {'<.': '<.', '=.': '=.', '.>': '.>', 'acc': 'acc', None: ''}

def print_table(table: dict, terminals: list) -> None:
    col = 6
    header = f"{'':>{col}}" + "".join(f"{t:>{col}}" for t in terminals)
    sep    = "-" * len(header)
    print("\n" + "=" * len(header))
    print("  Operator Precedence Table  —  Pascal Expression Grammar")
    print("=" * len(header))
    print(header)
    print(sep)
    for row in terminals:
        line = f"{row:>{col}}"
        for col_t in terminals:
            cell = REL_DISPLAY.get(table[row][col_t], '')
            line += f"{cell:>{col}}"
        print(line)
    print("=" * len(header) + "\n")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

if __name__ == '__main__':
    leading  = compute_leading(GRAMMAR)
    trailing = compute_trailing(GRAMMAR)
    [table, terminals], conflicts = build_table(GRAMMAR, leading, trailing, START)

    if conflicts:
        print("\n[!] Grammar is NOT operator-precedence — conflicts detected:")
        for c in conflicts:
            print(c)
    else:
        print("\n[✓] No conflicts — grammar is a valid operator-precedence grammar.")

    print_table(table, terminals)
