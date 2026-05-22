# -*- coding: utf-8 -*-
"""
==============================================================
 LL(1) Non-Recursive Predictive Parser for Pascal - Lab 11
 Compiler Construction - Spring 2026
==============================================================

 This module:
   1. Defines the Pascal grammar (left-recursion-free, left-factored)
   2. Automatically computes FIRST and FOLLOW sets
   3. Constructs the LL(1) predictive parsing table
   4. Runs the stack-driven parsing algorithm with a step-by-step trace
      (identical in format to Table 4.4 in the lab manual)
   5. Includes a lexer so real Pascal-like source code can be tested

 Grammar (eps = epsilon):
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

 Run:  python ll1_parser.py
==============================================================
"""

from __future__ import annotations
import sys
import re
from collections import defaultdict
from typing import Dict, List, Set, Tuple

# Force UTF-8 stdout so the output works correctly on Windows consoles
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

# ==============================================================
# SECTION 1 - GRAMMAR DEFINITION
# ==============================================================

EPS    = "eps"  # represents the empty string (epsilon)
DOLLAR = "$"    # end-of-input marker

# Productions are stored as (lhs: str, rhs: List[str]) tuples.
# Non-terminals are ALL_CAPS; terminals are lowercase keywords or punctuation.

GRAMMAR: List[Tuple[str, List[str]]] = [
    # -- top-level structure
    ("PROGRAM",      ["program", "id", ";", "BLOCK", "."]),
    ("BLOCK",        ["VAR_DECL", "STMT_BLOCK"]),
    ("VAR_DECL",     ["var", "DECL_LIST"]),
    ("VAR_DECL",     [EPS]),
    ("DECL_LIST",    ["DECL", "DECL_REST"]),
    ("DECL_REST",    [";", "DECL_LIST"]),
    ("DECL_REST",    [EPS]),
    ("DECL",         ["id", ":", "TYPE"]),
    ("TYPE",         ["integer"]),
    ("TYPE",         ["real"]),
    # -- statements
    ("STMT_BLOCK",   ["begin", "STMT_LIST", "end"]),
    ("STMT_LIST",    ["STMT", "STMT_REST"]),
    ("STMT_REST",    [";", "STMT_LIST"]),
    ("STMT_REST",    [EPS]),
    ("STMT",         ["ASSIGN_STMT"]),
    ("STMT",         ["IF_STMT"]),
    ("STMT",         ["WHILE_STMT"]),
    ("ASSIGN_STMT",  ["id", ":=", "EXPR"]),
    ("IF_STMT",      ["if", "EXPR", "then", "STMT", "else", "STMT"]),
    ("WHILE_STMT",   ["while", "EXPR", "do", "STMT"]),
    # -- expressions
    ("EXPR",         ["TERM", "EXPRP"]),
    ("EXPRP",        ["+", "TERM", "EXPRP"]),
    ("EXPRP",        ["-", "TERM", "EXPRP"]),
    ("EXPRP",        [EPS]),
    ("TERM",         ["FACTOR", "TERMP"]),
    ("TERMP",        ["*", "FACTOR", "TERMP"]),
    ("TERMP",        ["/", "FACTOR", "TERMP"]),
    ("TERMP",        [EPS]),
    ("FACTOR",       ["(", "EXPR", ")"]),
    ("FACTOR",       ["id"]),
    ("FACTOR",       ["number"]),
]

START_SYMBOL = "PROGRAM"

# Derive non-terminal and terminal sets automatically from the grammar
NON_TERMINALS: Set[str] = {lhs for lhs, _ in GRAMMAR}


def _is_terminal(sym: str) -> bool:
    return sym not in NON_TERMINALS and sym != EPS


TERMINALS: Set[str] = set()
for _, rhs in GRAMMAR:
    for sym in rhs:
        if _is_terminal(sym):
            TERMINALS.add(sym)
TERMINALS.add(DOLLAR)


# ==============================================================
# SECTION 2 - FIRST SET COMPUTATION
# ==============================================================

def compute_first(grammar: List[Tuple[str, List[str]]]) -> Dict[str, Set[str]]:
    """
    Compute FIRST sets for all grammar symbols using the iterative
    fixed-point algorithm from Section 3.5 of the lab manual.

    FIRST(X) = the set of terminals that can appear as the first symbol
               of any string derivable from X (including eps if X =>* eps).
    """
    first: Dict[str, Set[str]] = defaultdict(set)

    # Base case: FIRST(a) = {a} for every terminal a
    for term in TERMINALS:
        first[term] = {term}
    first[EPS] = {EPS}

    changed = True
    while changed:
        changed = False
        for lhs, rhs in grammar:
            before = len(first[lhs])

            if rhs == [EPS]:
                # X -> eps  =>  add eps to FIRST(X)
                first[lhs].add(EPS)
            else:
                # Walk through each symbol in rhs
                for sym in rhs:
                    # Add FIRST(sym) - {eps} to FIRST(lhs)
                    first[lhs] |= (first[sym] - {EPS})
                    if EPS not in first[sym]:
                        break  # eps does not propagate past this symbol
                else:
                    # All symbols in rhs can derive eps => lhs can too
                    first[lhs].add(EPS)

            if len(first[lhs]) != before:
                changed = True

    return first


def first_of_string(symbols: List[str], first: Dict[str, Set[str]]) -> Set[str]:
    """Return FIRST set of a sequence of grammar symbols."""
    result: Set[str] = set()
    for sym in symbols:
        result |= (first[sym] - {EPS})
        if EPS not in first[sym]:
            break
    else:
        result.add(EPS)
    return result


# ==============================================================
# SECTION 3 - FOLLOW SET COMPUTATION
# ==============================================================

def compute_follow(
    grammar: List[Tuple[str, List[str]]],
    first: Dict[str, Set[str]],
    start: str,
) -> Dict[str, Set[str]]:
    """
    Compute FOLLOW sets for all non-terminals using the iterative
    fixed-point algorithm from Section 3.5 of the lab manual.

    FOLLOW(A) = the set of terminals that can appear immediately to the
                right of A in some sentential form.
    """
    follow: Dict[str, Set[str]] = defaultdict(set)
    follow[start].add(DOLLAR)  # Rule 1: $ is always in FOLLOW(start)

    changed = True
    while changed:
        changed = False
        for lhs, rhs in grammar:
            for i, sym in enumerate(rhs):
                if sym in NON_TERMINALS:
                    beta = rhs[i + 1:]          # everything after sym
                    before = len(follow[sym])

                    first_beta = first_of_string(beta, first)

                    # Rule 2: add FIRST(beta) - {eps} to FOLLOW(sym)
                    follow[sym] |= (first_beta - {EPS})

                    # Rule 3: if eps in FIRST(beta), add FOLLOW(lhs) to FOLLOW(sym)
                    if EPS in first_beta:
                        follow[sym] |= follow[lhs]

                    if len(follow[sym]) != before:
                        changed = True

    return follow


# ==============================================================
# SECTION 4 - LL(1) PARSING TABLE CONSTRUCTION
# ==============================================================

# ParseTable maps (NonTerminal, Terminal) -> list[production]
# A valid LL(1) grammar has exactly one entry per occupied cell.
ParseTable = Dict[Tuple[str, str], List[Tuple[str, List[str]]]]


def build_parse_table(
    grammar: List[Tuple[str, List[str]]],
    first: Dict[str, Set[str]],
    follow: Dict[str, Set[str]],
) -> ParseTable:
    """
    Construct the LL(1) predictive parsing table M using the algorithm
    from Section 3.6 of the lab manual.

    For each production A -> alpha:
      1. For each terminal a in FIRST(alpha): add A->alpha to M[A, a]
      2. If eps in FIRST(alpha): for each b in FOLLOW(A): add A->alpha to M[A, b]
    """
    table: ParseTable = defaultdict(list)

    for lhs, rhs in grammar:
        first_rhs = first_of_string(rhs, first)

        # Rule 1
        for terminal in first_rhs - {EPS}:
            table[(lhs, terminal)].append((lhs, rhs))

        # Rule 2
        if EPS in first_rhs:
            for terminal in follow[lhs]:
                table[(lhs, terminal)].append((lhs, rhs))

    return table


def check_ll1_conflicts(table: ParseTable) -> List[Tuple[str, str]]:
    """Return (non-terminal, terminal) pairs with more than one production (conflicts)."""
    return [(nt, t) for (nt, t), prods in table.items() if len(prods) > 1]


# ==============================================================
# SECTION 5 - LEXER
# ==============================================================

_TOKEN_RE = re.compile(
    r"(?P<NUMBER>\d+(\.\d+)?)"
    r"|(?P<ASSIGN>:=)"
    r"|(?P<COLON>:)"
    r"|(?P<SEMI>;)"
    r"|(?P<DOT>\.)"
    r"|(?P<LPAREN>\()"
    r"|(?P<RPAREN>\))"
    r"|(?P<PLUS>\+)"
    r"|(?P<MINUS>-)"
    r"|(?P<STAR>\*)"
    r"|(?P<SLASH>/)"
    r"|(?P<ID>[A-Za-z_]\w*)"
    r"|(?P<SKIP>\s+)"
)

_KEYWORDS = {
    "program", "var", "begin", "end", "integer", "real",
    "if", "then", "else", "while", "do",
}

_GROUP_TO_TERMINAL: Dict[str, str] = {
    "ASSIGN": ":=",
    "COLON":  ":",
    "SEMI":   ";",
    "DOT":    ".",
    "LPAREN": "(",
    "RPAREN": ")",
    "PLUS":   "+",
    "MINUS":  "-",
    "STAR":   "*",
    "SLASH":  "/",
}


def tokenize(source: str) -> List[str]:
    """
    Lex a Pascal-like source string and return terminal symbols
    matching the grammar, terminated by '$'.
    """
    tokens: List[str] = []
    for m in _TOKEN_RE.finditer(source):
        kind = m.lastgroup
        val  = m.group()
        if kind == "SKIP":
            continue
        if kind == "ID":
            tokens.append(val if val in _KEYWORDS else "id")
        elif kind == "NUMBER":
            tokens.append("number")
        else:
            tokens.append(_GROUP_TO_TERMINAL[kind])
    tokens.append(DOLLAR)
    return tokens


# ==============================================================
# SECTION 6 - LL(1) TABLE-DRIVEN PARSING ALGORITHM
# ==============================================================

def _rhs_str(rhs: List[str]) -> str:
    """Format the RHS of a production for display."""
    return " ".join(rhs) if rhs != [EPS] else "eps"


def parse(
    tokens: List[str],
    table: ParseTable,
    start: str,
    *,
    verbose: bool = True,
) -> bool:
    """
    Run the non-recursive LL(1) parsing algorithm (Section 3.7).

    The parser maintains an explicit stack (instead of the call stack used
    by a recursive descent parser).  At each step it inspects the top of
    stack X and the current lookahead a and does one of:
      - Match   : X == a  -> pop stack, advance input
      - Expand  : X is NT -> replace with M[X,a] (push RHS in reverse)
      - Accept  : X == a == $
      - Error   : no applicable rule

    Returns True on acceptance, False on error.
    Prints a step-by-step trace when verbose=True.
    """
    # Stack: left element is bottom ($), right element is top (start symbol)
    stack: List[str] = [DOLLAR, start]
    ip = 0   # index into tokens[]

    # Column widths for the trace table
    SW, IW, OW = 38, 34, 30

    def stack_str() -> str:
        return " ".join(stack)

    def input_str() -> str:
        return " ".join(tokens[ip:])

    def print_header() -> None:
        print(f"{'Stack':<{SW}}{'Input':<{IW}}{'Output':<{OW}}Action")
        print("-" * (SW + IW + OW + 12))

    def print_row(output: str, action: str) -> None:
        print(f"{stack_str():<{SW}}{input_str():<{IW}}{output:<{OW}}{action}")

    if verbose:
        print_header()
        print_row("", "Initial")

    while stack:
        X = stack[-1]   # top of stack
        a = tokens[ip]  # current lookahead

        # -- Case 1: Accept
        if X == DOLLAR and a == DOLLAR:
            if verbose:
                print_row("", "*** ACCEPT ***")
            return True

        # -- Case 2: Terminal match
        if _is_terminal(X):
            if X == a:
                stack.pop()
                ip += 1
                if verbose:
                    print_row("", f"Match '{a}'")
            else:
                if verbose:
                    print_row("", f"[ERROR] expected '{X}' but got '{a}'")
                return False

        # -- Case 3: Non-terminal -> consult parsing table
        else:
            productions = table.get((X, a), [])
            if not productions:
                if verbose:
                    print_row("", f"[ERROR] no entry M[{X}, '{a}']")
                return False

            lhs, rhs = productions[0]          # LL(1): at most one entry
            prod_str = f"{lhs} -> {_rhs_str(rhs)}"

            stack.pop()
            if rhs != [EPS]:
                for sym in reversed(rhs):
                    stack.append(sym)

            if verbose:
                print_row(prod_str, "Expand")

    # Stack drained without $ match (should not happen with correct grammar)
    return False


# ==============================================================
# SECTION 7 - DISPLAY HELPERS
# ==============================================================

# Canonical display order for non-terminals
_NT_ORDER = [
    "PROGRAM", "BLOCK", "VAR_DECL", "DECL_LIST", "DECL_REST",
    "DECL", "TYPE", "STMT_BLOCK", "STMT_LIST", "STMT_REST",
    "STMT", "ASSIGN_STMT", "IF_STMT", "WHILE_STMT",
    "EXPR", "EXPRP", "TERM", "TERMP", "FACTOR",
]


def _sorted_nts() -> List[str]:
    return [nt for nt in _NT_ORDER if nt in NON_TERMINALS]


def print_first_follow(
    first: Dict[str, Set[str]],
    follow: Dict[str, Set[str]],
) -> None:
    sep = "=" * 72
    print(f"\n{sep}")
    print("  FIRST and FOLLOW Sets")
    print(sep)
    print(f"  {'Non-Terminal':<18} {'FIRST':<32} FOLLOW")
    print("  " + "-" * 68)
    for nt in _sorted_nts():
        f_str  = "{ " + ", ".join(sorted(first[nt]))  + " }"
        fo_str = "{ " + ", ".join(sorted(follow[nt])) + " }"
        print(f"  {nt:<18} {f_str:<32} {fo_str}")
    print(sep)


def print_parse_table(table: ParseTable) -> None:
    """
    Print the LL(1) parsing table in two complementary formats:

    View A – Grouped Summary
      For each non-terminal, list every distinct production it has and the
      lookahead token(s) that select it.  Easy to read at a glance.

    View B – Compact 2D Grid
      Classical row-per-NT / column-per-terminal grid.  Column widths are
      computed dynamically so nothing overflows.  Cells show only the RHS
      (the NT header already tells you the LHS).
    """
    nts   = _sorted_nts()
    terms = sorted(TERMINALS - {DOLLAR}) + [DOLLAR]

    W = 78   # overall page width

    # ------------------------------------------------------------------
    # View A: Grouped Summary
    # ------------------------------------------------------------------
    print(f"\n{'=' * W}")
    print("  LL(1) PARSING TABLE  —  View A: Grouped by Non-Terminal")
    print(f"{'=' * W}")
    print(f"  Format:  <Non-Terminal>  |  Lookahead(s)  =>  Production")
    print(f"  {'(empty cells = no rule / error entry)'}")
    print(f"{'-' * W}")

    for nt in nts:
        # Collect: production_string -> list of terminals that trigger it
        prod_to_tokens: Dict[str, List[str]] = {}
        for t in terms:
            prods = table.get((nt, t), [])
            if prods:
                lhs, rhs = prods[0]
                key = _rhs_str(rhs)
                prod_to_tokens.setdefault(key, []).append(t)

        if not prod_to_tokens:
            continue  # NT has no table entries (shouldn't happen)

        first_line = True
        for rhs_s, lookaheads in prod_to_tokens.items():
            la_str = "  { " + ",  ".join(lookaheads) + " }"
            prod_str = f"{nt}  ->  {rhs_s}"
            if first_line:
                print(f"  {nt}")
                first_line = False
            # indent lookahead block
            print(f"    Lookahead : {la_str}")
            print(f"    Production: {prod_str}")
            print()

    print(f"{'=' * W}")

    # ------------------------------------------------------------------
    # View B: Compact 2D Grid  (paginated by terminal columns)
    # ------------------------------------------------------------------

    # Compute the exact display width needed for each terminal column
    # (header text OR widest RHS in that column, plus 2 chars padding)
    col_widths: Dict[str, int] = {}
    for t in terms:
        max_w = len(t)
        for nt in nts:
            prods = table.get((nt, t), [])
            if prods:
                _, rhs = prods[0]
                max_w = max(max_w, len(_rhs_str(rhs)))
        col_widths[t] = max_w + 2      # 1 space padding on each side

    nt_col = max(len(nt) for nt in nts) + 2   # width of the NT name column
    MAX_PAGE_W = 120                           # maximum characters per line

    # Split terminals into "pages" so no page exceeds MAX_PAGE_W chars
    pages: List[List[str]] = []
    current_page: List[str] = []
    current_w = nt_col
    for t in terms:
        needed = col_widths[t] + 1      # +1 for the '|' separator
        if current_page and current_w + needed > MAX_PAGE_W:
            pages.append(current_page)
            current_page = [t]
            current_w = nt_col + needed
        else:
            current_page.append(t)
            current_w += needed
    if current_page:
        pages.append(current_page)

    total_pages = len(pages)
    for page_num, page_terms in enumerate(pages, 1):
        page_w = nt_col + sum(col_widths[t] + 1 for t in page_terms)

        title = (
            f"  LL(1) PARSING TABLE  --  2-D Grid  "
            f"(RHS only, page {page_num}/{total_pages})"
        )
        print(f"\n{'=' * page_w}")
        print(title)
        print(f"{'=' * page_w}")

        # Header row
        header = " " * nt_col
        for t in page_terms:
            header += "|" + t.center(col_widths[t])
        print(header)

        # Divider after header
        def _div(page_cols: List[str]) -> str:
            d = "-" * nt_col
            for tc in page_cols:
                d += "+" + "-" * col_widths[tc]
            return d

        print(_div(page_terms))

        # Data rows
        for nt in nts:
            row = nt.ljust(nt_col)
            for t in page_terms:
                prods = table.get((nt, t), [])
                if prods:
                    _, rhs = prods[0]
                    cell = _rhs_str(rhs)
                    if len(prods) > 1:
                        cell += " !"
                else:
                    cell = ""
                row += "|" + cell.center(col_widths[t])
            print(row)
            print(_div(page_terms))

        print(f"{'=' * page_w}")


# ==============================================================
# SECTION 8 - TEST DRIVER
# ==============================================================

def run_test(
    label: str,
    source: str,
    table: ParseTable,
) -> None:
    sep = "=" * 80
    print(f"\n{sep}")
    print(f"  TEST  : {label}")
    print(f"  INPUT : {source}")
    print(sep)

    tokens = tokenize(source)
    print(f"  Tokens: {' '.join(tokens)}\n")

    result = parse(tokens, table, START_SYMBOL)

    verdict = "[OK] PARSE SUCCESSFUL" if result else "[FAIL] PARSE FAILED"
    print(f"\n  {verdict}")
    print(sep)


def main() -> None:
    banner = "=" * 80
    print(banner)
    print("  LL(1) Non-Recursive Predictive Parser for Pascal")
    print(banner)

    # Step 1 - Compute FIRST sets
    print("\n[Step 1] Computing FIRST sets...")
    first = compute_first(GRAMMAR)

    # Step 2 - Compute FOLLOW sets
    print("[Step 2] Computing FOLLOW sets...")
    follow = compute_follow(GRAMMAR, first, START_SYMBOL)

    print_first_follow(first, follow)

    # Step 3 - Build parsing table
    print("\n[Step 3] Building LL(1) parsing table...")
    table = build_parse_table(GRAMMAR, first, follow)

    conflicts = check_ll1_conflicts(table)
    if conflicts:
        print(f"\n  [!] WARNING: {len(conflicts)} conflict(s) - grammar may not be LL(1)!")
        for nt, t in conflicts:
            print(f"       M[{nt}, '{t}'] has {len(table[(nt, t)])} entries")
    else:
        print("  [OK] No conflicts - grammar is LL(1).")

    print_parse_table(table)

    # Step 4 - Run test cases
    print(f"\n{'='*80}")
    print("  PARSING TESTS")
    print(f"{'='*80}")

    # # Test 1: simple variable declaration + assignment
    # run_test(
    #     "Simple assignment",
    #     "program sample ; var x : integer ; y : real begin x := 5 end .",
    #     table,
    # )

    # # Test 2: if-else with arithmetic
    # run_test(
    #     "If-else with arithmetic",
    #     "program demo ; var a : integer ; b : integer "
    #     "begin a := 10 ; if a + 5 then b := a * 2 else b := a - 1 end .",
    #     table,
    # )

    # # Test 3: while loop
    # run_test(
    #     "While loop",
    #     "program loop ; var i : integer "
    #     "begin i := 0 ; while i do i := i + 1 end .",
    #     table,
    # )

    # # Test 4: no var section (epsilon production for VAR_DECL)
    # run_test(
    #     "No variables (epsilon VAR_DECL)",
    #     "program novar ; begin x := 42 end .",
    #     table,
    # )

    # # Test 5: nested parenthesised expression
    # run_test(
    #     "Nested expression",
    #     "program expr_test ; var result : real "
    #     "begin result := ( 3 + 4 ) * ( 10 / 2 ) end .",
    #     table,
    # )

    # Test 6: intentional syntax error (missing :=)
    run_test(
        "Syntax error - missing :=",
        "program bad ; begin x 42 end .",
        table,
    )


if __name__ == "__main__":
    main()
