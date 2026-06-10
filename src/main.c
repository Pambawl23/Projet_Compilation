/*
 * main.c — Point d'entrée + implémentations de symboles.h
 * Auteur : Papa Mbaye BA 
 * Usage   : ./sgn_parser <fichier.sgn> [--debug]
 * stdout  → JSON (toujours émis, même en cas d'erreurs)
 * stderr  → messages lisibles pour débogage
 */

#define _POSIX_C_SOURCE 200809L
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "symboles.h"

/* ── Variables globales ── */
Programme g_programme;
ErreurSGN g_erreurs[MAX_ERR];
int       g_nb_erreurs = 0;

/* Fournis par Bison / Flex */
int  yyparse(void);
void yyrestart(FILE *f);
extern FILE *yyin;

/* ================================================================
 * Collecte unifiée des erreurs (LEX / SYN / SEM)
 * ================================================================ */

void ajouter_erreur(const char *type, int ligne, const char *msg)
{
    if (g_nb_erreurs >= MAX_ERR)
        return;
    strncpy(g_erreurs[g_nb_erreurs].type,    type, 15);
    g_erreurs[g_nb_erreurs].ligne = ligne;
    strncpy(g_erreurs[g_nb_erreurs].message, msg,  MAX_STR - 1);
    g_nb_erreurs++;
    fprintf(stderr, "[ERREUR %s] ligne %d : %s\n", type, ligne, msg);
}

/* ================================================================
 * Gestion des niveaux
 * ================================================================ */

void programme_init(Programme *p)
{
    memset(p, 0, sizeof(Programme));
}

Niveau *programme_add_niveau(Programme *p, CodeNiveau code)
{
    int i;
    for (i = 0; i < p->nb_niveaux; i++)
        if (p->niveaux[i].id == code)
            return &p->niveaux[i];

    if (p->nb_niveaux >= MAX_NIV)
        return NULL;

    memset(&p->niveaux[p->nb_niveaux], 0, sizeof(Niveau));
    p->niveaux[p->nb_niveaux].id = code;
    return &p->niveaux[p->nb_niveaux++];
}

/* ================================================================
 * Gestion des étudiants
 * ================================================================ */

Etudiant *niveau_find_etudiant(Niveau *niv, const char *matricule)
{
    int i;
    for (i = 0; i < niv->nb_etudiants; i++)
        if (strcmp(niv->etudiants[i].matricule, matricule) == 0)
            return &niv->etudiants[i];
    return NULL;
}

Etudiant *niveau_add_etudiant(Niveau *niv, const char *matricule, const char *nom)
{
    Etudiant *e;
    if (niv->nb_etudiants >= MAX_ETU)
        return NULL;

    e = &niv->etudiants[niv->nb_etudiants++];
    memset(e, 0, sizeof(Etudiant));
    strncpy(e->matricule, matricule, MAX_STR - 1);
    strncpy(e->nom,       nom,       MAX_STR - 1);
    return e;
}

/* ================================================================
 * Gestion des semestres
 * ================================================================ */

Semestre *etudiant_add_semestre(Etudiant *e, CodeSemestre id)
{
    Semestre *s;
    if (e->nb_semestres >= MAX_SEM)
        return NULL;

    s = &e->semestres[e->nb_semestres++];
    memset(s, 0, sizeof(Semestre));
    s->id = id;
    return s;
}

/* ================================================================
 * Gestion des modules
 * ================================================================ */

int semestre_add_module(Semestre *s, const char *nom, int coef, double note)
{
    Module *m;
    if (s->nb_modules >= MAX_MOD)
        return -1;

    m = &s->modules[s->nb_modules++];
    strncpy(m->nom, nom, MAX_STR - 1);
    m->coef = coef;
    m->note = note;
    return 0;
}

/* ================================================================
 * Calculs — formules du sujet §3.2.2
 * ================================================================ */

/* Formule (1) : moyenne pondérée d'un semestre */
static double semestre_moyenne(Semestre *s)
{
    double somme_pond = 0.0, somme_coef = 0.0;
    int i;
    for (i = 0; i < s->nb_modules; i++) {
        somme_pond += s->modules[i].coef * s->modules[i].note;
        somme_coef += s->modules[i].coef;
    }
    return somme_coef > 0.0 ? somme_pond / somme_coef : 0.0;
}

/* Formule (2) : moyenne arithmétique des moyennes semestrielles */
static double etudiant_moyenne_annuelle(Etudiant *e)
{
    double total = 0.0;
    int i;
    if (e->nb_semestres == 0)
        return 0.0;
    for (i = 0; i < e->nb_semestres; i++)
        total += e->semestres[i].moyenne;
    return total / e->nb_semestres;
}

/* Décision et mention — tableau §3.2.3 */
static void etudiant_set_mention(Etudiant *e)
{
    double m = e->moyenne_annuelle;
    if      (m >= 16.0) { strcpy(e->decision, "Admis");   strcpy(e->mention, "Tres Bien");  }
    else if (m >= 14.0) { strcpy(e->decision, "Admis");   strcpy(e->mention, "Bien");        }
    else if (m >= 12.0) { strcpy(e->decision, "Admis");   strcpy(e->mention, "Assez Bien"); }
    else if (m >= 10.0) { strcpy(e->decision, "Admis");   strcpy(e->mention, "Passable");   }
    else                { strcpy(e->decision, "Ajourne"); strcpy(e->mention, "");            }
}

/* Tri décroissant par moyenne + affectation des rangs */
static void niveau_calcule_rangs(Niveau *niv)
{
    Etudiant tmp;
    int i, j;
    for (i = 0; i < niv->nb_etudiants - 1; i++)
        for (j = 0; j < niv->nb_etudiants - 1 - i; j++)
            if (niv->etudiants[j].moyenne_annuelle < niv->etudiants[j + 1].moyenne_annuelle) {
                tmp                   = niv->etudiants[j];
                niv->etudiants[j]     = niv->etudiants[j + 1];
                niv->etudiants[j + 1] = tmp;
            }
    for (i = 0; i < niv->nb_etudiants; i++)
        niv->etudiants[i].rang = i + 1;
}

/* Orchestration post-parsing */
void programme_calcule_tout(Programme *p)
{
    int ni, ei, si;
    for (ni = 0; ni < p->nb_niveaux; ni++) {
        Niveau *niv = &p->niveaux[ni];
        for (ei = 0; ei < niv->nb_etudiants; ei++) {
            Etudiant *e = &niv->etudiants[ei];
            for (si = 0; si < e->nb_semestres; si++)
                e->semestres[si].moyenne = semestre_moyenne(&e->semestres[si]);
            e->moyenne_annuelle = etudiant_moyenne_annuelle(e);
            etudiant_set_mention(e);
        }
        niveau_calcule_rangs(niv);
    }
}

/* ================================================================
 * Vérification cohérence semestre / niveau
 * L1 → S1,S2 | L2 → S3,S4 | L3 → S5,S6
 * ================================================================ */

int semestre_valide_pour_niveau(CodeSemestre sem, CodeNiveau niv)
{
    switch (niv) {
        case NIV_L1: return (sem == SEM_S1 || sem == SEM_S2);
        case NIV_L2: return (sem == SEM_S3 || sem == SEM_S4);
        case NIV_L3: return (sem == SEM_S5 || sem == SEM_S6);
        default:     return 0;
    }
}

/* ================================================================
 * Sérialisation JSON — format §3.3.2 du sujet
 * Toujours émis, même si des erreurs sont présentes
 * ================================================================ */

static void json_esc(FILE *out, const char *s)
{
    for (; *s; s++) {
        if      (*s == '"')  fputs("\\\"", out);
        else if (*s == '\\') fputs("\\\\", out);
        else                 fputc(*s, out);
    }
}

void programme_to_json(Programme *p, FILE *out)
{
    static const char *NOM_NIV[] = { "", "L1", "L2", "L3" };
    static const char *NOM_SEM[] = { "", "S1", "S2", "S3", "S4", "S5", "S6" };
    int ni, ei, si, mi;

    fprintf(out, "{\n  \"annee\": \"");
    json_esc(out, p->annee);
    fprintf(out, "\",\n  \"niveaux\": [\n");

    for (ni = 0; ni < p->nb_niveaux; ni++) {
        Niveau *niv = &p->niveaux[ni];
        fprintf(out, "    {\n      \"niveau\": \"%s\",\n      \"etudiants\": [\n",
                NOM_NIV[niv->id]);

        for (ei = 0; ei < niv->nb_etudiants; ei++) {
            Etudiant *e = &niv->etudiants[ei];
            fprintf(out, "        {\n          \"matricule\": \"");
            json_esc(out, e->matricule);
            fprintf(out, "\",\n          \"nom\": \"");
            json_esc(out, e->nom);
            fprintf(out, "\",\n          \"semestres\": [\n");

            for (si = 0; si < e->nb_semestres; si++) {
                Semestre *s = &e->semestres[si];
                fprintf(out, "            {\n              \"id\": \"%s\",\n"
                             "              \"modules\": [\n", NOM_SEM[s->id]);

                for (mi = 0; mi < s->nb_modules; mi++) {
                    Module *m = &s->modules[mi];
                    fprintf(out, "                {\"nom\": \"");
                    json_esc(out, m->nom);
                    fprintf(out, "\", \"coef\": %d, \"note\": %.1f}%s\n",
                            m->coef, m->note, mi < s->nb_modules - 1 ? "," : "");
                }
                fprintf(out, "              ],\n              \"moyenne\": %.2f\n"
                             "            }%s\n",
                        s->moyenne, si < e->nb_semestres - 1 ? "," : "");
            }

            fprintf(out,
                    "          ],\n"
                    "          \"moyenne_annuelle\": %.2f,\n"
                    "          \"mention\": \"%s\",\n"
                    "          \"decision\": \"%s\",\n"
                    "          \"rang\": %d\n"
                    "        }%s\n",
                    e->moyenne_annuelle, e->mention, e->decision, e->rang,
                    ei < niv->nb_etudiants - 1 ? "," : "");
        }
        fprintf(out, "      ]\n    }%s\n", ni < p->nb_niveaux - 1 ? "," : "");
    }

    /* Toutes les erreurs (LEX + SYN + SEM) dans le même tableau JSON */
    fprintf(out, "  ],\n  \"erreurs\": [\n");
    for (ni = 0; ni < g_nb_erreurs; ni++) {
        fprintf(out, "    {\"type\": \"%s\", \"ligne\": %d, \"message\": \"",
                g_erreurs[ni].type, g_erreurs[ni].ligne);
        json_esc(out, g_erreurs[ni].message);
        fprintf(out, "\"}%s\n", ni < g_nb_erreurs - 1 ? "," : "");
    }
    fprintf(out, "  ]\n}\n");
}

/* ================================================================
 * main
 * ================================================================ */

int main(int argc, char *argv[])
{
    int         debug   = 0;
    const char *fichier = NULL;
    FILE       *fp      = NULL;
    int         rc;
    int         i;

    for (i = 1; i < argc; i++) {
        if      (strcmp(argv[i], "--debug") == 0) debug = 1;
        else if (argv[i][0] != '-')               fichier = argv[i];
        else {
            fprintf(stderr, "Option inconnue : %s\n", argv[i]);
            return EXIT_FAILURE;
        }
    }

    if (fichier) {
        fp = fopen(fichier, "r");
        if (!fp) { perror(fichier); return EXIT_FAILURE; }
    }

    yyrestart(fp ? fp : stdin);
    programme_init(&g_programme);

    rc = yyparse();
    if (fp) fclose(fp);

    if (debug)
        fprintf(stderr, "[DEBUG] parse rc=%d, nb_erreurs=%d\n", rc, g_nb_erreurs);

    /* JSON toujours émis — Python le lit même en cas d'erreurs */
    programme_to_json(&g_programme, stdout);
    fflush(stdout);

    return (rc == 0 && g_nb_erreurs == 0) ? EXIT_SUCCESS : EXIT_FAILURE;
}
