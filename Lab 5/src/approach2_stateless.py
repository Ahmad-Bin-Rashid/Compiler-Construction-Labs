
from tokens import Token, TokenType, KEYWORDS, print_token_stream


class Stateless:


    def __init__(self, source: str):
        self._src    = source
        self._pos    = 0
        self._line   = 1
        self._col    = 1

    #  Public API 
    def tokenize(self) -> list[Token]:
        tokens = []
        while True:
            tok = self._next_token()
            tokens.append(tok)
            if tok.type == TokenType.EOF:
                break
        return tokens

    #  Cursor helpers 
    def _peek(self, offset: int = 0) -> str:
        idx = self._pos + offset
        return self._src[idx] if idx < len(self._src) else '\0'

    def _advance(self) -> str:
        ch = self._peek()
        self._pos += 1
        if ch == '\n':
            self._line += 1
            self._col   = 1
        else:
            self._col  += 1
        return ch

    def _skip_whitespace(self):
        while self._peek() in (' ', '\t', '\r', '\n'):
            self._advance()

    def _here(self):
    
        return self._line, self._col

    #  Top-level dispatcher 
    def _next_token(self) -> Token:
        self._skip_whitespace()

        ch = self._peek()
        if ch == '\0':
            return Token(TokenType.EOF, '', None, self._line, self._col)

        if ch.isalpha() or ch == '_':
            return self._scan_identifier()

        if ch.isdigit():
            return self._scan_number()

        if ch == '"':
            return self._scan_string()

        if ch == '/':
            return self._scan_slash()          # / or // or /*…*/

        if ch in '=!<>':
            return self._scan_relational()

        if ch in '+-*':
            return self._scan_arithmetic()

        if ch in '(){};,[]':
            return self._scan_delimiter()

        # Unknown character
        line, col = self._here()
        bad = self._advance()
        return Token(TokenType.ERROR, bad, None, line, col)

    #  Sub-scanners 

    def _scan_identifier(self) -> Token:
    
        line, col = self._here()
        buf = []
        while self._peek().isalnum() or self._peek() == '_':
            buf.append(self._advance())
        lexeme = ''.join(buf)
        ttype  = TokenType.KEYWORD if lexeme in KEYWORDS else TokenType.IDENTIFIER
        return Token(ttype, lexeme, None, line, col)

    def _scan_number(self) -> Token:
    
        line, col = self._here()
        buf = []

        # Consume integer part
        while self._peek().isdigit():
            buf.append(self._advance())

        # Check for optional fractional part
        if self._peek() == '.' and self._peek(1).isdigit():
            buf.append(self._advance())          # consume '.'
            while self._peek().isdigit():
                buf.append(self._advance())
            lexeme = ''.join(buf)
            return Token(TokenType.FLOAT, lexeme, float(lexeme), line, col)

        lexeme = ''.join(buf)
        return Token(TokenType.INTEGER, lexeme, int(lexeme), line, col)

    def _scan_string(self) -> Token:
    
        line, col = self._here()
        buf = [self._advance()]                  # consume opening '"'
        while True:
            ch = self._peek()
            if ch == '\0':                       # unterminated
                return Token(TokenType.ERROR, ''.join(buf), None, line, col)
            buf.append(self._advance())
            if ch == '"':
                break
        lexeme = ''.join(buf)
        return Token(TokenType.STRING, lexeme, lexeme[1:-1], line, col)

    def _scan_slash(self) -> Token:
    
        line, col = self._here()

        if self._peek(1) == '/':
            # Line comment — consume until newline
            buf = []
            while self._peek() not in ('\n', '\0'):
                buf.append(self._advance())
            return Token(TokenType.COMMENT, ''.join(buf), None, line, col)

        if self._peek(1) == '*':
            # Block comment — consume until */
            buf = [self._advance(), self._advance()]   # '/*'
            while True:
                if self._peek() == '\0':
                    return Token(TokenType.ERROR, ''.join(buf), None, line, col)
                ch = self._advance()
                buf.append(ch)
                if ch == '*' and self._peek() == '/':
                    buf.append(self._advance())        # consume '/'
                    break
            return Token(TokenType.COMMENT, ''.join(buf), None, line, col)

        # Plain division operator
        self._advance()
        return Token(TokenType.SLASH, '/', None, line, col)

    def _scan_relational(self) -> Token:
    
        line, col = self._here()
        ch  = self._advance()
        nxt = self._peek()

        if ch == '=' and nxt == '=':
            self._advance()
            return Token(TokenType.EQ, '==', None, line, col)
        if ch == '=':
            return Token(TokenType.ASSIGN, '=', None, line, col)
        if ch == '!' and nxt == '=':
            self._advance()
            return Token(TokenType.NEQ, '!=', None, line, col)
        if ch == '<' and nxt == '=':
            self._advance()
            return Token(TokenType.LTE, '<=', None, line, col)
        if ch == '<':
            return Token(TokenType.LT, '<', None, line, col)
        if ch == '>' and nxt == '=':
            self._advance()
            return Token(TokenType.GTE, '>=', None, line, col)
        if ch == '>':
            return Token(TokenType.GT, '>', None, line, col)

        return Token(TokenType.ERROR, ch, None, line, col)

    def _scan_arithmetic(self) -> Token:
    
        line, col = self._here()
        ch = self._advance()
        mapping = {'+': TokenType.PLUS, '-': TokenType.MINUS, '*': TokenType.STAR}
        return Token(mapping[ch], ch, None, line, col)

    def _scan_delimiter(self) -> Token:
    
        line, col = self._here()
        ch = self._advance()
        mapping = {
            '(': TokenType.LPAREN,  ')': TokenType.RPAREN,
            '{': TokenType.LBRACE,  '}': TokenType.RBRACE,
            ';': TokenType.SEMICOLON, ',': TokenType.COMMA,
            '[': TokenType.LBRACKET, ']': TokenType.RBRACKET,
        }
        ttype = mapping.get(ch, TokenType.ERROR)
        return Token(ttype, ch, None, line, col)


#  Standalone runner 
if __name__ == '__main__':
    import sys
    path = sys.argv[1] if len(sys.argv) > 1 else 'program.pascal'
    src  = open(path).read()
    lexer = Stateless(src)
    toks  = lexer.tokenize()
    print_token_stream(toks, 'Approach 2 — Stateless (Functional Dispatch)')
