"""Gorev cubugu one gecse bile bacaklarin gorunur kaldigini dogrular."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PySide6.QtCore import QRect, Qt, QTimer
from PySide6.QtGui import QColor, QGuiApplication, QPainter
from PySide6.QtWidgets import QApplication, QWidget

from littleprince import pet as pet_mod
from littleprince import platforms as w

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "shot_topmost.png")


class Cover(QWidget):
    """Gorev cubugunu taklit eden, her zaman ustte kapatan pencere."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Kapatan Pencere")
        self.setWindowFlag(Qt.WindowStaysOnTopHint, True)
        self.setWindowFlag(Qt.FramelessWindowHint, True)

    def paintEvent(self, _e):
        p = QPainter(self)
        p.fillRect(self.rect(), QColor("#0B1420"))
        p.end()


def main():
    app = QApplication(sys.argv)
    p = pet_mod.PetWindow()
    p.show()

    def place_on_taskbar():
        scr = QGuiApplication.primaryScreen().availableGeometry()
        p.support_hwnd = None
        p.support_y = float(scr.bottom() + 1)
        p.x = float(scr.right() - 700)
        p.y = p._rest_y()
        p.move(int(p.x), int(p.y))
        p.sit_down()
        print(
            "oturdu: state=", p.state, "scale=", p.scale, "W/H=", p.W, p.H,
            "y=", round(p.y), "support_y=", round(p.support_y),
            "alt sinir=", p._screen_bottom_at(p.x + p.W / 2),
        )

    cover = Cover()

    def raise_cover():
        scr = QGuiApplication.primaryScreen().availableGeometry()
        # tam gorev cubugu bolgesini ve biraz ustunu kapat
        cover.setGeometry(scr.right() - 950, scr.bottom() - 110, 900, 110)
        cover.show()
        cover.raise_()
        cover.activateWindow()
        print("kapatan pencere one gecti")

    def grab(tag):
        r = QGuiApplication.primaryScreen().devicePixelRatio()
        pm = QGuiApplication.primaryScreen().grabWindow(0)
        x = int((p.x - 90) * r)
        y = int((p.y - 60) * r)
        pm.copy(QRect(x, y, int((p.W + 180) * r), int((p.H + 90) * r))).save(
            OUT.replace(".png", f"_{tag}.png")
        )
        pet_i = w.z_order_index(int(p.winId()))
        cov_i = w.z_order_index(int(cover.winId()))
        tray = w.find_window("Shell_TrayWnd")
        tray_i = w.z_order_index(tray) if tray else None
        print(
            f"{tag}: pet_topmost={w.is_topmost(int(p.winId()))} "
            f"pet_z={pet_i} kapatan_z={cov_i} gorevcubugu_z={tray_i} "
            f"-> pet one mi? {pet_i is not None and cov_i is not None and pet_i < cov_i}"
        )

    QTimer.singleShot(500, place_on_taskbar)
    QTimer.singleShot(1500, raise_cover)
    QTimer.singleShot(2500, lambda: grab("kapatan_one"))
    QTimer.singleShot(3500, lambda: grab("sonra"))
    QTimer.singleShot(3800, app.quit)
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
