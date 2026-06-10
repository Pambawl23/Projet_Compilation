/*
 * lexer.l — Analyseur lexical SGN (Flex)
 * Auteur : Papa Mbaye BA
 * Erreurs lexicales : collectées dans g_erreurs[] via ajouter_erreur()
 */

%{
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "parser.tab.h"
#include "symboles.h"

static char *strip_quotes(const char *s)
{
    size_t n = strlen(s);
    char  *r = malloc(n - 1);
    if (!r) { perror("malloc"); exit(EXIT_FAILURE); }
    memcpy(r, s + 1, n - 2);
    r[n - 2] = '\0';
    return r;
}
%}

%option noyywrap yylineno warn noinput nounput

BLANC    [ \t\r]+
NL       \n
NOMBRE   [0-9]+(\.[0-9]+)?
STR      \"[^\"\n]*\"
COMMENT  "--"[^\n]*

%%

{COMMENT}   { /* commentaire ignoré */ }
{BLANC}     { /* blancs ignorés      */ }
{NL}        { /* saut de ligne       */ }

"ANNEE"     { return ANNEE;        }
"NIVEAU"    { return NIVEAU_KW;    }
"ETUDIANT"  { return ETUDIANT_KW;  }
"MATRICULE" { return MATRICULE_KW; }
"NOM"       { return NOM_KW;       }
"PRENOM"    { return PRENOM_KW;    }
"SEMESTRE"  { return SEMESTRE_KW;  }
"MODULE"    { return MODULE_KW;    }
"COEF"      { return COEF_KW;      }
"NOTE"      { return NOTE_KW;      }

"L1"        { return NIV_L1_TOK; }
"L2"        { return NIV_L2_TOK; }
"L3"        { return NIV_L3_TOK; }
"S1"        { return SEM_S1_TOK; }
"S2"        { return SEM_S2_TOK; }
"S3"        { return SEM_S3_TOK; }
"S4"        { return SEM_S4_TOK; }
"S5"        { return SEM_S5_TOK; }
"S6"        { return SEM_S6_TOK; }

{NOMBRE}    {
                if (strchr(yytext, '.')) {
                    yylval.reel   = atof(yytext); return REEL;
                } else {
                    yylval.entier = atoi(yytext); return ENTIER;
                }
            }

{STR}       { yylval.chaine = strip_quotes(yytext); return STRING_TOK; }

\"[^\"\n]*\n {
                char msg[MAX_STR];
                snprintf(msg, MAX_STR, "chaine non terminee a la ligne %d", yylineno);
                ajouter_erreur("LEX", yylineno, msg);
            }

":"         { return ':'; }
"{"         { return '{'; }
"}"         { return '}'; }

.           {
                char msg[MAX_STR];
                snprintf(msg, MAX_STR,
                    "caractere illegal '%s' (ASCII %d)", yytext, (unsigned char)yytext[0]);
                ajouter_erreur("LEX", yylineno, msg);
            }

%%
