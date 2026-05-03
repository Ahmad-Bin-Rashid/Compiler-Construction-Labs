
from tokens import Token, TokenType, KEYWORDS, print_token_stream



#  Character Classes  (columns of the transition table)

class CC:               # Character Class indices
    LETTER  = 0   # a-z A-Z _
    DIGIT   = 1   # 0-9
    DOT     = 2   # .
    DQUOTE  = 3   # "
    PLUS    = 4   # +
    MINUS   = 5   # -
    STAR    = 6   # *
    SLASH   = 7   # /
    EQ      = 8   # =
    BANG    = 9   # !
    LT      = 10  # <
    GT      = 11  # >
    LPAREN  = 12  # (
    RPAREN  = 13  # )
    LBRACE  = 14  # {
    RBRACE  = 15  # }
    SEMI    = 16  # ;
    COMMA   = 17  # ,
    LBRACK  = 18  # [
    RBRACK  = 19  # ]
    NEWLINE = 20  # \n
    SPACE   = 21  # space / tab / \r
    EOF_CC  = 22  # \0
    OTHER   = 23  # anything else
    NUM_CLASSES = 24


def classify(ch: str) -> int:
    if ch.isalpha() or ch == '_':  return CC.LETTER
    if ch.isdigit():               return CC.DIGIT
    tbl = {
        '.':  CC.DOT,   '"': CC.DQUOTE,
        '+':  CC.PLUS,  '-': CC.MINUS,  '*': CC.STAR, '/': CC.SLASH,
        '=':  CC.EQ,    '!': CC.BANG,   '<': CC.LT,   '>': CC.GT,
        '(':  CC.LPAREN,'(': CC.LPAREN, ')': CC.RPAREN,
        '{':  CC.LBRACE,'}': CC.RBRACE, ';': CC.SEMI,
        ',':  CC.COMMA, '[': CC.LBRACK, ']': CC.RBRACK,
        '\n': CC.NEWLINE,
        ' ':  CC.SPACE, '\t': CC.SPACE, '\r': CC.SPACE,
        '\0': CC.EOF_CC,
    }
    return tbl.get(ch, CC.OTHER)



#  States

class S:
    START    =  0
    IN_ID    =  1   # inside identifier
    IN_INT   =  2   # inside integer
    IN_FLOAT =  3   # inside float (after '.')
    IN_STR   =  4   # inside string
    IN_ESC   =  5   # inside string, after backslash (reserved)
    A_SLASH  =  6   # saw '/'
    IN_LCMT  =  7   # inside // comment
    IN_BCMT  =  8   # inside /* comment
    IN_BCMT2 =  9   # saw '*' inside block comment
    A_EQ     = 10   # saw '='
    A_BANG   = 11   # saw '!'
    A_LT     = 12   # saw '<'
    A_GT     = 13   # saw '>'
    # Single-char token accepting states (reached from START, DONE immediately)
    PLUS_S   = 20
    MINUS_S  = 21
    STAR_S   = 22
    LPAR_S   = 23
    RPAR_S   = 24
    LBRC_S   = 25
    RBRC_S   = 26
    SEMI_S   = 27
    COMMA_S  = 28
    LBRK_S   = 29
    RBRK_S   = 30
    ERR      = 98
    DONE     = 99


# -1 sentinel means "ERROR"
ERR  = S.ERR
DONE = S.DONE

# Helper: build a row initialised to a default, with overrides
def _row(default, overrides=None):
    r = [default] * CC.NUM_CLASSES
    if overrides:
        for k, v in overrides.items():
            r[k] = v
    return r



#  Transition Table   table[state][char_class] → next_state
#  States ≥ 20 are single-step accepting states treated specially.

TRANSITION: dict[int, list[int]] = {

    S.START: _row(ERR, {
            CC.LETTER:  S.IN_ID,
            CC.DIGIT:   S.IN_INT,
            CC.DQUOTE:  S.IN_STR,
            CC.SLASH:   S.A_SLASH,
            CC.EQ:      S.A_EQ,
            CC.BANG:    S.A_BANG,
            CC.LT:      S.A_LT,
            CC.GT:      S.A_GT,
            CC.PLUS:    S.PLUS_S,
            CC.MINUS:   S.MINUS_S,
            CC.STAR:    S.STAR_S,
            CC.LPAREN:  S.LPAR_S,
            CC.RPAREN:  S.RPAR_S,
            CC.LBRACE:  S.LBRC_S,
            CC.RBRACE:  S.RBRC_S,
            CC.SEMI:    S.SEMI_S,
            CC.COMMA:   S.COMMA_S,
            CC.LBRACK:  S.LBRK_S,
            CC.RBRACK:  S.RBRK_S,
            CC.SPACE:   S.START,     # consume whitespace
            CC.NEWLINE: S.START,
            CC.EOF_CC:  DONE,
        }),

    S.IN_ID:    _row(DONE, {CC.LETTER: S.IN_ID, CC.DIGIT: S.IN_ID}),
    S.IN_INT:   _row(DONE, {CC.DIGIT: S.IN_INT, CC.DOT: S.IN_FLOAT}),
    S.IN_FLOAT: _row(DONE, {CC.DIGIT: S.IN_FLOAT}),
    S.IN_STR:   _row(S.IN_STR, {CC.DQUOTE: DONE, CC.EOF_CC: ERR}),

    S.A_SLASH:  _row(DONE, {CC.SLASH: S.IN_LCMT, CC.STAR: S.IN_BCMT}),
    S.IN_LCMT:  _row(S.IN_LCMT, {CC.NEWLINE: DONE, CC.EOF_CC: DONE}),
    S.IN_BCMT:  _row(S.IN_BCMT, {CC.STAR: S.IN_BCMT2, CC.EOF_CC: ERR}),
    S.IN_BCMT2: _row(S.IN_BCMT, {CC.SLASH: DONE, CC.STAR: S.IN_BCMT2, CC.EOF_CC: ERR}),

    S.A_EQ:   _row(DONE, {CC.EQ: DONE}),
    S.A_BANG: _row(ERR,  {CC.EQ: DONE}),
    S.A_LT:   _row(DONE, {CC.EQ: DONE}),
    S.A_GT:   _row(DONE, {CC.EQ: DONE}),
}

# Single-char accepting states don't need transitions (handled immediately)
for _s in (S.PLUS_S, S.MINUS_S, S.STAR_S, S.LPAR_S, S.RPAR_S,
           S.LBRC_S, S.RBRC_S, S.SEMI_S, S.COMMA_S, S.LBRK_S, S.RBRK_S):
    TRANSITION[_s] = _row(DONE)



#  Accepting-state → token type mapper

def _make_token(state: int, prev_state: int, lexeme: str,
                line: int, col: int) -> Token:

    lex = lexeme

    # Resolve compound tokens via prev_state path
    if prev_state in (S.IN_ID,):
        ttype = TokenType.KEYWORD if lex in KEYWORDS else TokenType.IDENTIFIER
        return Token(ttype, lex, None, line, col)

    if prev_state == S.IN_INT:
        return Token(TokenType.INTEGER, lex, int(lex), line, col)

    if prev_state == S.IN_FLOAT:
        return Token(TokenType.FLOAT, lex, float(lex), line, col)

    if prev_state == S.IN_STR:
        return Token(TokenType.STRING, lex, lex[1:-1], line, col)

    if prev_state in (S.IN_LCMT, S.IN_BCMT, S.IN_BCMT2):
        return Token(TokenType.COMMENT, lex.rstrip(), None, line, col)

    if prev_state == S.A_SLASH:
        return Token(TokenType.SLASH, lex, None, line, col)

    if prev_state == S.A_EQ:
        return Token(TokenType.EQ if lex == '==' else TokenType.ASSIGN, lex, None, line, col)

    if prev_state == S.A_BANG:
        return Token(TokenType.NEQ, lex, None, line, col)

    if prev_state == S.A_LT:
        return Token(TokenType.LTE if lex == '<=' else TokenType.LT, lex, None, line, col)

    if prev_state == S.A_GT:
        return Token(TokenType.GTE if lex == '>=' else TokenType.GT, lex, None, line, col)

    # Single-char states
    single = {
        S.PLUS_S:  TokenType.PLUS,  S.MINUS_S: TokenType.MINUS,
        S.STAR_S:  TokenType.STAR,  S.LPAR_S:  TokenType.LPAREN,
        S.RPAR_S:  TokenType.RPAREN,S.LBRC_S:  TokenType.LBRACE,
        S.RBRC_S:  TokenType.RBRACE,S.SEMI_S:  TokenType.SEMICOLON,
        S.COMMA_S: TokenType.COMMA, S.LBRK_S:  TokenType.LBRACKET,
        S.RBRK_S:  TokenType.RBRACKET,
    }
    if prev_state in single:
        return Token(single[prev_state], lex, None, line, col)

    # EOF
    if lex == '' or lex == '\0':
        return Token(TokenType.EOF, '', None, line, col)

    return Token(TokenType.ERROR, lex, None, line, col)



#  Driver

class TableDriven:


    def __init__(self, source: str):
        self._src  = source
        self._pos  = 0
        self._line = 1
        self._col  = 1

    def tokenize(self) -> list[Token]:
        tokens = []
        while True:
            tok = self._next_token()
            tokens.append(tok)
            if tok.type == TokenType.EOF:
                break
        return tokens

    def _peek(self) -> str:
        return self._src[self._pos] if self._pos < len(self._src) else '\0'

    def _advance(self) -> str:
        ch = self._peek()
        self._pos += 1
        if ch == '\n': self._line += 1; self._col = 1
        else:          self._col  += 1
        return ch

    def _unget(self):
        if self._pos > 0:
            self._pos -= 1
            ch = self._src[self._pos]
            if ch == '\n': self._line -= 1; self._col = 1
            else:          self._col  -= 1

    def _next_token(self) -> Token:
        # Skip leading whitespace via the table (state stays START)
        while self._peek() in (' ', '\t', '\r', '\n'):
            self._advance()

        if self._peek() == '\0':
            return Token(TokenType.EOF, '', None, self._line, self._col)

        state      = S.START
        prev_state = S.START
        lexeme     = []
        tok_line   = self._line
        tok_col    = self._col

        retract_always = {S.IN_ID, S.IN_INT, S.IN_FLOAT, S.A_SLASH}
        retract_if_not_eq = {S.A_EQ, S.A_LT, S.A_GT}
        single_char_states = set(range(20, 31))

        while state not in (DONE, ERR):
            ch    = self._advance()
            cc    = classify(ch)
            nxt   = TRANSITION[state][cc]

            should_retract = (nxt == DONE and ch != chr(0) and
                              (state in retract_always or
                               (state in retract_if_not_eq and ch != '=')))
            if should_retract:
                self._unget()
            else:
                if ch != chr(0):
                    lexeme.append(ch)

            prev_state = state
            state      = nxt

            if state in single_char_states:
                prev_state = state
                state      = DONE
                break

        lex_str = ''.join(lexeme)

        if state == ERR:
            return Token(TokenType.ERROR, lex_str or '?', None, tok_line, tok_col)

        return _make_token(state, prev_state, lex_str, tok_line, tok_col)


#  Standalone runner 
if __name__ == '__main__':
    import sys
    path = sys.argv[1] if len(sys.argv) > 1 else 'program.pascal'
    src  = open(path).read()
    lexer = TableDriven(src)
    toks  = lexer.tokenize()
    print_token_stream(toks, 'Approach 3 — Transition Table Driven')
