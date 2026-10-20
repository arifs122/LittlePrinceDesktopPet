"""Karakterin tum durumlarini bir PNG sayfasi olarak cizer (onizleme icin)."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QFont, QPainter, QPen, QPixmap
from PySide6.QtWidgets import QApplication

import prince

SCALE = 2.0
STATES = ["idle", "walk", "sit", "fall", "drag"]
COLS = 8
CW = int(prince.W * SCALE)
CH = int(prince.H * SCALE)
PAD = 6
LABEL = 20


def main():
    app = QApplication(sys.argv)
    cell_w = CW + PAD * 2
    cell_h = CH + PAD * 2
    width = 30 + cell_w * COLS
    height = 30 + (cell_h * 2 + LABEL) * len(STATES)

    sheet = QPixmap(width, height)
    sheet.fill(QColor("#2B2B33"))

    p = QPainter(sheet)
    p.setRenderHint(QPainter.Antialiasing, True)
    p.setFont(QFont("Segoe UI", 9))

    y = 24
    for state in STATES:
        n = prince.frame_count(state)
        for facing, name in ((1, "sag"), (-1, "sol")):
            p.setPen(QColor("#EEEEEE"))
            p.drawText(6, y + 14, f"{state} / {name}")
            for col in range(n):
                x0 = 30 + col * cell_w
                p.fillRect(x0, y, cell_w, cell_h, QColor("#3A3A46"))
                pm = prince.render(state, col, facing=facing, scale=SCALE)
                p.drawPixmap(x0 + PAD, y + PAD, pm)
                # destek/platform hizasini isaretle
                ay = y + PAD + int(prince.ANCHOR.get(state, prince.H) * SCALE)
                p.setPen(QPen(QColor("#FF5555"), 1, Qt.DashLine))
                p.drawLine(x0, ay, x0 + cell_w, ay)
                p.setPen(Qt.NoPen)
            y += cell_h
        y += LABEL

    p.end()
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "preview.png")
    sheet.save(out)
    print("Kaydedildi:", out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
