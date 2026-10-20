"""Tum yardimcilari (tilki, gul, fenerci, yilan, baobap) PNG olarak cizer."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QFont, QPainter, QPen, QPixmap
from PySide6.QtWidgets import QApplication

import companion

SCALE = 2.0
PAD = 8
LABEL = 22

ROWS = [
    ("fox", "walk", [0, 1, 2, 3, 4, 5]),
    ("fox", "sit", [0, 12, 24, 36]),
    ("rose", "idle", [0, 15, 30, 45]),
    ("lamplighter", "idle", [0, 40, 62, 100, 130]),
    ("lamplighter", "walk", [0, 1, 2, 3]),
    ("snake", "idle", [0, 14, 28, 42, 56]),
    ("baobab", "idle", [0, 12, 24, 36, 48]),
]


def main():
    app = QApplication(sys.argv)

    cell_w = int(max(companion.SPECIES[s][0] for s, _, _ in ROWS) * SCALE) + PAD * 2
    cell_h = int(max(companion.SPECIES[s][1] for s, _, _ in ROWS) * SCALE) + PAD * 2

    width = 130 + cell_w * 6 + 30
    height = 30 + (cell_h + LABEL) * len(ROWS) * 2

    sheet = QPixmap(width, height)
    sheet.fill(QColor("#2B2B33"))
    p = QPainter(sheet)
    p.setRenderHint(QPainter.Antialiasing, True)
    p.setFont(QFont("Segoe UI", 9))

    y = 24
    for species, state, frames in ROWS:
        for facing, name in ((1, "sag"), (-1, "sol")):
            p.setPen(QColor("#EEEEEE"))
            p.drawText(6, y + cell_h // 2 + 6, f"{species} / {state} / {name}")
            for col, fr in enumerate(frames):
                x0 = 130 + col * cell_w
                p.fillRect(x0, y, cell_w, cell_h, QColor("#3A3A46"))
                pm = companion.render(species, state, fr, facing=facing, scale=SCALE)
                ax = x0 + (cell_w - pm.width()) // 2
                ay = y + cell_h - PAD - pm.height()
                p.drawPixmap(ax, ay, pm)
                p.setPen(QPen(QColor("#FF5555"), 1, Qt.DashLine))
                p.drawLine(x0, y + cell_h - PAD, x0 + cell_w, y + cell_h - PAD)
                p.setPen(Qt.NoPen)
                p.setPen(QColor("#888888"))
                p.drawText(x0 + 4, y + 13, f"k{fr}")
                p.setPen(Qt.NoPen)
            y += cell_h
        y += LABEL

    p.end()
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "preview_companions.png")
    sheet.save(out)
    print("Kaydedildi:", out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
