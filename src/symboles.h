/*
 * symboles.h — Déclarations SGN (structures, constantes, prototypes)
 * Auteur : Papa Mbaye BA
 */
#ifndef SYMBOLES_H
#define SYMBOLES_H

#include <stdio.h>
#include <stdlib.h>
#include <string.h>

/* ── Constantes ── */
#define MAX_MOD  64
#define MAX_SEM   6
#define MAX_ETU 256
#define MAX_NIV   3
#define MAX_ERR 256   /* lex + syn + sem peuvent s'accumuler */
#define MAX_STR 256

/* ── Énumérations ── */
typedef enum { NIV_L1 = 1, NIV_L2 = 2, NIV_L3 = 3 } CodeNiveau;
typedef enum {
    SEM_S1 = 1, SEM_S2 = 2, SEM_S3 = 3,
    SEM_S4 = 4, SEM_S5 = 5, SEM_S6 = 6
} CodeSemestre;

/* ── Structures ── */
typedef struct {
    char   nom[MAX_STR];
    int    coef;
    double note;
} Module;

typedef struct {
    CodeSemestre id;
    Module       modules[MAX_MOD];
    int          nb_modules;
    double       moyenne;
} Semestre;

typedef struct {
    char     matricule[MAX_STR];
    char     nom[MAX_STR];
    Semestre semestres[MAX_SEM];
    int      nb_semestres;
    double   moyenne_annuelle;
    char     mention[32];
    char     decision[16];
    int      rang;
} Etudiant;

typedef struct {
    CodeNiveau id;
    Etudiant   etudiants[MAX_ETU];
    int        nb_etudiants;
} Niveau;

typedef struct {
    char   annee[MAX_STR];
    Niveau niveaux[MAX_NIV];
    int    nb_niveaux;
} Programme;

typedef struct {
    int  ligne;
    char type[16];     /* "LEX", "SYN", "SEM" */
    char message[MAX_STR];
} ErreurSGN;

/* ── Variables globales (définies dans main.c) ── */
extern Programme g_programme;
extern ErreurSGN g_erreurs[MAX_ERR];
extern int       g_nb_erreurs;

/* ── Prototypes ── */
void      programme_init(Programme *p);
Niveau   *programme_add_niveau(Programme *p, CodeNiveau code);
Etudiant *niveau_find_etudiant(Niveau *niv, const char *matricule);
Etudiant *niveau_add_etudiant(Niveau *niv, const char *matricule, const char *nom);
Semestre *etudiant_add_semestre(Etudiant *e, CodeSemestre id);
int       semestre_add_module(Semestre *s, const char *nom, int coef, double note);
void      programme_calcule_tout(Programme *p);
int       semestre_valide_pour_niveau(CodeSemestre sem, CodeNiveau niv);
void      ajouter_erreur(const char *type, int ligne, const char *msg);
void      programme_to_json(Programme *p, FILE *out);

#endif /* SYMBOLES_H */
