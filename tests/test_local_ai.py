"""Yerlesik (llama.cpp) modelin gercekten cevap urettigini test eder."""
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QApplication

from littleprince import llm
from littleprince import pet as pet_mod

T0 = time.time()


def log(msg):
    print(f"  [{time.time()-T0:5.1f}s] {msg}", flush=True)


def main():
    app = QApplication(sys.argv)
    p = pet_mod.PetWindow()
    p.cfg["llm_provider"] = "local"
    p.cfg["local_model"] = "qwen0.5"

    log(f"model hazir mi: {llm.local_model_ready(p.cfg)}")
    log(f"model yolu: {llm.local_model_path(p.cfg)}")

    p.open_chat()
    QTimer.singleShot(2500, lambda: log(
        f"saglayici={p.chat.provider!r} durum={p.chat.status.text()!r}"
    ))
    QTimer.singleShot(3000, lambda: (
        p.chat.input.setText("Merhaba, sen kimsin? Kısaca anlat."),
        p.chat.send(),
        log("mesaj gonderildi (model yukleniyor...)"),
    ))
    QTimer.singleShot(15000, lambda: log(f"ara cevap: {p.chat.lines[-1][1][:120]!r}"))
    QTimer.singleShot(45000, lambda: log(f"SON CEVAP: {p.chat.lines[-1][1][:400]!r}"))
    QTimer.singleShot(46000, lambda: log(f"gecmis={len(p.chat.history)}"))
    QTimer.singleShot(47000, app.quit)
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
