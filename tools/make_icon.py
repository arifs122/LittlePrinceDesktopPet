"""Kucuk Prens karakterinden app.ico uretir (exe simgesi icin)."""
import os
import struct
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication

import prince

SIZES = [16, 32, 48, 64, 128, 256]
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "app.ico")


def render_png(size: int) -> bytes:
    """Karakteri (idle pozu) seffaf arka planda PNG olarak dondurur."""
    from PySide6.QtCore import QBuffer, QByteArray, QIODevice

    pm = prince.render("idle", 0, facing=1, scale=1.0)
    pm = pm.scaled(size, size, Qt.KeepAspectRatio, Qt.SmoothTransformation)

    canvas = pm
    buf = QByteArray()
    dev = QBuffer(buf)
    dev.open(QIODevice.WriteOnly)
    canvas.save(dev, "PNG")
    dev.close()
    return bytes(buf)


def main():
    app = QApplication(sys.argv)

    images = []
    for s in SIZES:
        data = render_png(s)
        images.append((s, data))
        print(f"  {s}x{s}: {len(data)} bayt")

    # ICO konteyneri (PNG tabanli; Vista ve sonrasi destekler)
    count = len(images)
    header = struct.pack("<HHH", 0, 1, count)
    offset = 6 + 16 * count

    entries = b""
    blob = b""
    for s, data in images:
        w = 0 if s >= 256 else s
        h = 0 if s >= 256 else s
        entries += struct.pack("<BBBBHHII", w, h, 0, 0, 1, 32, len(data), offset)
        blob += data
        offset += len(data)

    out = os.path.abspath(OUT)
    with open(out, "wb") as f:
        f.write(header + entries + blob)
    print("Kaydedildi:", out, os.path.getsize(out), "bayt")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
