"""Uyku, isinlanma ve sert inis tepkisini test eder."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QColor, QPainter
from PySide6.QtWidgets import QApplication, QWidget

import pet as pet_mod


class Box(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Test Yuzeyi")
        self.setGeometry(420, 300, 620, 320)

    def paintEvent(self, _e):
        p = QPainter(self)
        p.fillRect(self.rect(), QColor("#14202A"))
        p.end()


def main():
    app = QApplication(sys.argv)
    box = Box()
    box.show()

    p = pet_mod.PetWindow()
    p.cfg["sleep_enabled"] = True
    p.cfg["sleep_after"] = 16        # alt sinir 15 sn
    p.cfg["teleport_chance"] = 0.0
    p.show()

    def log(m):
        print("  " + m, flush=True)

    # --- platformlar ---
    QTimer.singleShot(1200, lambda: log(
        f"platform sayisi={len(p.platforms)} "
        f"yuzeyler={[(round(x['x1']), round(x['y'])) for x in p.platforms]}"
    ))

    # --- 1) uyku ---
    QTimer.singleShot(18000, lambda: log(
        f"[uyku] 18sn bosta -> state={p.state} "
        + ("(uyudu, Z ciziliyor)" if p.state == "sleep" else "SORUN")
    ))
    QTimer.singleShot(18400, lambda: (p.react(), log(f"[uyku] tiklandi -> state={p.state}")))

    # --- 2) isinlanma ---
    def tp():
        p.cfg["sleep_enabled"] = False
        p.idle_seconds = 0
        before = (round(p.x), round(p.support_y), p.support_hwnd)
        ok = p._start_teleport()
        log(f"[isinlanma] basladi={ok} phase={p.tp_phase} onceki={before}")

    QTimer.singleShot(19000, tp)
    QTimer.singleShot(21000, lambda: log(
        f"[isinlanma] sonuc: x={round(p.x)} support_y={round(p.support_y)} "
        f"hwnd={p.support_hwnd} phase={p.tp_phase} scale={p.tp_scale:.2f}"
    ))

    # --- 3) sert inis ---
    stats = {"max_land": 0}

    def big_drop():
        p.tp_phase = 0
        p.tp_scale = 1.0
        floor = p._screen_bottom_at(p.x + p.W / 2)
        p.support_hwnd = None
        p.support_y = float(floor)
        p.y = float(floor) - p.H - 420
        p.vy = 0.0
        p.fall_from_y = p.y
        p.state = "fall"
        p.action_frames = 0
        log(f"[inis] 420 px yukaridan birakildi (y={round(p.y)})")

    def poll():
        stats["max_land"] = max(stats["max_land"], p.land_frames)

    QTimer.singleShot(21600, big_drop)
    poller = QTimer()
    poller.timeout.connect(poll)
    poller.start(40)

    QTimer.singleShot(23000, lambda: log(
        f"[inis] max land_frames={stats['max_land']} state={p.state} "
        f"y={round(p.y)} support_y={round(p.support_y)} "
        + ("(yaylanma calisti)" if stats["max_land"] > 0 else "SORUN - yaylanma yok")
    ))

    QTimer.singleShot(23800, app.quit)
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
