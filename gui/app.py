# ================================================================
# app.py — Application principale SGN (PyQt6)
# Auteurs : Gilbert Ngor Thiomby DIOUF
# Usage   : python3 app.py
# ================================================================
import sys, os, csv, json
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QPlainTextEdit, QFileDialog, QMessageBox,
    QTabWidget, QTableWidget, QTableWidgetItem, QHeaderView,
    QAbstractItemView, QSplitter, QFrame, QSizePolicy
)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui  import QColor, QFont, QIcon
from parser_bridge import analyser

# ── Palette ───────────────────────────────────────────────────────
BG, SURFACE, SURFACE2 = "#0b1326", "#111827", "#1e2840"
BORDER                = "#2a3550"
BLUE, BLUE_DIM        = "#4d8eff", "#1a3a6e"
RED,  RED_DIM         = "#ff5451", "#3a0f0e"
GREEN                 = "#10B981"
AMBER                 = "#F59E0B"
TEXT, MUTED, FAINT    = "#dae2fd", "#6b7a99", "#2e3f60"
MONO                  = "Menlo, Monaco, Courier New, monospace"

MENTION_COULEUR = {
    "Tres Bien":  GREEN,
    "Bien":       GREEN,
    "Assez Bien": "#adc6ff",
    "Passable":   AMBER,
    "":           RED,
}

SS = f"""
/* ── Base ── */
QMainWindow, QWidget {{
    background: {BG};
    color: {TEXT};
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
    font-size: 13px;
}}

/* ── Barre de titre / toolbar ── */
QFrame#toolbar {{
    background: {SURFACE};
    border-bottom: 1px solid {BORDER};
    border-radius: 0px;
}}

/* ── Panneau fichier ── */
QFrame#file_panel {{
    background: {SURFACE2};
    border: 1px solid {BORDER};
    border-radius: 6px;
}}
QLabel#drop_label {{
    color: {MUTED};
    font-size: 12px;
}}
QLabel#file_name {{
    color: {TEXT};
    font-weight: 600;
    font-size: 13px;
}}

/* ── Éditeur ── */
QPlainTextEdit {{
    background: {SURFACE};
    border: 1px solid {BORDER};
    border-radius: 4px;
    font-family: {MONO};
    font-size: 12px;
    color: {TEXT};
    selection-background-color: {BLUE_DIM};
}}
QPlainTextEdit:focus {{
    border-color: {BLUE};
}}

/* ── Onglets ── */
QTabWidget::pane {{
    border: 1px solid {BORDER};
    border-radius: 0 4px 4px 4px;
    background: {SURFACE};
}}
QTabBar::tab {{
    background: {BG};
    color: {MUTED};
    padding: 7px 20px;
    border: 1px solid {BORDER};
    border-bottom: none;
    border-radius: 4px 4px 0 0;
    margin-right: 2px;
    font-size: 12px;
}}
QTabBar::tab:selected {{
    background: {SURFACE};
    color: {TEXT};
    font-weight: 600;
}}
QTabBar::tab:hover:!selected {{
    background: {SURFACE2};
    color: {TEXT};
}}

/* ── Tableau ── */
QTableWidget {{
    background: {SURFACE};
    border: none;
    gridline-color: {BORDER};
    outline: none;
}}
QTableWidget::item {{
    padding: 6px 10px;
    border-bottom: 1px solid {BORDER};
}}
QTableWidget::item:selected {{
    background: {BLUE_DIM};
    color: {TEXT};
}}
QHeaderView::section {{
    background: {BG};
    color: {MUTED};
    border: none;
    border-bottom: 2px solid {BORDER};
    border-right: 1px solid {BORDER};
    padding: 6px 10px;
    font-size: 11px;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}}

/* ── Boutons ── */
QPushButton {{
    background: transparent;
    border: 1px solid {BORDER};
    color: {MUTED};
    border-radius: 5px;
    padding: 6px 14px;
    font-size: 12px;
    min-width: 80px;
}}
QPushButton:hover {{
    background: {SURFACE2};
    color: {TEXT};
    border-color: {BLUE};
}}
QPushButton#btn_run {{
    background: {BLUE};
    color: #ffffff;
    font-weight: 700;
    border: none;
    padding: 7px 20px;
    font-size: 13px;
    min-width: 110px;
}}
QPushButton#btn_run:hover {{
    background: #6fa3ff;
}}
QPushButton#btn_run:disabled {{
    background: {BLUE_DIM};
    color: {MUTED};
}}

/* ── Scrollbars ── */
QScrollBar:vertical {{
    background: {BG};
    width: 6px;
    border-radius: 3px;
    margin: 0;
}}
QScrollBar::handle:vertical {{
    background: {BORDER};
    border-radius: 3px;
    min-height: 30px;
}}
QScrollBar::handle:vertical:hover {{
    background: {MUTED};
}}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ height: 0; }}
QScrollBar:horizontal {{
    background: {BG};
    height: 6px;
    border-radius: 3px;
}}
QScrollBar::handle:horizontal {{
    background: {BORDER};
    border-radius: 3px;
}}
QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{ width: 0; }}

/* ── Splitter ── */
QSplitter::handle {{
    background: {BORDER};
}}
QSplitter::handle:horizontal {{ width: 1px; }}
QSplitter::handle:vertical   {{ height: 1px; }}

/* ── Zone erreurs ── */
QFrame#err_frame {{
    background: {RED_DIM};
    border: 1px solid {RED};
    border-radius: 5px;
}}
QLabel#err_title {{
    color: {RED};
    font-weight: 700;
    font-size: 12px;
}}
QPlainTextEdit#err_text {{
    background: transparent;
    border: none;
    color: #ff8a88;
    font-family: {MONO};
    font-size: 11px;
}}

/* ── Badge statut ── */
QLabel#badge_ok  {{ color: {GREEN}; font-weight:700; font-size:11px; }}
QLabel#badge_err {{ color: {RED};   font-weight:700; font-size:11px; }}
QLabel#badge_wait{{ color: {MUTED}; font-size:11px; }}

/* ── Étiquette état vide ── */
QLabel#empty_label {{
    color: {MUTED};
    font-size: 14px;
}}
"""

COLS = ["Matricule", "Nom", "Niveau", "Semestre",
        "Moy. Sem.", "Moy. Ann.", "Rang", "Mention", "Décision"]


# ── Drag & Drop sur le panneau fichier ────────────────────────────
class FilePanel(QFrame):
    """Panneau compact : nom de fichier + zone drop + bouton Parcourir."""

    def __init__(self, cb_load, cb_browse):
        super().__init__()
        self.setObjectName("file_panel")
        self.setAcceptDrops(True)
        self.setFixedHeight(52)

        lay = QHBoxLayout(self)
        lay.setContentsMargins(12, 0, 12, 0)
        lay.setSpacing(10)

        # Icône dossier
        ico = QLabel("📄")
        ico.setFixedWidth(22)

        # Nom du fichier
        self.lbl = QLabel("Glissez un fichier .sgn ici ou cliquez sur Parcourir")
        self.lbl.setObjectName("drop_label")

        # Bouton Parcourir
        btn = QPushButton("Parcourir…")
        btn.setFixedWidth(100)
        btn.clicked.connect(cb_browse)

        lay.addWidget(ico)
        lay.addWidget(self.lbl, stretch=1)
        lay.addWidget(btn)

        self._cb_load = cb_load

    def set_file(self, nom):
        self.lbl.setText(f"  {nom}")
        self.lbl.setObjectName("file_name")
        self.lbl.setStyleSheet(f"color:{TEXT}; font-weight:600;")

    def dragEnterEvent(self, e):
        e.acceptProposedAction() if e.mimeData().hasUrls() else e.ignore()

    def dropEvent(self, e):
        urls = e.mimeData().urls()
        if urls:
            self._cb_load(urls[0].toLocalFile())


# ── Fenêtre principale ─────────────────────────────────────────────
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("SGN — Système de Gestion des Notes")
        self.setMinimumSize(900, 600)
        self.resize(1180, 760)
        self.fichier    = None
        self._last_data = None
        self._build()

    # ── Construction ──────────────────────────────────────────────
    def _build(self):
        root = QWidget()
        self.setCentralWidget(root)
        main = QVBoxLayout(root)
        main.setSpacing(0)
        main.setContentsMargins(0, 0, 0, 0)

        # ── 1. Toolbar ──────────────────────────────────────────
        toolbar = QFrame()
        toolbar.setObjectName("toolbar")
        toolbar.setFixedHeight(52)
        tlay = QHBoxLayout(toolbar)
        tlay.setContentsMargins(16, 0, 16, 0)
        tlay.setSpacing(8)

        title = QLabel("SGN")
        title.setStyleSheet(f"color:{TEXT}; font-weight:700; font-size:15px;")

        self.badge = QLabel("En attente d'un fichier")
        self.badge.setObjectName("badge_wait")

        self.btn_run = QPushButton("▶  Analyser")
        self.btn_run.setObjectName("btn_run")
        self.btn_run.setEnabled(False)
        self.btn_run.clicked.connect(self._analyser)

        btn_csv = QPushButton("⬇  CSV")
        btn_csv.clicked.connect(self._export_csv)
        btn_txt = QPushButton("⬇  TXT")
        btn_txt.clicked.connect(self._export_txt)

        tlay.addWidget(title)
        tlay.addSpacing(8)
        tlay.addWidget(self.badge, stretch=1)
        tlay.addWidget(btn_csv)
        tlay.addWidget(btn_txt)
        tlay.addWidget(self.btn_run)
        main.addWidget(toolbar)

        # ── 2. Corps principal ──────────────────────────────────
        body = QWidget()
        blay = QVBoxLayout(body)
        blay.setContentsMargins(12, 10, 12, 10)
        blay.setSpacing(8)
        main.addWidget(body, stretch=1)

        # Panneau fichier (drag & drop + parcourir)
        self.file_panel = FilePanel(self._charger_fichier, self._ouvrir)
        blay.addWidget(self.file_panel)

        # Splitter vertical : éditeur (haut, rétractable) | onglets résultats (bas)
        self.splitter = QSplitter(Qt.Orientation.Vertical)
        self.splitter.setHandleWidth(4)
        blay.addWidget(self.splitter, stretch=1)

        # Éditeur
        self.editeur = QPlainTextEdit()
        self.editeur.setPlaceholderText("Contenu du fichier .sgn (éditable avant analyse)…")
        self.editeur.setMinimumHeight(40)
        self.splitter.addWidget(self.editeur)

        # Onglets
        self.tabs = QTabWidget()
        self.splitter.addWidget(self.tabs)

        # Proportions initiales : éditeur 25 % / onglets 75 %
        self.splitter.setSizes([180, 520])

        # — Onglet Résultats —
        tab_res = QWidget()
        vr = QVBoxLayout(tab_res)
        vr.setContentsMargins(0, 0, 0, 0)
        vr.setSpacing(0)

        self.table = QTableWidget(0, len(COLS))
        self.table.setHorizontalHeaderLabels(COLS)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.setAlternatingRowColors(True)
        self.table.setStyleSheet(
            f"QTableWidget {{ alternate-background-color: {SURFACE2}; }}")
        self.table.verticalHeader().setVisible(False)

        # Message état vide (superposé)
        self.lbl_vide = QLabel("Aucun résultat — chargez un fichier .sgn et cliquez Analyser")
        self.lbl_vide.setObjectName("empty_label")
        self.lbl_vide.setAlignment(Qt.AlignmentFlag.AlignCenter)

        vr.addWidget(self.table)
        vr.addWidget(self.lbl_vide)
        self.tabs.addTab(tab_res, "  Résultats  ")

        # — Onglet JSON brut —
        tab_json = QWidget()
        vj = QVBoxLayout(tab_json)
        vj.setContentsMargins(6, 6, 6, 6)
        self.zone_json = QPlainTextEdit()
        self.zone_json.setReadOnly(True)
        self.zone_json.setFont(QFont(MONO, 11))
        self.zone_json.setPlaceholderText("Le JSON retourné par sgn_parser apparaîtra ici…")
        vj.addWidget(self.zone_json)
        self.tabs.addTab(tab_json, "  JSON brut  ")

        # ── 3. Bandeau erreurs (masqué par défaut) ──────────────
        self.err_frame = QFrame()
        self.err_frame.setObjectName("err_frame")
        self.err_frame.setVisible(False)
        elay = QVBoxLayout(self.err_frame)
        elay.setContentsMargins(10, 6, 10, 6)
        elay.setSpacing(2)

        err_header = QHBoxLayout()
        lbl_err_ico   = QLabel("⚠")
        lbl_err_ico.setStyleSheet(f"color:{RED}; font-size:13px;")
        self.lbl_err_title = QLabel("0 erreur")
        self.lbl_err_title.setObjectName("err_title")
        btn_close_err = QPushButton("✕")
        btn_close_err.setFixedSize(20, 20)
        btn_close_err.setStyleSheet(
            f"border:none; color:{MUTED}; font-size:11px; background:transparent;")
        btn_close_err.clicked.connect(lambda: self.err_frame.setVisible(False))
        err_header.addWidget(lbl_err_ico)
        err_header.addWidget(self.lbl_err_title, stretch=1)
        err_header.addWidget(btn_close_err)

        self.zone_err = QPlainTextEdit()
        self.zone_err.setObjectName("err_text")
        self.zone_err.setReadOnly(True)
        self.zone_err.setMaximumHeight(70)

        elay.addLayout(err_header)
        elay.addWidget(self.zone_err)
        blay.addWidget(self.err_frame)

        # État initial
        self._maj_etat_vide(vide=True)

    # ── État vide / rempli ────────────────────────────────────────
    def _maj_etat_vide(self, vide):
        self.table.setVisible(not vide)
        self.lbl_vide.setVisible(vide)

    # ── Chargement ────────────────────────────────────────────────
    def _ouvrir(self):
        f, _ = QFileDialog.getOpenFileName(
            self, "Ouvrir un fichier SGN", "", "SGN (*.sgn);;Tous (*)")
        if f:
            self._charger_fichier(f)

    def _charger_fichier(self, f):
        self.fichier = f
        self.file_panel.set_file(os.path.basename(f))
        self.badge.setText(f"  {os.path.basename(f)}")
        self.badge.setObjectName("badge_wait")
        self.badge.setStyleSheet(f"color:{MUTED}; font-size:11px;")
        self.btn_run.setEnabled(True)
        try:
            with open(f, encoding="utf-8") as fh:
                self.editeur.setPlainText(fh.read())
        except Exception as e:
            self._afficher_erreur_ui(f"Lecture : {e}")

    # ── Analyse ───────────────────────────────────────────────────
    def _analyser(self):
        if not self.fichier:
            return
        try:
            with open(self.fichier, "w", encoding="utf-8") as fh:
                fh.write(self.editeur.toPlainText())
        except Exception as e:
            self._afficher_erreur_ui(f"Sauvegarde : {e}")
            return

        self.btn_run.setEnabled(False)
        self.btn_run.setText("…")
        QApplication.processEvents()

        data = analyser(self.fichier)
        self._last_data = data

        self.btn_run.setEnabled(True)
        self.btn_run.setText("▶  Analyser")

        self._afficher(data)

    # ── Affichage ─────────────────────────────────────────────────
    def _afficher(self, data):
        # JSON brut
        self.zone_json.setPlainText(json.dumps(data, ensure_ascii=False, indent=2))

        # Erreurs
        errs = data.get("erreurs", [])
        if errs:
            self.lbl_err_title.setText(
                f"{len(errs)} erreur{'s' if len(errs) > 1 else ''} détectée{'s' if len(errs) > 1 else ''}")
            self.zone_err.setPlainText(
                "\n".join(f"[{e.get('type','?')}] Ligne {e['ligne']} : {e['message']}"
                          for e in errs))
            self.err_frame.setVisible(True)
            self.badge.setText(f"⚠  {len(errs)} erreur{'s' if len(errs)>1 else ''}")
            self.badge.setStyleSheet(f"color:{RED}; font-weight:700; font-size:11px;")
        else:
            self.err_frame.setVisible(False)
            self.badge.setText("✓  Analyse réussie")
            self.badge.setStyleSheet(f"color:{GREEN}; font-weight:700; font-size:11px;")

        # Tableau
        self.table.setRowCount(0)
        niveaux = data.get("niveaux", [])
        a_des_lignes = False

        for niv in niveaux:
            for etu in niv.get("etudiants", []):
                sems = etu.get("semestres", [{}])
                for i, sem in enumerate(sems):
                    a_des_lignes = True
                    r = self.table.rowCount()
                    self.table.insertRow(r)
                    vals = [
                        etu.get("matricule", "")                if i == 0 else "",
                        etu.get("nom", "")                      if i == 0 else "",
                        niv.get("niveau", "")                   if i == 0 else "",
                        sem.get("id", ""),
                        f"{sem.get('moyenne', 0):.2f}",
                        f"{etu.get('moyenne_annuelle', 0):.2f}" if i == 0 else "",
                        str(etu.get("rang", ""))                if i == 0 else "",
                        etu.get("mention", "")                  if i == 0 else "",
                        etu.get("decision", "")                 if i == 0 else "",
                    ]
                    for c, v in enumerate(vals):
                        item = QTableWidgetItem(v)
                        item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                        if c == 7 and v:
                            item.setForeground(QColor(MENTION_COULEUR.get(v, TEXT)))
                        # Décision : gras
                        if c == 8 and v:
                            f2 = item.font(); f2.setBold(True); item.setFont(f2)
                        self.table.setItem(r, c, item)

        self._maj_etat_vide(not a_des_lignes)
        # Aller sur Résultats si données, JSON brut si seulement erreurs
        self.tabs.setCurrentIndex(0 if a_des_lignes else 1)

    def _afficher_erreur_ui(self, msg):
        self.lbl_err_title.setText("Erreur")
        self.zone_err.setPlainText(msg)
        self.err_frame.setVisible(True)

    # ── Export ────────────────────────────────────────────────────
    def _lignes_export(self):
        entete = [self.table.horizontalHeaderItem(c).text()
                  for c in range(self.table.columnCount())]
        lignes = [entete]
        for r in range(self.table.rowCount()):
            lignes.append([
                self.table.item(r, c).text() if self.table.item(r, c) else ""
                for c in range(self.table.columnCount())
            ])
        return lignes

    def _verifier_export(self):
        if self._last_data is None:
            QMessageBox.warning(self, "SGN", "Lancez une analyse d'abord.")
            return False
        return True

    def _export_csv(self):
        if not self._verifier_export():
            return
        f, _ = QFileDialog.getSaveFileName(
            self, "Exporter CSV", "resultats.csv", "CSV (*.csv)")
        if not f:
            return
        try:
            with open(f, "w", newline="", encoding="utf-8") as fh:
                w = csv.writer(fh)
                for ligne in self._lignes_export():
                    w.writerow(ligne)
            errs = self._last_data.get("erreurs", [])
            if errs:
                with open(f, "a", newline="", encoding="utf-8") as fh:
                    w = csv.writer(fh)
                    w.writerow([])
                    w.writerow(["TYPE", "LIGNE", "MESSAGE"])
                    for e in errs:
                        w.writerow([e.get("type", "?"), e["ligne"], e["message"]])
            QMessageBox.information(self, "Export", f"CSV exporté :\n{f}")
        except Exception as e:
            self._afficher_erreur_ui(f"Export CSV : {e}")

    def _export_txt(self):
        if not self._verifier_export():
            return
        f, _ = QFileDialog.getSaveFileName(
            self, "Exporter TXT", "resultats.txt", "Texte (*.txt)")
        if not f:
            return
        try:
            lignes = self._lignes_export()
            largeurs = [max(len(str(row[c])) for row in lignes)
                        for c in range(len(lignes[0]))]
            sep = "+-" + "-+-".join("-" * l for l in largeurs) + "-+"
            with open(f, "w", encoding="utf-8") as fh:
                fh.write("SGN — Résultats d'analyse\n")
                fh.write("=" * len(sep) + "\n\n")
                fh.write(sep + "\n")
                for i, row in enumerate(lignes):
                    cells = " | ".join(str(row[c]).center(largeurs[c])
                                       for c in range(len(row)))
                    fh.write(f"| {cells} |\n")
                    if i == 0:
                        fh.write(sep + "\n")
                fh.write(sep + "\n")
                errs = self._last_data.get("erreurs", [])
                if errs:
                    fh.write("\nERREURS DETECTEES\n")
                    fh.write("-" * 40 + "\n")
                    for e in errs:
                        fh.write(
                            f"[{e.get('type','?')}] Ligne {e['ligne']} : {e['message']}\n")
            QMessageBox.information(self, "Export", f"TXT exporté :\n{f}")
        except Exception as e:
            self._afficher_erreur_ui(f"Export TXT : {e}")


# ── Lancement ─────────────────────────────────────────────────────
if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyleSheet(SS)
    w = MainWindow()
    w.show()
    sys.exit(app.exec())
