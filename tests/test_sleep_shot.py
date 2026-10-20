"""Uyku pozunun ekran goruntusunu alir (Z harfleri dahil)."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PySide6.QtCore import QRect, QTimer
from PySide6.QtGui import QGuiApplication
from PySide6.QtWidgets import QApplication

from littleprince import pet as pet_mod

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "shot_sleep.png")


def main():
    app = QApplication(sys.argv)
    p = pet_mod.PetWindow()
    p.cfg["sleep_enabled"] = False
    p.show()

    def sleep_now():
        p.sit_locked = False
        p._cursor_check = lambda: None      # test: fare uyandirmasin
        p.set_state("sleep")
        p.anim_frame = 30
        p.move(int(p.x), int(p.y))
        print("uyku pozu kuruldu: state=", p.state, "y=", round(p.y),
              "beklenen=", round(p.support_y - 55 * p.scale))

    def grab():
        r = QGuiApplication.primaryScreen().devicePixelRatio()
        scr_pm = QGuiApplication.primaryScreen().grabWindow(0)
        screen = QRect(0, 0, scr_pm.width(), scr_pm.height())
        rect = QRect(
            int((p.x - 70) * r),
            int((p.y - 80) * r),
            int((p.W + 140) * r),
            int((p.H + 120) * r),
        ).intersected(screen)
        scr_pm.copy(rect).save(OUT)
        scr_pm.save(OUT.replace("shot_sleep", "shot_sleep_full"))
        print("kaydedildi:", OUT, rect.width(), "x", rect.height())
        print("pet pencere konumu:", p.x, p.y, "gorunur:", p.isVisible())
        QTimer.singleShot(200, app.quit)

    QTimer.singleShot(700, sleep_now)
    QTimer.singleShot(2200, grab)
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
