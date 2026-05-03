
from tokens import Token, TokenType, KEYWORDS, print_token_stream


#  States 
class State:
    START      = 0
    IN_ID      = 1   # inside an identifier / keyword
    IN_INT     = 2   # inside an integer literal
    IN_FLOAT   = 3   # after the decimal point
    IN_STRING  = 4   # inside a string literal
    IN_LINE_CMT= 5   # inside a // comment
    IN_BLK_CMT = 6   # inside a /* … */ comment
    IN_BLK_END = 7   # saw '*' inside block comment — waiting for '/'
    IN_NEQ     = 8   # saw '!' — expecting '='
    IN_EQ      = 9   # saw '=' — could be '==' or plain '='
    IN_LT      = 10  # saw '<' — could be '<='
    IN_GT      = 11  # saw '>' — could be '>='
    IN_SLASH   = 12  # saw '/' — could be comment start
    DONE       = 99
    ERROR      = -1


class StateBased:
    def __init__(self, source: str):
        self._src   = source
        self._pos   = 0
        self._line  = 1
        self._col   = 1
        self._tokens: list[Token] = []

    #  Public entry point 
    def tokenize(self) -> list[Token]:
        while True:
            tok = self._next_token()
            self._tokens.append(tok)
            if tok.type == TokenType.EOF:
                break
        return self._tokens

    #  Character helpers 
    def _peek(self) -> str:
        return self._src[self._pos] if self._pos < len(self._src) else '\0'

    def _advance(self) -> str:
        ch = self._src[self._pos] if self._pos < len(self._src) else '\0'
        self._pos += 1
        if ch == '\n':
            self._line += 1
            self._col   = 1
        else:
            self._col  += 1
        return ch

    def _unget(self):
    
        if self._pos > 0:
            self._pos -= 1
            if self._src[self._pos] == '\n':
                self._line -= 1
                # Approximate col — good enough for error messages
                self._col = 1
            else:
                self._col -= 1

    def _make(self, ttype, lexeme, line, col, value=None) -> Token:
        if ttype == TokenType.IDENTIFIER and lexeme in KEYWORDS:
            ttype = TokenType.KEYWORD
        return Token(ttype, lexeme, value, line, col)

    #  Core state machine 
    def _next_token(self) -> Token:
        # Skip whitespace before entering the state machine
        while self._peek() in (' ', '\t', '\r', '\n'):
            self._advance()

        if self._peek() == '\0':
            return Token(TokenType.EOF, '', None, self._line, self._col)

        state   = State.START
        lexeme  = []
        tok_line = self._line
        tok_col  = self._col
        result  = None          # filled when state → DONE

        while state not in (State.DONE, State.ERROR):
            ch = self._advance()

            #  START 
            if state == State.START:
                lexeme.append(ch)

                if ch.isalpha() or ch == '_':
                    state = State.IN_ID

                elif ch.isdigit():
                    state = State.IN_INT

                elif ch == '"':
                    state = State.IN_STRING

                elif ch == '/':
                    state = State.IN_SLASH          # could be / or // or /*

                elif ch == '!':
                    state = State.IN_NEQ

                elif ch == '=':
                    state = State.IN_EQ

                elif ch == '<':
                    state = State.IN_LT

                elif ch == '>':
                    state = State.IN_GT

                elif ch == '+':
                    result = self._make(TokenType.PLUS, '+', tok_line, tok_col)
                    state  = State.DONE

                elif ch == '-':
                    result = self._make(TokenType.MINUS, '-', tok_line, tok_col)
                    state  = State.DONE

                elif ch == '*':
                    result = self._make(TokenType.STAR, '*', tok_line, tok_col)
                    state  = State.DONE

                elif ch == '(':
                    result = self._make(TokenType.LPAREN, '(', tok_line, tok_col)
                    state  = State.DONE

                elif ch == ')':
                    result = self._make(TokenType.RPAREN, ')', tok_line, tok_col)
                    state  = State.DONE

                elif ch == '{':
                    result = self._make(TokenType.LBRACE, '{', tok_line, tok_col)
                    state  = State.DONE

                elif ch == '}':
                    result = self._make(TokenType.RBRACE, '}', tok_line, tok_col)
                    state  = State.DONE

                elif ch == ';':
                    result = self._make(TokenType.SEMICOLON, ';', tok_line, tok_col)
                    state  = State.DONE

                elif ch == ',':
                    result = self._make(TokenType.COMMA, ',', tok_line, tok_col)
                    state  = State.DONE

                elif ch == '[':
                    result = self._make(TokenType.LBRACKET, '[', tok_line, tok_col)
                    state  = State.DONE

                elif ch == ']':
                    result = self._make(TokenType.RBRACKET, ']', tok_line, tok_col)
                    state  = State.DONE

                elif ch == '\0':
                    result = Token(TokenType.EOF, '', None, tok_line, tok_col)
                    state  = State.DONE

                else:
                    state = State.ERROR

            #  IN_ID: collecting identifier chars 
            elif state == State.IN_ID:
                if ch.isalnum() or ch == '_':
                    lexeme.append(ch)
                else:
                    self._unget()
                    lex_str = ''.join(lexeme)
                    result  = self._make(TokenType.IDENTIFIER, lex_str, tok_line, tok_col)
                    state   = State.DONE

            #  IN_INT: collecting integer digits 
            elif state == State.IN_INT:
                if ch.isdigit():
                    lexeme.append(ch)
                elif ch == '.':
                    lexeme.append(ch)
                    state = State.IN_FLOAT
                else:
                    self._unget()
                    lex_str = ''.join(lexeme)
                    result  = self._make(TokenType.INTEGER, lex_str, tok_line, tok_col, int(lex_str))
                    state   = State.DONE

            #  IN_FLOAT: after decimal point 
            elif state == State.IN_FLOAT:
                if ch.isdigit():
                    lexeme.append(ch)
                else:
                    self._unget()
                    lex_str = ''.join(lexeme)
                    result  = self._make(TokenType.FLOAT, lex_str, tok_line, tok_col, float(lex_str))
                    state   = State.DONE

            #  IN_STRING: inside double-quoted string 
            elif state == State.IN_STRING:
                lexeme.append(ch)
                if ch == '"':
                    lex_str = ''.join(lexeme)
                    result  = Token(TokenType.STRING, lex_str, lex_str[1:-1], tok_line, tok_col)
                    state   = State.DONE
                elif ch == '\0':
                    state = State.ERROR   # unterminated string

            #  IN_SLASH: saw '/' 
            elif state == State.IN_SLASH:
                if ch == '/':
                    lexeme.append(ch)
                    state = State.IN_LINE_CMT
                elif ch == '*':
                    lexeme.append(ch)
                    state = State.IN_BLK_CMT
                else:
                    self._unget()
                    result = self._make(TokenType.SLASH, '/', tok_line, tok_col)
                    state  = State.DONE

            #  IN_LINE_CMT: // style — read until newline 
            elif state == State.IN_LINE_CMT:
                if ch == '\n' or ch == '\0':
                    lex_str = ''.join(lexeme).rstrip()
                    result  = Token(TokenType.COMMENT, lex_str, None, tok_line, tok_col)
                    state   = State.DONE
                else:
                    lexeme.append(ch)

            #  IN_BLK_CMT: /* style — scan for */ 
            elif state == State.IN_BLK_CMT:
                lexeme.append(ch)
                if ch == '*':
                    state = State.IN_BLK_END
                elif ch == '\0':
                    state = State.ERROR   # unterminated block comment

            #  IN_BLK_END: saw '*' inside block comment 
            elif state == State.IN_BLK_END:
                lexeme.append(ch)
                if ch == '/':
                    lex_str = ''.join(lexeme)
                    result  = Token(TokenType.COMMENT, lex_str, None, tok_line, tok_col)
                    state   = State.DONE
                elif ch == '*':
                    pass   # stay — e.g. "/**/"
                else:
                    state = State.IN_BLK_CMT

            #  IN_NEQ: saw '!' 
            elif state == State.IN_NEQ:
                if ch == '=':
                    lexeme.append(ch)
                    result = self._make(TokenType.NEQ, '!=', tok_line, tok_col)
                    state  = State.DONE
                else:
                    self._unget()
                    state = State.ERROR

            #  IN_EQ: saw '=' — could be '==' or assign 
            elif state == State.IN_EQ:
                if ch == '=':
                    lexeme.append(ch)
                    result = self._make(TokenType.EQ, '==', tok_line, tok_col)
                else:
                    self._unget()
                    result = self._make(TokenType.ASSIGN, '=', tok_line, tok_col)
                state = State.DONE

            #  IN_LT: saw '<' 
            elif state == State.IN_LT:
                if ch == '=':
                    lexeme.append(ch)
                    result = self._make(TokenType.LTE, '<=', tok_line, tok_col)
                else:
                    self._unget()
                    result = self._make(TokenType.LT, '<', tok_line, tok_col)
                state = State.DONE

            #  IN_GT: saw '>' 
            elif state == State.IN_GT:
                if ch == '=':
                    lexeme.append(ch)
                    result = self._make(TokenType.GTE, '>=', tok_line, tok_col)
                else:
                    self._unget()
                    result = self._make(TokenType.GT, '>', tok_line, tok_col)
                state = State.DONE

        #  Handle ERROR 
        if state == State.ERROR:
            lex_str = ''.join(lexeme) if lexeme else '?'
            return Token(TokenType.ERROR, lex_str, None, tok_line, tok_col)

        return result


#  Standalone runner 
if __name__ == '__main__':
    import sys
    path = sys.argv[1] if len(sys.argv) > 1 else 'program.pascal'
    src  = open(path).read()
    lexer = StateBased(src)
    toks  = lexer.tokenize()
    print_token_stream(toks, 'Approach 1 — State-Based (Direct Coded)')
