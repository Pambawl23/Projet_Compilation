# interface.py — Widgets réutilisables SGN (PyQt6)
# Auteurs : Gilbert Ngor Thiomby DIOUF

from PyQt6.QtWidgets import QLabel, QFrame, QVBoxLayout
from PyQt6.QtCore    import Qt

# Couleurs (partagées avec app.py via import)
BG      = "#0b1326"
SURFACE = "#171f33"
BORDER  = "#424754"
BLUE    = "#4d8eff"
RED     = "#ff5451"
GREEN   = "#10B981"
AMBER   = "#F59E0B"
TEXT    = "#dae2fd"
MUTED   = "#8c909f"
MONO    = "JetBrains Mono, Menlo, monospace"

MENTION_COLOR = {
    "Tres Bien":  GREEN,
    "Bien":       GREEN,
    "Assez Bien": "#adc6ff",
    "Passable":   AMBER,
    "":           RED,
}


class StatCard(QFrame):
    """Carte de métrique compacte (affichage d'une valeur numérique)."""
    def __init__(self, titre: str, valeur: str, couleur: str = BLUE):
        super().__init__()
        self.setStyleSheet(
            f"QFrame{{background:{SURFACE};border:1px solid {BORDER};"
            f"border-radius:6px;padding:8px;}}"
        )
        lay = QVBoxLayout(self); lay.setSpacing(2); lay.setContentsMargins(10, 8, 10, 8)
        lbl_t = QLabel(titre); lbl_t.setStyleSheet(f"color:{MUTED};font-size:11px;")
        lbl_v = QLabel(valeur); lbl_v.setStyleSheet(f"color:{couleur};font-size:18px;font-weight:600;")
        lay.addWidget(lbl_t); lay.addWidget(lbl_v)


class BadgeDecision(QLabel):
    """Badge coloré Admis (bleu) / Ajourné (rouge)."""
    def __init__(self, texte: str):
        super().__init__(texte)
        c = BLUE if texte == "Admis" else RED
        self.setStyleSheet(
            f"background:{c}22;color:{c};border:1px solid {c}44;"
            f"border-radius:4px;padding:2px 8px;font-size:11px;font-weight:700;"
        )
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
