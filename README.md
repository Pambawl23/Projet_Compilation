# SGN — Système de Gestion des Notes
**Module** : Compilation M1 Informatique | **Auteurs** : [NOM1] & [NOM2] | **Juin 2026**

## Prérequis
```bash
sudo apt install flex bison gcc python3 python3-pyqt6
```

## Compilation (Linux)
```bash
cd src/
make          # génère sgn_parser et le copie automatiquement dans gui/
```

## Tests en ligne de commande
```bash
cd src/
make test     # lance les 4 jeux de tests
```

## Interface graphique
```bash
cd gui/
python3 app.py
```

## Architecture
```
sgn_project/
├── src/
│   ├── lexer.l         # Analyseur lexical Flex
│   ├── parser.y        # Analyseur syntaxique/sémantique Bison
│   ├── symboles.h      # Table de symboles (header-only, sans symboles.c)
│   ├── main.c          # Point d'entrée
│   └── Makefile        # Copie sgn_parser → gui/ après compilation
├── gui/
│   ├── app.py          # Interface PyQt6 principale
│   ├── interface.py    # Widgets réutilisables (StatCard, BadgeDecision)
│   ├── parser_bridge.py# Pont subprocess Python ↔ binaire C
│   └── sgn_parser      # Binaire copié par make
├── tests/
│   ├── test_valide.sgn
│   ├── test_erreur_lex.sgn
│   ├── test_erreur_syn.sgn
│   └── test_erreur_sem.sgn
└── README.md
```

## Flux d'exécution
```
Fichier .sgn → Flex (tokens) → Bison (AST/sémantique) → JSON stdout
                                                              ↓
                                              Interface Python (subprocess)
                                                              ↓
                                              Tableau résultats + export CSV/TXT
```

## Format de sortie JSON
Le binaire `sgn_parser` émet sur **stdout** un JSON conforme à §3.3.2 du sujet.
Les erreurs lexicales/syntaxiques/sémantiques vont sur **stderr**.

## Nettoyage
```bash
make clean      # supprime les fichiers générés (.o, lex.yy.c, parser.tab.*)
make distclean  # supprime aussi sgn_parser et gui/sgn_parser
```
