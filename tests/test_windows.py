"""Test icin birkac basit pencere acar (karakterin uzerine konacagi platformlar)."""
import sys

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QFont, QPainter
from PySide6.QtWidgets import QApplication, QWidget

WINDOWS = [
    ("Test Penceresi A", 200, 500, 520, 380, "#2E5E8C"),
    ("Test Penceresi B", 900, 400, 620, 460, "#7A4A8C"),
]


class Box(QWidget):
    def __init__(self, title, x, y, w, h, color):
        super().__init__()
        self.setWindowTitle(title)
        self.setGeometry(x, y, w, h)
        self._color = QColor(color)

    def paintEvent(self, _e):
        p = QPainter(self)
        p.fillRect(self.rect(), self._color)
        p.setPen(QColor("#FFFFFF"))
        p.setFont(QFont("Segoe UI", 16))
        p.drawText(self.rect(), Qt.AlignCenter, self.windowTitle())
        p.end()


def main():
    app = QApplication(sys.argv)
    boxes = [Box(*w) for w in WINDOWS]
    for b in boxes:
        b.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
