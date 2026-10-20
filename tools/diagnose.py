"""Ortam teshisi: DPI olcegi ve pencere listesi tutarli mi?"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PySide6.QtWidgets import QApplication

from littleprince import platforms as w

app = QApplication(sys.argv)

print("virtual screen:", w.virtual_screen_rect())
for s in app.screens():
    print(
        f"  ekran {s.name()!r} dpr={s.devicePixelRatio()} "
        f"geom={s.geometry().getRect()} avail={s.availableGeometry().getRect()}"
    )

screens = app.screens()
qx = min(s.geometry().left() for s in screens)
qy = min(s.geometry().top() for s in screens)
qr = max(s.geometry().right() for s in screens)
qb = max(s.geometry().bottom() for s in screens)
vx, vy, vw, vh = w.virtual_screen_rect()
sx = vw / (qr - qx + 1)
sy = vh / (qb - qy + 1)
print(f"hesaplanan olcek: x={sx:.4f} y={sy:.4f}")

wins = w.list_windows()
print(f"\n{len(wins)} pencere bulundu:")
for win in wins:
    lx = (win["left"] - vx) / sx + qx
    ly = (win["top"] - vy) / sy + qy
    rx = (win["right"] - vx) / sx + qx
    print(
        f"  phys=({win['left']},{win['top']},{win['right']},{win['bottom']}) "
        f"-> logical=({lx:.0f},{ly:.0f},{rx:.0f})  {win['title'][:40]!r}"
    )
