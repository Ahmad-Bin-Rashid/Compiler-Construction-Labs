"""
op_prec_parser.py
=================
Operator Precedence Parser for Pascal expression grammar (lab manual §3.6).

Grammar:
    E  ->  E relop R  |  R
    R  ->  R addop T  |  T
    T  ->  T mulop F  |  F
    F  ->  ( E )      |  id

Token categories (Pascal):
    relop :  =  <>  <  >  <=  >=
    addop :  +  -  or  xor
    mulop :  *  /  div  mod  and  shl  shr
    id    :  identifiers, integer literals, real literals

Usage:
    python op_prec_parser.py                         # interactive mode
    python op_prec_parser.py "a + b * c"             # expression as argument
    python op_prec_parser.py "x = y + 1" "a * b"    # multiple expressions
"""

import sys
import re

from leading_trailing import GRAMMAR, START, is_terminal, compute_leading, compute_trailing
from op_prec_table   import build_table, all_terminals

# ---------------------------------------------------------------------------
# Tokeniser
# ---------------------------------------------------------------------------

# Pascal token patterns (order matters — longer tokens first)
_TOKEN_PATTERNS = [
    (r'<>|<=|>=|<|>|=',        'relop'),
    (r'\+|-(?!\d)|or\b|xor\b', 'addop'),
    (r'\*|/|div\b|mod\b|and\b|shl\b|shr\b', 'mulop'),
    (r'\(',                     '('),
    (r'\)',                     ')'),
    (r'[A-Za-z_][A-Za-z0-9_]*', 'id'),   # identifier (catches keywords already matched)
    (r'\d+(\.\d+)?',            'id'),   # numeric literal → treated as id
]

_MASTER_RE = re.compile(
    '|'.join(f'(?P<t{i}>{pat})' for i, (pat, _) in enumerate(_TOKEN_PATTERNS)),
    re.IGNORECASE,
)
_CAT = {f't{i}': cat for i, (_, cat) in enumerate(_TOKEN_PATTERNS)}


def tokenise(expr: str) -> list[str]:
    """Convert a Pascal expression string into a list of terminal category tokens."""
    tokens = []
    pos = 0
    expr = expr.strip()
    while pos < len(expr):
        if expr[pos].isspace():
            pos += 1
            continue
        m = _MASTER_RE.match(expr, pos)
        if m is None:
            raise ValueError(f"Unrecognised token at position {pos}: '{expr[pos:]}'")
        group = m.lastgroup
        cat   = _CAT[group]
        tokens.append(cat)
        pos = m.end()
    tokens.append('$')
    return tokens


# ---------------------------------------------------------------------------
# Parser driver  (lab manual §3.6)
# ---------------------------------------------------------------------------

def parse(tokens: list[str], table: dict, terminals: set,
          verbose: bool = True) -> bool:
    """
    Operator precedence parsing algorithm.
    Returns True on ACCEPT, False on ERROR.
    """
    stack = ['$']
    ip    = 0

    def top_term():
        for s in reversed(stack):
            if s in terminals:
                return s
        return None

    def stack_str():
        return ' '.join(stack)

    def input_str():
        return ' '.join(tokens[ip:])

    if verbose:
        w = 32
        print(f"\n{'STACK':<{w}} {'INPUT':<{w}} {'REL':<6}  ACTION")
        print('-' * (w * 2 + 20))

    while True:
        a   = top_term()
        b   = tokens[ip]
        rel = table.get(a, {}).get(b) if a else None

        if rel == 'acc':
            if verbose:
                print(f"{stack_str():<{w}} {input_str():<{w}} {'$=$':<6}  ACCEPT")
            return True

        if rel is None:
            if verbose:
                print(f"{stack_str():<{w}} {input_str():<{w}} {'ERR':<6}  ERROR — no relation for ({a}, {b})")
            return False

        if rel in ('<.', '=.'):
            if verbose:
                print(f"{stack_str():<{w}} {input_str():<{w}} {rel:<6}  Shift  {b}")
            stack.append(b)
            ip += 1

        else:  # rel == '.>' — REDUCE
            # Pop until topmost terminal on stack has <. relation
            # to the terminal most recently popped from the stack.
            handle_terms = []
            while True:
                # Pop one symbol
                sym = stack.pop()
                if sym in terminals:
                    handle_terms.append(sym)
                    last_popped = sym
                    new_top = top_term()
                    # Stop when new top terminal is <. to the last popped terminal
                    if new_top is None or table.get(new_top, {}).get(last_popped) == '<.':
                        break
            handle_str = ' '.join(reversed(handle_terms)) if handle_terms else '?'
            if verbose:
                print(f"{stack_str():<{w}} {input_str():<{w}} {rel:<6}  Reduce ({handle_str}) → E")
            stack.append('E')   # generic non-terminal


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def _banner():
    print("╔══════════════════════════════════════════════════════════╗")
    print("║   Pascal Operator Precedence Parser                      ║")
    print("╚══════════════════════════════════════════════════════════╝")
    print("  Grammar: E -> E relop R | R -> R addop T | T -> T mulop F | F -> (E)|id")
    print("  Terminals: relop  addop  mulop  (  )  id\n")


def main():
    leading  = compute_leading(GRAMMAR)
    trailing = compute_trailing(GRAMMAR)
    table, term_list, conflicts = build_table(GRAMMAR, leading, trailing, START)
    term_set = set(term_list)

    _banner()

    if conflicts:
        print("[!] Conflicts in precedence table:")
        for c in conflicts:
            print(c)
        print()

    exprs = sys.argv[1:] if len(sys.argv) > 1 else None

    if exprs:
        for expr in exprs:
            print(f"\n┌─ Input: {expr!r}")
            try:
                tokens = tokenise(expr)
                print(f"│  Tokens: {' '.join(tokens)}")
                result = parse(tokens, table, term_set)
                print(f"└─ Result: {'✓ ACCEPT' if result else '✗ ERROR'}\n")
            except ValueError as e:
                print(f"│  Tokeniser error: {e}")
                print("└─ Result: ✗ ERROR\n")
    else:
        # Interactive mode
        print("Enter a Pascal expression (or 'quit' to exit):")
        while True:
            try:
                expr = input("  > ").strip()
            except EOFError:
                break
            if expr.lower() in ('quit', 'exit', 'q'):
                break
            if not expr:
                continue
            try:
                tokens = tokenise(expr)
                print(f"  Tokens: {' '.join(tokens)}")
                result = parse(tokens, table, term_set)
                print(f"  Result: {'✓ ACCEPT' if result else '✗ ERROR'}\n")
            except ValueError as e:
                print(f"  Tokeniser error: {e}\n")


if __name__ == '__main__':
    main()
