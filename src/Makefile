# Makefile — Projet SGN (Système de Gestion des Notes)
# Auteurs : Papa Mbaye BA
# Cibles  : make | make test | make clean | make distclean
# Compatibilité : Ubuntu/Debian et macOS (Homebrew ou Xcode bison)

CC     = gcc
CFLAGS = -Wall -Wextra -g -std=c99 -D_POSIX_C_SOURCE=200809L

TARGET  = sgn_parser
TESTDIR = ../tests
OBJS    = parser.tab.o lex.yy.o main.o

# ── Détection de l'OS ─────────────────────────────────────────────
OS := $(shell uname)

ifeq ($(OS), Darwin)
    # macOS : préférer le bison Homebrew (moderne) si disponible,
    # sinon utiliser celui de Xcode (vieux, sans -Wall)
    BREW_BISON := $(shell brew --prefix bison 2>/dev/null)/bin/bison
    ifeq ($(shell test -x "$(BREW_BISON)" && echo yes), yes)
        BISON      = $(BREW_BISON)
        BISON_WARN = -Wall
    else
        BISON      = bison
        BISON_WARN =
    endif
    FLEX    = flex
    LDFLAGS = -ll -lm
else
    # Linux (Ubuntu/Debian)
    BISON      = bison
    BISON_WARN = -Wall
    FLEX       = flex
    LDFLAGS    = -lfl -lm
endif

# ── Cible principale ──────────────────────────────────────────────
all: $(TARGET)
	@cp -f $(TARGET) ../gui/$(TARGET)
	@echo "  ✓ $(TARGET) copié dans gui/"

$(TARGET): $(OBJS)
	$(CC) $(CFLAGS) -o $@ $^ $(LDFLAGS)
	@echo "  ✓ Compilation réussie → $(TARGET)"
	@echo "  Usage : ./$(TARGET) <fichier.sgn> [--debug]"

# ── Génération Bison / Flex ───────────────────────────────────────
parser.tab.c parser.tab.h: parser.y
	$(BISON) -d $(BISON_WARN) $<

lex.yy.c: lexer.l parser.tab.h
	$(FLEX) $<

# ── Compilation des objets ────────────────────────────────────────
parser.tab.o: parser.tab.c parser.tab.h symboles.h
	$(CC) $(CFLAGS) -c $<

lex.yy.o: lex.yy.c parser.tab.h symboles.h
	$(CC) $(CFLAGS) -Wno-sign-compare -c $<

main.o: main.c symboles.h
	$(CC) $(CFLAGS) -c $<

# ── Tests ─────────────────────────────────────────────────────────
test: $(TARGET)
	@echo "=== Test 1 : fichier valide ==="
	./$(TARGET) $(TESTDIR)/test_valide.sgn | python3 -m json.tool
	@echo ""
	@echo "=== Test 2 : erreurs lexicales ==="
	-./$(TARGET) $(TESTDIR)/test_erreur_lex.sgn 2>/dev/null | python3 -m json.tool
	@echo ""
	@echo "=== Test 3 : erreurs syntaxiques ==="
	-./$(TARGET) $(TESTDIR)/test_erreur_syn.sgn 2>/dev/null | python3 -m json.tool
	@echo ""
	@echo "=== Test 4 : erreurs sémantiques ==="
	-./$(TARGET) $(TESTDIR)/test_erreur_sem.sgn 2>/dev/null | python3 -m json.tool

# ── Nettoyage ─────────────────────────────────────────────────────
clean:
	rm -f $(OBJS) parser.tab.c parser.tab.h lex.yy.c

distclean: clean
	rm -f $(TARGET) ../gui/$(TARGET)

.PHONY: all test clean distclean
