"""Tum yoldas turlerinin sorunsuz olusturuldugunu hizlica dogrular."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QApplication

import companion
import pet as pet_mod


def main():
    app = QApplication(sys.argv)
    p = pet_mod.PetWindow()

    names = list(companion.SPECIES.keys())
    errors = []

    def try_one(i):
        if i >= len(names):
            print("hatalar:", errors if errors else "yok")
            QTimer.singleShot(200, app.quit)
            return
        sp = names[i]
        try:
            p._dismiss_companion()
            p.sit_down()
            c = companion.Companion(sp, p, 1 if i % 2 == 0 else -1, p.x - 400, p.x + 400)
            p.companion = c
            c.show()
            pm = companion.render(sp, c.pose, 10, facing=1, scale=p.scale)
            print(
                f"  {sp:12s} OK  boyut={c.W}x{c.H} gelis={c.arrive} "
                f"hedef_x={c.target_x:.0f} pixmap={pm.width()}x{pm.height()}"
            )
        except Exception as exc:
            errors.append(f"{sp}: {exc!r}")
            print(f"  {sp:12s} HATA: {exc!r}")
        QTimer.singleShot(120, lambda: try_one(i + 1))

    QTimer.singleShot(300, lambda: try_one(0))
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
