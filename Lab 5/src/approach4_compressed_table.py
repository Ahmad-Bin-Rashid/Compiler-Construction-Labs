
from approach3_table_driven import (
    TRANSITION, classify, S, CC, ERR, DONE,
    _make_token
)
from tokens import Token, TokenType, print_token_stream


#  Step 1 — Build Compressed Table from the dense table in Approach 3

class CompressedTable:


    def __init__(self, dense: dict[int, list[int]]):
        self.default   : dict[int, int]            = {}
        self.overrides : dict[int, dict[int, int]] = {}
        self._compress(dense)

    def _compress(self, dense: dict[int, list[int]]):
        for state, row in dense.items():
            # Find most frequent value → becomes the default
            freq: dict[int, int] = {}
            for v in row:
                freq[v] = freq.get(v, 0) + 1
            default_val = max(freq, key=freq.__getitem__)

            self.default[state]   = default_val
            self.overrides[state] = {
                cc: v for cc, v in enumerate(row) if v != default_val
            }

    def lookup(self, state: int, cc: int) -> int:
        ovr = self.overrides.get(state)
        if ovr and cc in ovr:
            return ovr[cc]
        return self.default.get(state, ERR)

    def stats(self) -> dict:
        total_cells     = sum(len(row) for row in TRANSITION.values())
        stored_overrides= sum(len(v) for v in self.overrides.values())
        stored_defaults = len(self.default)
        return {
            'states'          : len(self.default),
            'char_classes'    : CC.NUM_CLASSES,
            'dense_cells'     : total_cells,
            'compressed_cells': stored_overrides + stored_defaults,
            'reduction_%'     : round(
                100 * (1 - (stored_overrides + stored_defaults) / total_cells), 1
            ) if total_cells else 0,
        }


#  Compressed Lexer Driver

class CompressedLexer:


    def __init__(self, source: str):
        self._src    = source
        self._pos    = 0
        self._line   = 1
        self._col    = 1
        self._ctable = CompressedTable(TRANSITION)

    def tokenize(self) -> list[Token]:
        tokens = []
        while True:
            tok = self._next_token()
            tokens.append(tok)
            if tok.type == TokenType.EOF:
                break
        return tokens

    def compressed_stats(self) -> dict:
        return self._ctable.stats()

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
        while self._peek() in (' ', '\t', '\r', '\n'):
            self._advance()

        if self._peek() == '\0':
            return Token(TokenType.EOF, '', None, self._line, self._col)

        state      = S.START
        prev_state = S.START
        lexeme     = []
        tok_line   = self._line
        tok_col    = self._col

        retract_states = {S.IN_ID, S.IN_INT, S.IN_FLOAT,
                          S.A_SLASH, S.A_EQ, S.A_LT, S.A_GT}

        retract_always = {S.IN_ID, S.IN_INT, S.IN_FLOAT, S.A_SLASH}
        retract_if_not_eq = {S.A_EQ, S.A_LT, S.A_GT}
        single_char_states = set(range(20, 31))

        while state not in (DONE, ERR):
            ch  = self._advance()
            cc  = classify(ch)
            nxt = self._ctable.lookup(state, cc)

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


# ── Standalone runner ──────────────────────────────────────────────────
if __name__ == '__main__':
    import sys
    path = sys.argv[1] if len(sys.argv) > 1 else 'program.pascal'
    src  = open(path).read()
    lexer = CompressedLexer(src)
    toks  = lexer.tokenize()
    print_token_stream(toks, 'Compressed Table Lexer')

    stats = lexer.compressed_stats()
    print('\n  Compression Statistics:')
    print(f'    States            : {stats["states"]}')
    print(f'    Char classes      : {stats["char_classes"]}')
    print(f'    Dense table cells : {stats["dense_cells"]}')
    print(f'    Compressed entries: {stats["compressed_cells"]}')
    print(f'    Memory reduction  : {stats["reduction_%"]}%\n')
