"""Masaustunun ekran goruntusunu alir (dogrulama icin)."""
import os
import sys

from PySide6.QtGui import QGuiApplication

app = QGuiApplication(sys.argv)
scr = QGuiApplication.primaryScreen()
pm = scr.grabWindow(0)
out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "screenshot.png")
pm.save(out)
print("Kaydedildi:", out, pm.width(), "x", pm.height())
