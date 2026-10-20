"""Ayar penceresinin acilip degerleri uyguladigini test eder."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QApplication

from littleprince import pet as pet_mod


def main():
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)
    p = pet_mod.PetWindow()

    def run():
        p.open_settings()
        d = p._settings
        print("dialog acildi:", d is not None, "gorunur:", d.isVisible())
        print("boyut alani:", d.scale.value(), "hiz:", d.speed.value(), "sans:", d.chance.value())
        d.scale.setValue(2.0)
        d.chance.setValue(80)
        d.on_top.setChecked(False)
        print("uygulandi ->", p.cfg)
        print("pencere:", p.W, p.H, "on_top:", p._on_top)
        d._reset()
        print("varsayilana dondu ->", p.cfg)
        d.close()
        print("dialog kapandi:", not d.isVisible())
        QTimer.singleShot(200, app.quit)

    QTimer.singleShot(300, run)
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
