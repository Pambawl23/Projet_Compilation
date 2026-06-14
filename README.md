# SGN — Système de Gestion des Notes

**Module** : Compilation — GeIT2

**Année académique** : 2025–2026

**Auteurs** : Papa Mbaye BA & Gilbert Ngor Thiomby DIOUF


**Date de Soumission** :  15 Juin 2026

---

## Présentation

Ce projet implémente un **Système de Gestion des Notes (SGN)** pour les trois
premiers niveaux d'une formation universitaire (L1, L2, L3). Il met en
pratique les concepts fondamentaux de la théorie des langages et de la
compilation :

- définition d'un langage dédié (DSL) `.sgn` décrivant des notes d'étudiants,
- analyse lexicale avec **Flex**,
- analyse syntaxique et sémantique avec **Bison**,
- construction d'une table de symboles,
- calcul automatique des moyennes, mentions et décisions de passage,
- interface graphique de test en **Python/PyQt6**.

---
## Architecture du projet

```
sgn_project/
├── src/
│   ├── lexer.l           # Analyseur lexical Flex
│   ├── parser.y           # Analyseur syntaxique/sémantique Bison
│   ├── symboles.h         # Structures de données et table de symboles
│   ├── symboles.c          # Implémentation (calculs, JSON, rangs)
│   ├── ast.h / ast.c       # Arbre syntaxique abstrait (mode --debug)
│   ├── main.c              # Point d'entrée
│   └── Makefile            # Compilation automatisée
│
├── gui/
│   ├── app.py              # Interface PyQt6 principale
│   ├── interface.py        # Widgets réutilisables (StatCard, BadgeDecision)
│   └── parser_bridge.py    # Pont subprocess Python ↔ binaire C
│
├── tests/
│   ├── test_valide.sgn
│   ├── test_erreur_lex.sgn
│   ├── test_erreur_syn.sgn
│   └── test_erreur_sem.sgn
│
├── rapport/
│   ├── rapport.pdf
│   └── rapport.tex
│
└── README.md
```

## Langage `.sgn` — aperçu

```sgn
-- Fichier notes : Annee academique 2025-2026
ANNEE "2025-2026"

NIVEAU L1 {
    ETUDIANT {
        MATRICULE : "L1-2025-001"
        NOM : "DIALLO Mamadou"
        PRENOM : "Mamadou"
        SEMESTRE S1 {
            MODULE "Algorithmique" COEF 3 NOTE 14.5
            MODULE "Mathematiques" COEF 4 NOTE 12.0
        }
    }
}
```

La grammaire formelle complète (BNF) et la liste des tokens sont détaillées
dans le rapport technique (`rapport/rapport.pdf`).

## Prérequis

### Linux (Ubuntu/Debian)

```bash
sudo apt update
sudo apt install flex bison gcc python3 python3-pip
pip3 install PyQt6 --break-system-packages
```

### macOS

Le `bison` fourni par Xcode est une vieille version (2.3) qui ne supporte pas
toutes les directives modernes. Installez la version GNU via Homebrew :

```bash
brew install flex bison
echo 'export PATH="/opt/homebrew/opt/bison/bin:$PATH"' >> ~/.zshrc   # Apple Silicon
echo 'export PATH="/opt/homebrew/opt/bison/bin:$PATH"' >> ~/.zshrc   # Intel : /usr/local/opt/bison/bin
source ~/.zshrc

python3 -m pip install PyQt6
```

Vérifiez les versions :

```bash
bison --version   # doit afficher 3.x
flex --version    # doit afficher 2.6+
python3 --version # 3.10+
```

---

## Compilation

```bash
cd src/
make
```

Cette commande :

1. génère `parser.tab.c` / `parser.tab.h` via Bison,
2. génère `lex.yy.c` via Flex,
3. compile et lie l'ensemble en un binaire `sgn_parser`.

En cas de modification du code source, recompilez proprement avec :

```bash
make distclean   # supprime les fichiers générés ET le binaire
make
```

---

## Utilisation en ligne de commande

```bash
cd src/
./sgn_parser <fichier.sgn>            # JSON sur stdout, erreurs sur stderr
./sgn_parser <fichier.sgn> --debug    # affiche en plus l'AST sur stderr
./sgn_parser --help                   # aide
```

Exemple :

```bash
./sgn_parser ../tests/test_valide.sgn
```

---

## Tests automatisés

```bash
cd src/
make test
```

Cette cible exécute les 4 jeux de tests fournis dans `tests/` :

| Fichier                  | Objectif                                                        |
|--------------------------|------------------------------------------------------------------|
| `test_valide.sgn`        | Parsing complet sans erreur — vérifie le JSON et les calculs    |
| `test_erreur_lex.sgn`    | Chaîne non terminée, caractères illégaux (`@`, `#`)             |
| `test_erreur_syn.sgn`    | Champ obligatoire manquant (erreur syntaxique)                  |
| `test_erreur_sem.sgn`    | Note hors `[0,20]`, coefficient `< 1`, semestre/niveau incohérent, doublon de matricule |

Pour tester uniquement l'analyseur lexical :

```bash
make test_lexer
```

---

## Interface graphique (PyQt6)

```bash
cd gui/
python3 app.py
```

Fonctionnalités :

- **Parcourir** pour charger un fichier `.sgn`,
- **éditeur intégré** : modification directe avant analyse,
- **▶ Analyser** : appelle `sgn_parser` via `subprocess` et affiche le résultat,
- **tableau de résultats** : matricule, nom, niveau, semestre, moyennes,
  rang, mention (colorée), décision,
- **zone d'erreurs** : affiche les erreurs lexicales / syntaxiques /
  sémantiques avec leur numéro de ligne,
- **export CSV ou TXT** : sauvegarde le tableau de résultats.

`parser_bridge.py` recherche automatiquement le binaire `sgn_parser` dans
plusieurs emplacements (`gui/`, `../src/`). Si le binaire n'est pas trouvé,
un message clair est affiché dans la zone d'erreurs.

---



---



---

## Flux d'exécution

```
Fichier .sgn
     │
     ▼
   Flex (lexer.l) ──► tokens
     │
     ▼
   Bison (parser.y) ──► AST + table de symboles + vérifications sémantiques
     │
     ▼
   symboles.c ──► calculs (moyennes, rang, mention, décision)
     │
     ▼
   JSON sur stdout            erreurs sur stderr
     │
     ▼
   Interface Python (subprocess, parser_bridge.py)
     │
     ▼
   Tableau de résultats + export CSV
```

---

## Format de sortie JSON

Le binaire `sgn_parser` émet sur **stdout** un JSON conforme au format
défini section 3.3.2 du sujet :

```json
{
  "annee": "2025-2026",
  "niveaux": [
    {
      "niveau": "L1",
      "etudiants": [
        {
          "matricule": "L1-2025-001",
          "nom": "DIALLO Mamadou",
          "prenom": "Mamadou",
          "semestres": [
            {
              "id": "S1",
              "modules": [
                {"nom": "Algorithmique", "coef": 3, "note": 14.5}
              ],
              "moyenne": 14.07
            }
          ],
          "moyenne_annuelle": 14.07,
          "mention": "Assez Bien",
          "decision": "Admis",
          "rang": 1
        }
      ]
    }
  ],
  "erreurs": []
}
```

Les erreurs lexicales, syntaxiques et sémantiques sont écrites sur
**stderr** au format :

```
[ERREUR LEXICALE]    ligne <N> : <message>
[ERREUR SYNTAXIQUE]  ligne <N> : <message>
[ERREUR SEMANTIQUE]  ligne <N> : <message>
```

et sont également recensées dans le tableau `erreurs` du JSON.

---


## Nettoyage

```bash
make clean      # supprime les fichiers générés (.o, lex.yy.c, parser.tab.*)
make distclean  # supprime également le binaire sgn_parser
```

---

## Références

- *Flex & Bison*, John Levine, O'Reilly, 2009.
- *Compilers: Principles, Techniques, and Tools* (Aho, Lam, Sethi, Ullman),
  Pearson, 2006.
- Documentation Flex : <https://github.com/westes/flex>
- Documentation Bison : <https://www.gnu.org/software/bison/manual/>
- Python subprocess : <https://docs.python.org/3/library/subprocess.html>
