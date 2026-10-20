"""Oturma + yardimci goruntusu ve ayar (boyut) degisimini test eder."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PySide6.QtCore import QRect, QTimer
from PySide6.QtGui import QGuiApplication
from PySide6.QtWidgets import QApplication

import pet as pet_mod

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "shot_sit.png")


def main():
    app = QApplication(sys.argv)
    p = pet_mod.PetWindow()
    p.cfg["companion_chance"] = 1.0
    p.show()

    def shoot():
        QTimer.singleShot(2500, lambda: p.sit_down())
        QTimer.singleShot(6000, grab)

    def grab():
        r = QGuiApplication.primaryScreen().devicePixelRatio()
        scr = QGuiApplication.primaryScreen()
        pm = scr.grabWindow(0)
        x = int((p.x - 160) * r)
        y = int((p.y - 170) * r)
        w = int((p.W + 320) * r)
        h = int((p.H + 300) * r)
        crop = pm.copy(QRect(x, y, w, h))
        crop.save(OUT)
        print("ekran goruntusu:", OUT, crop.width(), "x", crop.height())
        print("boyut once:", p.W, p.H, "olcek:", p.scale)
        # --- boyut ayarini degistir ---
        p.apply_settings({"scale": 2.6})
        print("boyut sonra:", p.W, p.H, "olcek:", p.scale)
        print("state:", p.state, "y:", round(p.y), "support_y:", round(p.support_y))
        p.apply_settings({"scale": 1.0})
        print("kucuk boyut:", p.W, p.H)
        QTimer.singleShot(300, app.quit)

    QTimer.singleShot(0, shoot)
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
