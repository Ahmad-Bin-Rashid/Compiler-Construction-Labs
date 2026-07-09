"""
=============================================================
 Pascal Recursive-Descent Parser  —  Lab 13
=============================================================

 Extends the Lab-9 recursive-descent parser with a full
 symbol-table integration (Lab 13):

   • Variable declarations  → insert() into current scope
   • Function declarations  → insert() at outer scope
   • Use of identifiers     → lookup() across scope stack
   • Duplicate declarations → error reported immediately
   • Undeclared identifiers → error reported at point of use
   • begin/end blocks       → beginScope / endScope

 Grammar (same as Lab 9, Pascal subset):

   program     →  program id ; block .
   block       →  var_decl stmt_block
   var_decl    →  var decl_list | ε
   decl_list   →  decl decl_rest
   decl_rest   →  ; decl_list | ε
   decl        →  id : type
   type        →  integer | real
   stmt_block  →  begin stmt_list end
   stmt_list   →  stmt stmt_rest
   stmt_rest   →  ; stmt_list | ε
   stmt        →  assign_stmt | if_stmt | while_stmt
   assign_stmt →  id := expr
   if_stmt     →  if expr then stmt else stmt
   while_stmt  →  while expr do stmt
   expr        →  term expr'
   expr'       →  + term expr' | - term expr' | ε
   term        →  factor term'
   term'       →  * factor term' | / factor term' | ε
   factor      →  ( expr ) | id | number

 Run:
   python pascal_parser.py [input_file]
   python pascal_parser.py          (runs built-in test suite)
=============================================================
"""

import re
import sys
import os

# Import the symbol table from the same package
sys.path.insert(0, os.path.dirname(__file__))
from symbol_table import (
    SymbolTableManager,
    KIND_VAR, KIND_FUNC,
    TYPE_INT, TYPE_REAL,
)


# ──────────────────────────────────────────────────────────────
# 1.  TOKEN TYPES
# ──────────────────────────────────────────────────────────────
from enum import Enum, auto


class TT(Enum):
    # keywords
    PROGRAM = auto(); VAR     = auto(); BEGIN   = auto(); END     = auto()
    INTEGER = auto(); REAL    = auto(); IF      = auto(); THEN    = auto()
    ELSE    = auto(); WHILE   = auto(); DO      = auto()
    # operators / punctuation
    ASSIGN  = auto()   # :=
    COLON   = auto()   # :
    SEMI    = auto()   # ;
    DOT     = auto()   # .
    LPAREN  = auto()   # (
    RPAREN  = auto()   # )
    PLUS    = auto()   # +
    MINUS   = auto()   # -
    STAR    = auto()   # *
    SLASH   = auto()   # /
    # comparison operators (extended for richer expressions)
    EQ      = auto()   # =
    LT      = auto()   # <
    GT      = auto()   # >
    LEQ     = auto()   # <=
    GEQ     = auto()   # >=
    NEQ     = auto()   # <>
    # literals / names
    ID      = auto()
    NUMBER  = auto()
    # sentinel
    EOF     = auto()


KEYWORDS: dict[str, TT] = {
    "program": TT.PROGRAM, "var":     TT.VAR,     "begin": TT.BEGIN,
    "end":     TT.END,     "integer": TT.INTEGER,  "real":  TT.REAL,
    "if":      TT.IF,      "then":    TT.THEN,     "else":  TT.ELSE,
    "while":   TT.WHILE,   "do":      TT.DO,
}

TOKEN_NAMES: dict[TT, str] = {
    TT.PROGRAM: "program", TT.VAR:    "var",    TT.BEGIN:  "begin",
    TT.END:     "end",     TT.INTEGER:"integer", TT.REAL:   "real",
    TT.IF:      "if",      TT.THEN:   "then",   TT.ELSE:   "else",
    TT.WHILE:   "while",   TT.DO:     "do",     TT.ASSIGN: ":=",
    TT.COLON:   ":",       TT.SEMI:   ";",      TT.DOT:    ".",
    TT.LPAREN:  "(",       TT.RPAREN: ")",      TT.PLUS:   "+",
    TT.MINUS:   "-",       TT.STAR:   "*",      TT.SLASH:  "/",
    TT.EQ:      "=",       TT.LT:     "<",      TT.GT:     ">",
    TT.LEQ:     "<=",      TT.GEQ:    ">=",     TT.NEQ:    "<>",
    TT.ID:      "id",      TT.NUMBER: "number", TT.EOF:    "EOF",
}

# Pascal type keyword → symbol-table TYPE_* constant
TYPE_MAP: dict[TT, str] = {
    TT.INTEGER: TYPE_INT,
    TT.REAL:    TYPE_REAL,
}


# ──────────────────────────────────────────────────────────────
# 2.  LEXER  (enhanced: tracks line numbers)
# ──────────────────────────────────────────────────────────────
TOKEN_RE = re.compile(
    r"(?P<NUMBER>\d+(\.\d+)?)"
    r"|(?P<ASSIGN>:=)"
    r"|(?P<LEQ><=)"
    r"|(?P<GEQ>>=)"
    r"|(?P<NEQ><>)"
    r"|(?P<COLON>:)"
    r"|(?P<SEMI>;)"
    r"|(?P<DOT>\.)"
    r"|(?P<LPAREN>\()"
    r"|(?P<RPAREN>\))"
    r"|(?P<PLUS>\+)"
    r"|(?P<MINUS>-)"
    r"|(?P<STAR>\*)"
    r"|(?P<SLASH>/)"
    r"|(?P<EQ>=)"
    r"|(?P<LT><)"
    r"|(?P<GT>>)"
    r"|(?P<ID>[A-Za-z_]\w*)"
    r"|(?P<NEWLINE>\n)"
    r"|(?P<SKIP>[ \t\r]+)"
    r"|(?P<COMMENT>\{[^}]*\})"        # Pascal { … } comments
)


Token = tuple[TT, str, int]   # (type, lexeme, line_number)


def tokenize(text: str) -> list[Token]:
    """
    Tokenise *text* and return a list of (TT, lexeme, line) triples.
    Line numbers are 1-based.
    """
    tokens: list[Token] = []
    line = 1
    for m in TOKEN_RE.finditer(text):
        kind = m.lastgroup
        val  = m.group()
        if kind in ("SKIP", "COMMENT"):
            continue
        if kind == "NEWLINE":
            line += 1
            continue
        if kind == "ID" and val.lower() in KEYWORDS:
            tokens.append((KEYWORDS[val.lower()], val, line))
        elif kind in ("NUMBER", "ID", "ASSIGN", "LEQ", "GEQ", "NEQ",
                      "COLON", "SEMI", "DOT", "LPAREN", "RPAREN",
                      "PLUS", "MINUS", "STAR", "SLASH",
                      "EQ", "LT", "GT"):
            tokens.append((TT[kind], val, line))
    tokens.append((TT.EOF, "EOF", line))
    return tokens


# ──────────────────────────────────────────────────────────────
# 3.  PARSER  (Task 3 — symbol-table integrated)
# ──────────────────────────────────────────────────────────────
class Parser:
    """
    Recursive-descent parser for the Pascal subset defined by the
    Lab-9 grammar.  Now integrated with SymbolTableManager:

      • Declarations  → insert (duplicate = error)
      • Identifier use → lookup (undeclared = error)
      • Blocks        → beginScope / endScope
    """

    def __init__(self, tokens: list[Token], verbose: bool = False):
        self.tokens  = tokens
        self.pos     = 0
        self.errors  = 0
        self.verbose = verbose                    # show parse-trace lines
        self.stm     = SymbolTableManager()       # opens global scope (0)

    # ── Helpers ───────────────────────────────────────────────
    @property
    def current(self) -> Token:
        return self.tokens[self.pos]

    @property
    def tok(self) -> TT:
        return self.current[0]

    @property
    def lexeme(self) -> str:
        return self.current[1]

    @property
    def line(self) -> int:
        return self.current[2]

    def _name(self, tt: TT) -> str:
        return TOKEN_NAMES.get(tt, tt.name)

    def _trace(self, msg: str) -> None:
        """Print a parse-trace line only when verbose mode is on."""
        if self.verbose:
            print(f"  [parse] {msg}")

    def match(self, expected: TT) -> str:
        """
        Consume the current token if it matches *expected*.
        On mismatch, report an error and skip the unexpected token
        (panic-mode recovery — one token).
        Returns the consumed lexeme (empty string on error).
        """
        if self.tok == expected:
            lex = self.lexeme
            self._trace(f"{self._name(expected):<12} → \"{lex}\"")
            self.pos += 1
            return lex
        else:
            print(f"ERROR line {self.line}: expected '{self._name(expected)}' "
                  f"but found '{self._name(self.tok)}' (\"{self.lexeme}\")")
            self.errors += 1
            self.pos += 1
            return ""

    # ── Grammar rules ─────────────────────────────────────────

    def parse_program(self):
        """program → program id ; block ."""
        self._trace("parse_program")
        self.match(TT.PROGRAM)

        prog_name = self.lexeme
        prog_line = self.line
        self.match(TT.ID)
        # Register the program name as a function in the global scope
        result = self.stm.insert(prog_name, KIND_FUNC, TYPE_INT, prog_line)
        if result is None:
            print(f"ERROR line {prog_line}: duplicate declaration '{prog_name}'")
            self.errors += 1

        self.match(TT.SEMI)

        # A Pascal program block gets its own scope
        self.stm.begin_scope()
        self.parse_block()
        self.stm.end_scope()

        self.match(TT.DOT)

        # Close the global scope
        self.stm.end_scope()

    def parse_block(self):
        """block → var_decl stmt_block"""
        self._trace("parse_block")
        self.parse_var_decl()
        self.parse_stmt_block()

    def parse_var_decl(self):
        """var_decl → var decl_list | ε"""
        self._trace("parse_var_decl")
        if self.tok == TT.VAR:
            self.match(TT.VAR)
            self.parse_decl_list()

    def parse_decl_list(self):
        """decl_list → decl decl_rest"""
        self._trace("parse_decl_list")
        self.parse_decl()
        self.parse_decl_rest()

    def parse_decl_rest(self):
        """decl_rest → ; decl_list | ε"""
        self._trace("parse_decl_rest")
        if self.tok == TT.SEMI:
            self.match(TT.SEMI)
            # Only continue decl_list if the next token can start a declaration
            # (i.e. is an ID), otherwise this ; belongs to stmt_rest.
            if self.tok == TT.ID:
                self.parse_decl_list()

    def parse_decl(self):
        """decl → id : type   (Task 3: insert into symbol table)"""
        self._trace("parse_decl")
        var_name = self.lexeme
        var_line = self.line
        self.match(TT.ID)
        self.match(TT.COLON)
        var_type = self.parse_type()       # returns the TYPE_* string

        # ── Task 3: insert into current scope, detect duplicates ──
        result = self.stm.insert(var_name, KIND_VAR, var_type, var_line)
        if result is None:
            print(f"ERROR line {var_line}: "
                  f"duplicate declaration '{var_name}' in this scope")
            self.errors += 1

    def parse_type(self) -> str:
        """type → integer | real   Returns the TYPE_* constant string."""
        self._trace("parse_type")
        if self.tok in TYPE_MAP:
            type_str = TYPE_MAP[self.tok]
            self.match(self.tok)
            return type_str
        else:
            print(f"ERROR line {self.line}: expected 'integer' or 'real', "
                  f"found '{self._name(self.tok)}' (\"{self.lexeme}\")")
            self.errors += 1
            self.pos += 1
            return TYPE_INT    # recovery default

    def parse_stmt_block(self):
        """stmt_block → begin stmt_list end"""
        self._trace("parse_stmt_block")
        self.match(TT.BEGIN)
        self.parse_stmt_list()
        self.match(TT.END)

    def parse_stmt_list(self):
        """stmt_list → stmt stmt_rest"""
        self._trace("parse_stmt_list")
        self.parse_stmt()
        self.parse_stmt_rest()

    def parse_stmt_rest(self):
        """stmt_rest → ; stmt_list | ε"""
        self._trace("parse_stmt_rest")
        if self.tok == TT.SEMI:
            self.match(TT.SEMI)
            # Only recurse if a statement can follow
            if self.tok in (TT.ID, TT.IF, TT.WHILE):
                self.parse_stmt_list()

    def parse_stmt(self):
        """stmt → assign_stmt | if_stmt | while_stmt"""
        self._trace("parse_stmt")
        if self.tok == TT.ID:
            self.parse_assign_stmt()
        elif self.tok == TT.IF:
            self.parse_if_stmt()
        elif self.tok == TT.WHILE:
            self.parse_while_stmt()
        else:
            print(f"ERROR line {self.line}: expected statement (id/if/while), "
                  f"found '{self._name(self.tok)}' (\"{self.lexeme}\")")
            self.errors += 1
            self.pos += 1

    def parse_assign_stmt(self):
        """assign_stmt → id := expr   (Task 3: lookup lhs)"""
        self._trace("parse_assign_stmt")
        var_name = self.lexeme
        var_line = self.line
        self.match(TT.ID)

        # ── Task 3: verify LHS identifier is declared ─────────
        e = self.stm.lookup(var_name)
        if e is None:
            print(f"ERROR line {var_line}: undeclared identifier '{var_name}'")
            self.errors += 1

        self.match(TT.ASSIGN)
        self.parse_expr()

    def parse_if_stmt(self):
        """if_stmt → if expr then stmt else stmt"""
        self._trace("parse_if_stmt")
        self.match(TT.IF)
        self.parse_expr()
        self.match(TT.THEN)
        self.parse_stmt()
        self.match(TT.ELSE)
        self.parse_stmt()

    def parse_while_stmt(self):
        """while_stmt → while expr do stmt"""
        self._trace("parse_while_stmt")
        self.match(TT.WHILE)
        self.parse_expr()
        self.match(TT.DO)
        self.parse_stmt()

    def parse_expr(self):
        """expr → term expr'"""
        self._trace("parse_expr")
        self.parse_term()
        self.parse_expr_prime()

    def parse_expr_prime(self):
        """expr' → + term expr' | - term expr' | = term expr' | < term expr' | … | ε"""
        self._trace("parse_expr'")
        if self.tok in (TT.PLUS, TT.MINUS, TT.EQ, TT.LT, TT.GT,
                        TT.LEQ, TT.GEQ, TT.NEQ):
            self.match(self.tok)
            self.parse_term()
            self.parse_expr_prime()

    def parse_term(self):
        """term → factor term'"""
        self._trace("parse_term")
        self.parse_factor()
        self.parse_term_prime()

    def parse_term_prime(self):
        """term' → * factor term' | / factor term' | ε"""
        self._trace("parse_term'")
        if self.tok in (TT.STAR, TT.SLASH):
            self.match(self.tok)
            self.parse_factor()
            self.parse_term_prime()

    def parse_factor(self):
        """factor → ( expr ) | id | number   (Task 3: lookup id uses)"""
        self._trace("parse_factor")
        if self.tok == TT.LPAREN:
            self.match(TT.LPAREN)
            self.parse_expr()
            self.match(TT.RPAREN)
        elif self.tok == TT.ID:
            id_name = self.lexeme
            id_line = self.line
            self.match(TT.ID)
            # ── Task 3: every identifier used in an expression must be declared
            e = self.stm.lookup(id_name)
            if e is None:
                print(f"ERROR line {id_line}: undeclared identifier '{id_name}'")
                self.errors += 1
        elif self.tok == TT.NUMBER:
            self.match(TT.NUMBER)
        else:
            print(f"ERROR line {self.line}: expected '(' or id or number, "
                  f"found '{self._name(self.tok)}' (\"{self.lexeme}\")")
            self.errors += 1
            self.pos += 1


# ──────────────────────────────────────────────────────────────
# 4.  DRIVER HELPERS
# ──────────────────────────────────────────────────────────────
def run_source(label: str, source: str, verbose: bool = False) -> int:
    """
    Tokenise *source*, parse it, and return the error count.
    Prints a test banner before and verdict after.
    """
    sep = "═" * 60
    print(f"\n{sep}")
    print(f"  TEST  : {label}")
    print(sep)
    if verbose:
        print(f"  SOURCE:\n{source}\n")

    tokens = tokenize(source)
    p = Parser(tokens, verbose=verbose)
    p.parse_program()

    verdict = ("✔  PARSE + SYMBOL TABLE OK"
               if p.errors == 0
               else f"✘  FINISHED WITH {p.errors} ERROR(S)")
    print(f"\n{verdict}")
    print(sep)
    return p.errors


def run_file(path: str, verbose: bool = False) -> int:
    """Read a Pascal source file and parse it."""
    with open(path, "r", encoding="utf-8") as fh:
        source = fh.read()
    return run_source(path, source, verbose=verbose)


# ──────────────────────────────────────────────────────────────
# 5.  BUILT-IN TEST SUITE
# ──────────────────────────────────────────────────────────────
if __name__ == "__main__":
    if len(sys.argv) > 1:
        # Parse a file supplied on the command line
        verbose_flag = "--verbose" in sys.argv or "-v" in sys.argv
        for arg in sys.argv[1:]:
            if arg not in ("--verbose", "-v"):
                run_file(arg, verbose=verbose_flag)
        sys.exit(0)

    # ── Test 1: valid simple program ─────────────────────────
    run_source(
        "Valid — simple variable declaration + assignment",
        "program sample ;\n"
        "var x : integer ;\n"
        "    y : real\n"
        "begin\n"
        "  x := 5 ;\n"
        "  y := x\n"
        "end .\n"
    )

    # ── Test 2: valid if-else with arithmetic ─────────────────
    run_source(
        "Valid — if-else with arithmetic",
        "program demo ;\n"
        "var a : integer ;\n"
        "    b : integer\n"
        "begin\n"
        "  a := 10 ;\n"
        "  if a + 5 then\n"
        "    b := a * 2\n"
        "  else\n"
        "    b := a - 1\n"
        "end .\n"
    )

    # ── Test 3: valid while loop ───────────────────────────────
    run_source(
        "Valid — while loop",
        "program loop ;\n"
        "var i : integer\n"
        "begin\n"
        "  i := 0 ;\n"
        "  while i do\n"
        "    i := i + 1\n"
        "end .\n"
    )

    # ── Test 4: duplicate declaration (should trigger error) ──
    run_source(
        "Invalid — duplicate variable 'x'",
        "program dup ;\n"
        "var x : integer ;\n"
        "    x : real\n"        # duplicate!
        "begin\n"
        "  x := 1\n"
        "end .\n"
    )

    # ── Test 5: undeclared identifier (should trigger error) ──
    run_source(
        "Invalid — undeclared identifier 'z'",
        "program undecl ;\n"
        "var x : integer\n"
        "begin\n"
        "  x := z + 1\n"        # z is undeclared
        "end .\n"
    )

    # ── Test 6: no var section (ε production) ─────────────────
    run_source(
        "Invalid — no var section, undeclared identifier 'x'",
        "program novar ;\n"
        "begin\n"
        "  x := 42\n"           # x never declared
        "end .\n"
    )

    # ── Test 7: nested expression, all declared ────────────────
    run_source(
        "Valid — nested parenthesised expression",
        "program expr_test ;\n"
        "var result : real ;\n"
        "    a      : integer ;\n"
        "    b      : integer\n"
        "begin\n"
        "  a      := 3 ;\n"
        "  b      := 4 ;\n"
        "  result := ( a + b ) * ( 10 / 2 )\n"
        "end .\n"
    )
