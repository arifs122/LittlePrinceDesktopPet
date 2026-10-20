"""Sohbet penceresini tek basina test eder (sahte karakter ile)."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QApplication

from littleprince.chat import ChatWindow


class BubbleStub:
    def __init__(self):
        self.last = None

    def say(self, text, seconds=4.0):
        self.last = text
        print("  [baloncuk]", text[:60], flush=True)


class FakePet:
    def __init__(self):
        self.cfg = {
            "llm_provider": "off",
            "llm_base_url": "http://localhost:11434",
            "llm_model": "",
            "llm_api_key": "",
        }
        self.x = 200.0
        self.y = 300.0
        self.W = 96
        self.H = 108
        self.bubble = BubbleStub()

    def open_settings(self):
        print("  [ayarlar] aciliyor", flush=True)


def main():
    app = QApplication(sys.argv)
    pet = FakePet()
    w = ChatWindow(pet)
    w.show_chat()

    QTimer.singleShot(1200, lambda: print(
        f"  hazir={w.provider_ready} saglayici={w.provider!r} durum={w.status.text()!r}",
        flush=True,
    ))
    QTimer.singleShot(1500, lambda: (w.input.setText("gülünü anlat bana"), w.send()))
    QTimer.singleShot(1600, lambda: print(f"  gonderim sonrasi satir sayisi={len(w.lines)}", flush=True))
    QTimer.singleShot(4000, lambda: print(
        "  akis (kismi):", repr(w.lines[-1][1][:60]) if w.lines else "yok", flush=True
    ))
    QTimer.singleShot(6500, lambda: print(
        f"  gecmis={len(w.history)} roller={[h['role'] for h in w.history]} "
        f"satirlar={[l[0] for l in w.lines]} hata_var={'⚠' in w.lines[-1][1]} "
        f"bekliyor={w._awaiting}",
        flush=True,
    ))
    QTimer.singleShot(6900, lambda: print(
        "  tam cevap:", repr(w.lines[-1][1])[:200] if w.lines else "yok", flush=True
    ))
    QTimer.singleShot(7200, app.quit)
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
