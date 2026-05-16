%{
#include <stdio.h>
#include <stdlib.h>

#define T_PROGRAM 1
#define T_VAR 2
#define T_INTEGER 3
#define T_REAL 4
#define T_FUNCTION 5
#define T_PROCEDURE 6
#define T_BEGIN 7
#define T_END 8
#define T_IF 9
#define T_THEN 10
#define T_ELSE 11
#define T_WHILE 12
#define T_DO 13
#define T_ARRAY 14
#define T_OF 15
#define T_NOT 16
#define T_ID 17
#define T_NUM 18
#define T_ASSIGNOP 19
#define T_RELOP 20
#define T_ADDOP 21
#define T_MULOP 22
#define T_PUNCT 23

int line_number = 1;
extern FILE *yyin;
%}

/* Pascal case-insensitive */
%option caseless

/* Definitions */
DIGIT    [0-9]
LETTER   [a-zA-Z]
ID       {LETTER}({LETTER}|{DIGIT})*
NUM      {DIGIT}+(\.{DIGIT}+)?([eE][+-]?{DIGIT}+)?

%%

[ \t\r]+          { }
\n                { line_number++; }
"{"               {
                    int b;
                    while((b = input()) != '}' && b != EOF) {
                        if(b == '\n') line_number++;
                    }
                    if(b == EOF) {
                        printf("Error: Unterminated comment at line %d\n", line_number);
                    }
                  }

"program"         { return T_PROGRAM; }
"var"             { return T_VAR; }
"integer"         { return T_INTEGER; }
"real"            { return T_REAL; }
"function"        { return T_FUNCTION; }
"procedure"       { return T_PROCEDURE; }
"begin"           { return T_BEGIN; }
"end"             { return T_END; }
"if"              { return T_IF; }
"then"            { return T_THEN; }
"else"            { return T_ELSE; }
"while"           { return T_WHILE; }
"do"              { return T_DO; }
"array"           { return T_ARRAY; }
"of"              { return T_OF; }
"not"             { return T_NOT; }

":="              { return T_ASSIGNOP; }

"="|"<>"|"<="|"<"|">="|">" { return T_RELOP; }

"+"|"-"|"or"      { return T_ADDOP; }

"*"|"/"|"div"|"mod"|"and" { return T_MULOP; }

"("|")"|"["|"]"|","|";"|":"|".."|"." { return T_PUNCT; }

{ID}              { return T_ID; }
{NUM}             { return T_NUM; }

.                 {
                    printf("Lexical Error at line %d: Unexpected character '%s'\n", line_number, yytext);
                  }

%%

int yywrap() {
    return 1;
}

/* Token name for better output */
char* token_name(int token) {
    switch(token) {
        case T_PROGRAM: return "PROGRAM";
        case T_VAR: return "VAR";
        case T_INTEGER: return "INTEGER";
        case T_REAL: return "REAL";
        case T_FUNCTION: return "FUNCTION";
        case T_PROCEDURE: return "PROCEDURE";
        case T_BEGIN: return "BEGIN";
        case T_END: return "END";
        case T_IF: return "IF";
        case T_THEN: return "THEN";
        case T_ELSE: return "ELSE";
        case T_WHILE: return "WHILE";
        case T_DO: return "DO";
        case T_ARRAY: return "ARRAY";
        case T_OF: return "OF";
        case T_NOT: return "NOT";
        case T_ID: return "IDENTIFIER";
        case T_NUM: return "NUMBER";
        case T_ASSIGNOP: return "ASSIGNOP";
        case T_RELOP: return "RELOP";
        case T_ADDOP: return "ADDOP";
        case T_MULOP: return "MULOP";
        case T_PUNCT: return "PUNCT";
        default: return "UNKNOWN";
    }
}

/* Main Function */
int main(int argc, char **argv) {
    if(argc > 1) {
        yyin = fopen(argv[1], "r");
        if(!yyin) {
            perror(argv[1]);
            return 1;
        }
    }

    int token;
    while((token = yylex())) {
        printf("Token: %-12s | Lexeme: %s\n", token_name(token), yytext);
    }

    return 0;
}