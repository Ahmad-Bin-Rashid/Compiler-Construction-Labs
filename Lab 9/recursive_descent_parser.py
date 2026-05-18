"""
=============================================================
 Recursive Descent Parser for Pascal  —  Lab 9
 Compiler Construction · Spring 2026
=============================================================

 Grammar (after left-recursion removal & left factoring):

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

 Run:  python recursive_descent_parser.py
=============================================================
"""

import re
from enum import Enum, auto


# ──────────────────────────────────────────────────────────
# 1.  TOKEN TYPES
# ──────────────────────────────────────────────────────────
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
    # literals / names
    ID      = auto()
    NUMBER  = auto()
    # sentinel
    EOF     = auto()


KEYWORDS: dict[str, TT] = {
    "program": TT.PROGRAM, "var": TT.VAR,   "begin": TT.BEGIN,
    "end":     TT.END,     "integer": TT.INTEGER, "real": TT.REAL,
    "if":      TT.IF,      "then":  TT.THEN, "else": TT.ELSE,
    "while":   TT.WHILE,   "do":    TT.DO,
}

TOKEN_NAMES: dict[TT, str] = {
    TT.PROGRAM: "program", TT.VAR:    "var",    TT.BEGIN:  "begin",
    TT.END:     "end",     TT.INTEGER:"integer", TT.REAL:   "real",
    TT.IF:      "if",      TT.THEN:   "then",   TT.ELSE:   "else",
    TT.WHILE:   "while",   TT.DO:     "do",     TT.ASSIGN: ":=",
    TT.COLON:   ":",       TT.SEMI:   ";",      TT.DOT:    ".",
    TT.LPAREN:  "(",       TT.RPAREN: ")",      TT.PLUS:   "+",
    TT.MINUS:   "-",       TT.STAR:   "*",      TT.SLASH:  "/",
    TT.ID:      "id",      TT.NUMBER: "number", TT.EOF:    "EOF",
}


# ──────────────────────────────────────────────────────────
# 2.  LEXER
# ──────────────────────────────────────────────────────────
TOKEN_RE = re.compile(
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


def tokenize(text: str) -> list[tuple[TT, str]]:
    tokens: list[tuple[TT, str]] = []
    for m in TOKEN_RE.finditer(text):
        kind = m.lastgroup
        val  = m.group()
        if kind == "SKIP":
            continue
        if kind == "ID" and val in KEYWORDS:
            tokens.append((KEYWORDS[val], val))
        else:
            tokens.append((TT[kind], val))
    tokens.append((TT.EOF, "EOF"))
    return tokens


# ──────────────────────────────────────────────────────────
# 3.  PARSER
# ──────────────────────────────────────────────────────────
class Parser:
    def __init__(self, tokens: list[tuple[TT, str]]):
        self.tokens  = tokens
        self.pos     = 0
        self.errors  = 0

    # ── Internal helpers ──────────────────────────────────
    @property
    def current(self) -> tuple[TT, str]:
        return self.tokens[self.pos]

    @property
    def tok(self) -> TT:
        return self.current[0]

    @property
    def lexeme(self) -> str:
        return self.current[1]

    def _name(self, tt: TT) -> str:
        return TOKEN_NAMES.get(tt, tt.name)

    def match(self, expected: TT) -> None:
        if self.tok == expected:
            print(f"  [match] {self._name(expected):<12} → \"{self.lexeme}\"")
            self.pos += 1
        else:
            print(f"  [ERROR] Expected '{self._name(expected)}' "
                  f"but found '{self._name(self.tok)}' (\"{self.lexeme}\")")
            self.errors += 1
            # panic-mode recovery: skip one token
            self.pos += 1

    # ── Step 5 & 6: one procedure per non-terminal ────────

    def parse_program(self):
        """program → program id ; block ."""
        print("[parse_program]")
        self.match(TT.PROGRAM)
        self.match(TT.ID)
        self.match(TT.SEMI)
        self.parse_block()
        self.match(TT.DOT)

    def parse_block(self):
        """block → var_decl stmt_block"""
        print("[parse_block]")
        self.parse_var_decl()
        self.parse_stmt_block()

    def parse_var_decl(self):
        """var_decl → var decl_list | ε
        FIRST = { var }   FOLLOW = { begin }
        """
        print("[parse_var_decl]")
        if self.tok == TT.VAR:              # FIRST(var decl_list)
            self.match(TT.VAR)
            self.parse_decl_list()
        # else ε  (lookahead ∈ FOLLOW = { begin })

    def parse_decl_list(self):
        """decl_list → decl decl_rest"""
        print("[parse_decl_list]")
        self.parse_decl()
        self.parse_decl_rest()

    def parse_decl_rest(self):
        """decl_rest → ; decl_list | ε
        FIRST = { ; }   FOLLOW = { begin }
        """
        print("[parse_decl_rest]")
        if self.tok == TT.SEMI:             # FIRST(; decl_list)
            self.match(TT.SEMI)
            self.parse_decl_list()
        # else ε

    def parse_decl(self):
        """decl → id : type"""
        print("[parse_decl]")
        self.match(TT.ID)
        self.match(TT.COLON)
        self.parse_type()

    def parse_type(self):
        """type → integer | real"""
        print("[parse_type]")
        if self.tok == TT.INTEGER:
            self.match(TT.INTEGER)
        elif self.tok == TT.REAL:
            self.match(TT.REAL)
        else:
            print(f"  [ERROR] Expected 'integer' or 'real', "
                  f"found '{self._name(self.tok)}' (\"{self.lexeme}\")")
            self.errors += 1
            self.pos += 1

    def parse_stmt_block(self):
        """stmt_block → begin stmt_list end"""
        print("[parse_stmt_block]")
        self.match(TT.BEGIN)
        self.parse_stmt_list()
        self.match(TT.END)

    def parse_stmt_list(self):
        """stmt_list → stmt stmt_rest"""
        print("[parse_stmt_list]")
        self.parse_stmt()
        self.parse_stmt_rest()

    def parse_stmt_rest(self):
        """stmt_rest → ; stmt_list | ε
        FIRST = { ; }   FOLLOW = { end }
        """
        print("[parse_stmt_rest]")
        if self.tok == TT.SEMI:             # FIRST(; stmt_list)
            self.match(TT.SEMI)
            self.parse_stmt_list()
        # else ε

    def parse_stmt(self):
        """stmt → assign_stmt | if_stmt | while_stmt
        Table entry chosen by FIRST set of each alternative.
        """
        print("[parse_stmt]")
        if self.tok == TT.ID:
            self.parse_assign_stmt()
        elif self.tok == TT.IF:
            self.parse_if_stmt()
        elif self.tok == TT.WHILE:
            self.parse_while_stmt()
        else:
            print(f"  [ERROR] Expected statement (id/if/while), "
                  f"found '{self._name(self.tok)}' (\"{self.lexeme}\")")
            self.errors += 1
            self.pos += 1

    def parse_assign_stmt(self):
        """assign_stmt → id := expr"""
        print("[parse_assign_stmt]")
        self.match(TT.ID)
        self.match(TT.ASSIGN)
        self.parse_expr()

    def parse_if_stmt(self):
        """if_stmt → if expr then stmt else stmt"""
        print("[parse_if_stmt]")
        self.match(TT.IF)
        self.parse_expr()
        self.match(TT.THEN)
        self.parse_stmt()
        self.match(TT.ELSE)
        self.parse_stmt()

    def parse_while_stmt(self):
        """while_stmt → while expr do stmt"""
        print("[parse_while_stmt]")
        self.match(TT.WHILE)
        self.parse_expr()
        self.match(TT.DO)
        self.parse_stmt()

    def parse_expr(self):
        """expr → term expr'"""
        print("[parse_expr]")
        self.parse_term()
        self.parse_expr_prime()

    def parse_expr_prime(self):
        """expr' → + term expr' | - term expr' | ε
        FIRST = { +, - }
        FOLLOW = { then, else, do, ;, end, ) }  → produce ε
        """
        print("[parse_expr']")
        if self.tok == TT.PLUS:
            self.match(TT.PLUS)
            self.parse_term()
            self.parse_expr_prime()
        elif self.tok == TT.MINUS:
            self.match(TT.MINUS)
            self.parse_term()
            self.parse_expr_prime()
        # else ε

    def parse_term(self):
        """term → factor term'"""
        print("[parse_term]")
        self.parse_factor()
        self.parse_term_prime()

    def parse_term_prime(self):
        """term' → * factor term' | / factor term' | ε
        FIRST = { *, / }
        FOLLOW = { +, -, then, else, do, ;, end, ) }  → produce ε
        """
        print("[parse_term']")
        if self.tok == TT.STAR:
            self.match(TT.STAR)
            self.parse_factor()
            self.parse_term_prime()
        elif self.tok == TT.SLASH:
            self.match(TT.SLASH)
            self.parse_factor()
            self.parse_term_prime()
        # else ε

    def parse_factor(self):
        """factor → ( expr ) | id | number
        FIRST = { (, id, number }
        """
        print("[parse_factor]")
        if self.tok == TT.LPAREN:
            self.match(TT.LPAREN)
            self.parse_expr()
            self.match(TT.RPAREN)
        elif self.tok == TT.ID:
            self.match(TT.ID)
        elif self.tok == TT.NUMBER:
            self.match(TT.NUMBER)
        else:
            print(f"  [ERROR] Expected '(' or id or number, "
                  f"found '{self._name(self.tok)}' (\"{self.lexeme}\")")
            self.errors += 1
            self.pos += 1


# ──────────────────────────────────────────────────────────
# 4.  DRIVER
# ──────────────────────────────────────────────────────────
def run_test(label: str, source: str) -> None:
    sep = "═" * 58
    print(f"\n{sep}")
    print(f"  TEST  : {label}")
    print(f"  INPUT : {source}")
    print(sep)
    tokens = tokenize(source)
    p = Parser(tokens)
    p.parse_program()
    verdict = "✔  PARSE SUCCESSFUL" if p.errors == 0 else f"✘  PARSE FAILED ({p.errors} error(s))"
    print(f"\n{verdict}")
    print(sep)


if __name__ == "__main__":
    # ── Test 1: simple variable declaration + assignment ──────
    run_test(
        "Simple assignment",
        "program sample ; "
        "var x : integer ; y : real "
        "begin "
        "  x := 5 "
        "end ."
    )

    # ── Test 2: if-else with arithmetic ───────────────────────
    run_test(
        "If-else with arithmetic",
        "program demo ; "
        "var a : integer ; b : integer "
        "begin "
        "  a := 10 ; "
        "  if a + 5 then "
        "    b := a * 2 "
        "  else "
        "    b := a - 1 "
        "end ."
    )

    # ── Test 3: while loop ────────────────────────────────────
    run_test(
        "While loop",
        "program loop ; "
        "var i : integer "
        "begin "
        "  i := 0 ; "
        "  while i do "
        "    i := i + 1 "
        "end ."
    )

    # ── Test 4: no var section (ε production) ─────────────────
    run_test(
        "No variables (epsilon var_decl)",
        "program novar ; "
        "begin "
        "  x := 42 "
        "end ."
    )

    # ── Test 5: nested parenthesised expression ───────────────
    run_test(
        "Nested expression",
        "program expr_test ; "
        "var result : real "
        "begin "
        "  result := ( 3 + 4 ) * ( 10 / 2 ) "
        "end ."
    )

    # ── Test 6: intentional syntax error (missing :=) ─────────
    run_test(
        "Syntax error — missing :=",
        "program bad ; "
        "begin "
        "  x 42 "        # missing :=
        "end ."
    )
