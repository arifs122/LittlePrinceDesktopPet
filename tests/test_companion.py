"""Oturma + yardimci gelme davranisini otomatik test eder."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QApplication

from littleprince import pet as pet_mod


def main():
    app = QApplication(sys.argv)
    p = pet_mod.PetWindow()
    p.cfg["companion_chance"] = 1.0
    # Pencereyi gostermiyoruz: kullanici mudahale etmesin (winId yine olusur)

    def report(tag):
        c = p.companion
        print(
            f"{tag}: state={p.state} locked={p.sit_locked} "
            f"comp={c.species if c else '-'} comp_state={getattr(c, 'state', '-')} "
            f"comp_pose={getattr(c, 'pose', '-')} "
            f"comp_x={getattr(c, 'x', 0):.0f} target={getattr(c, 'target_x', 0):.0f}"
        )

    QTimer.singleShot(400, p.sit_down)
    for t, tag in ((1200, "t1"), (2500, "t2"), (4500, "t3"), (7000, "t4")):
        QTimer.singleShot(t, lambda tg=tag: report(tg))
    QTimer.singleShot(6500, p.stand_up)
    QTimer.singleShot(8000, lambda: report("kalkmis"))
    QTimer.singleShot(8800, app.quit)
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
