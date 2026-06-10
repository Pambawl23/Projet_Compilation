/*
 * parser.y — Analyseur syntaxique/semantique SGN (Bison LALR-1)
 * Auteur : Papa Mbaye BA
 *
 * Grammaire (BNF sujet section 2.2) :
 *   programme       ::= ANNEE STRING liste_niveaux
 *   liste_niveaux   ::= niveau | liste_niveaux niveau
 *   niveau          ::= NIVEAU_KW id_niveau '{' liste_etudiants '}'
 *   id_niveau       ::= L1 | L2 | L3
 *   liste_etudiants ::= etudiant | liste_etudiants etudiant
 *   etudiant        ::= ETUDIANT_KW '{' champs_etudiant liste_semestres '}'
 *   champs_etudiant ::= MATRICULE ':' STRING NOM ':' STRING [PRENOM ':' STRING]
 *   liste_semestres ::= semestre | liste_semestres semestre
 *   semestre        ::= SEMESTRE_KW id_sem '{' liste_modules '}'
 *   id_sem          ::= S1|S2|S3|S4|S5|S6
 *   liste_modules   ::= module_item | liste_modules module_item
 *   module_item     ::= MODULE STRING COEF ENTIER NOTE REEL
 *
 * Verifications semantiques :
 *   1. Note dans [0,20]
 *   2. Coefficient >= 1
 *   3. Doublon de matricule par niveau
 *   4. Coherence semestre/niveau (L1->S1,S2 | L2->S3,S4 | L3->S5,S6)
 */

%{
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "symboles.h"

extern int  yylineno;
int  yylex(void);
void yyerror(const char *msg);

static Niveau    *ctx_niv      = NULL;
static Etudiant  *ctx_etu      = NULL;
static Semestre  *ctx_sem      = NULL;
static CodeNiveau ctx_code_niv = 0;
%}

%define parse.error verbose

%union { double reel; int entier; char *chaine; }

%token ANNEE NIVEAU_KW ETUDIANT_KW MATRICULE_KW NOM_KW PRENOM_KW
%token SEMESTRE_KW MODULE_KW COEF_KW NOTE_KW
%token NIV_L1_TOK NIV_L2_TOK NIV_L3_TOK
%token SEM_S1_TOK SEM_S2_TOK SEM_S3_TOK SEM_S4_TOK SEM_S5_TOK SEM_S6_TOK

%token <reel>   REEL
%token <entier> ENTIER
%token <chaine> STRING_TOK

%type <entier> id_niveau id_sem

%start programme

%%

programme
    : ANNEE STRING_TOK liste_niveaux
        {
            strncpy(g_programme.annee, $2, MAX_STR - 1);
            free($2);
            programme_calcule_tout(&g_programme);
        }
    ;

liste_niveaux
    : niveau
    | liste_niveaux niveau
    ;

niveau
    : NIVEAU_KW id_niveau '{' liste_etudiants '}'
        { ctx_niv = NULL; }
    ;

id_niveau
    : NIV_L1_TOK { ctx_code_niv=NIV_L1; ctx_niv=programme_add_niveau(&g_programme,NIV_L1); $$=NIV_L1; }
    | NIV_L2_TOK { ctx_code_niv=NIV_L2; ctx_niv=programme_add_niveau(&g_programme,NIV_L2); $$=NIV_L2; }
    | NIV_L3_TOK { ctx_code_niv=NIV_L3; ctx_niv=programme_add_niveau(&g_programme,NIV_L3); $$=NIV_L3; }
    ;

liste_etudiants
    : etudiant
    | liste_etudiants etudiant
    ;

etudiant
    : ETUDIANT_KW '{' champs_etudiant liste_semestres '}'
        { ctx_etu = NULL; }
    ;

/*
 * champs_etudiant : MATRICULE + NOM obligatoires, PRENOM optionnel.
 * Verification 3 : doublon de matricule dans le niveau courant.
 */
champs_etudiant
    : MATRICULE_KW ':' STRING_TOK
      NOM_KW       ':' STRING_TOK
      prenom_opt
        {
            char msg[MAX_STR];
            if (ctx_niv && niveau_find_etudiant(ctx_niv, $3)) {
                snprintf(msg, MAX_STR,
                    "doublon matricule \"%s\" dans le niveau", $3);
                ajouter_erreur("SEM", yylineno, msg);
                ctx_etu = NULL;
            } else if (ctx_niv) {
                ctx_etu = niveau_add_etudiant(ctx_niv, $3, $6);
            }
            free($3); free($6);
        }
    ;

prenom_opt
    : %empty
    | PRENOM_KW ':' STRING_TOK  { free($3); }
    ;

liste_semestres
    : semestre
    | liste_semestres semestre
    ;

/*
 * Mid-rule action apres id_sem : cree le semestre avant de parser les modules.
 * Verification 4 : coherence semestre/niveau.
 */
semestre
    : SEMESTRE_KW id_sem
        {
            CodeSemestre cs = (CodeSemestre)$2;
            char msg[MAX_STR];
            const char *NS[] = {"","S1","S2","S3","S4","S5","S6"};
            const char *NN[] = {"","L1","L2","L3"};
            if (!semestre_valide_pour_niveau(cs, ctx_code_niv)) {
                snprintf(msg, MAX_STR,
                    "semestre %s invalide pour niveau %s",
                    NS[cs], NN[(int)ctx_code_niv]);
                ajouter_erreur("SEM", yylineno, msg);
            }
            ctx_sem = ctx_etu ? etudiant_add_semestre(ctx_etu, cs) : NULL;
        }
      '{' liste_modules '}'
        { ctx_sem = NULL; }
    ;

id_sem
    : SEM_S1_TOK { $$=SEM_S1; }
    | SEM_S2_TOK { $$=SEM_S2; }
    | SEM_S3_TOK { $$=SEM_S3; }
    | SEM_S4_TOK { $$=SEM_S4; }
    | SEM_S5_TOK { $$=SEM_S5; }
    | SEM_S6_TOK { $$=SEM_S6; }
    ;

liste_modules
    : module_item
    | liste_modules module_item
    ;

/*
 * Verifications 1 & 2 : note dans [0,20] et coefficient >= 1.
 */
module_item
    : MODULE_KW STRING_TOK COEF_KW ENTIER NOTE_KW REEL
        {
            char msg[MAX_STR];
            if ($6 < 0.0 || $6 > 20.0) {
                snprintf(msg, MAX_STR,
                    "note %.2f hors [0,20] pour \"%s\"", $6, $2);
                ajouter_erreur("SEM", yylineno, msg);
            }
            if ($4 < 1) {
                snprintf(msg, MAX_STR,
                    "coefficient %d invalide (doit etre >= 1) pour \"%s\"", $4, $2);
                ajouter_erreur("SEM", yylineno, msg);
            }
            if (ctx_sem) semestre_add_module(ctx_sem, $2, $4, $6);
            free($2);
        }
    ;

%%

void yyerror(const char *msg)
{
    ajouter_erreur("SYN", yylineno, msg);
}
