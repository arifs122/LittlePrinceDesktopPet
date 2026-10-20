"""Oturma pozunda bacaklarin alttaki pencere tarafindan kapatilip kapatilmadigini test eder."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PySide6.QtCore import QRect, Qt, QTimer
from PySide6.QtGui import QColor, QFont, QGuiApplication, QPainter
from PySide6.QtWidgets import QApplication, QWidget

import pet as pet_mod


class DarkBox(QWidget):
    def __init__(self, topmost):
        super().__init__()
        self.setWindowTitle("Test Kutusu")
        self.setGeometry(380, 520, 760, 420)
        if topmost:
            self.setWindowFlag(Qt.WindowStaysOnTopHint, True)

    def paintEvent(self, _e):
        p = QPainter(self)
        p.fillRect(self.rect(), QColor("#101820"))
        p.setPen(QColor("#7FE0C0"))
        p.setFont(QFont("Segoe UI", 14))
        p.drawText(self.rect(), Qt.AlignCenter, self.windowTitle())
        p.end()


def main():
    topmost = "--topmost" in sys.argv
    tag = "topmost" if topmost else "normal"
    out = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), f"shot_zorder_{tag}.png"
    )

    app = QApplication(sys.argv)
    box = DarkBox(topmost)

    p = pet_mod.PetWindow()
    p.show()

    if topmost:
        # Kutuyu bizim penceremizden SONRA one getir (ustte olanlarin da usti)
        box.show()
        box.raise_()
        box.activateWindow()
    else:
        box.show()

    def setup():
        p.refresh_platforms()
        print("--- platformlar ---")
        for pl in p.platforms:
            print(
                f"  x={pl['x1']:.0f}..{pl['x2']:.0f} y={pl['y']:.0f} hwnd={pl['hwnd']}"
            )
        print("test kutusu hwnd:", int(box.winId()), "geom:", box.geometry().getRect())
        # Test kutusunun tam olarak ustune oturt
        want = int(box.winId())
        for pl in p.platforms:
            if pl["hwnd"] == want:
                p.support_hwnd = pl["hwnd"]
                p.support_y = pl["y"]
                p.x = pl["x1"] + 240
                p.y = p.support_y - p._anchor("idle")
                p.move(int(p.x), int(p.y))
                print("platform bulundu:", pl)
                break
        else:
            print("UYARI: test penceresi platform olarak bulunamadi")
        p.sit_down()

    def grab():
        r = QGuiApplication.primaryScreen().devicePixelRatio()
        pm = QGuiApplication.primaryScreen().grabWindow(0)
        x = int((p.x - 140) * r)
        y = int((p.y - 140) * r)
        w = int((p.W + 280) * r)
        h = int((p.H + 260) * r)
        pm.copy(QRect(x, y, w, h)).save(out)
        print("kaydedildi:", out)
        print("pet y:", p.y, "support_y:", p.support_y, "pencere alt:", p.y + p.H)
        QTimer.singleShot(200, app.quit)

    QTimer.singleShot(600, setup)
    QTimer.singleShot(2600, grab)

    def check():
        import win32_windows as w

        print("pet hwnd:", int(p.winId()), "topmost mi?:", w.is_topmost(int(p.winId())))
        print("kutu hwnd:", int(box.winId()), "topmost mi?:", w.is_topmost(int(box.winId())))

    QTimer.singleShot(300, check)
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
