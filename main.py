"""Kucuk Prens masaustu kardesi - baslatma dosyasi.

Calistirmak icin:  python main.py
Cikis icin: karaktere sag tiklayip "Cikis".

Ozel: LP_SELFTEST=1 ortam degiskeni ile baslatilirsa arayuzu acmaz,
kendini test eder ve sonucu %TEMP%\\lp_selftest.txt dosyasina yazar.
"""
from __future__ import annotations

import os
import sys
import tempfile

from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QApplication

from littleprince import config
from littleprince.pet import PetWindow
from littleprince.ui_font import apply_app_font


def _selftest() -> int:
    """Paketlenmis exe'de modullerin ve (varsa) yerlesik modelin calistigini dogrular."""
    lines: list[str] = []
    ok = True

    def add(text: str, bad: bool = False):
        nonlocal ok
        lines.append(text)
        if bad:
            ok = False

    try:
        QApplication.instance() or QApplication(sys.argv)
        add("Qt: OK")
    except Exception as exc:
        add(f"Qt: HATA {exc!r}", True)

    from littleprince import features

    ai = features.ai_enabled()
    add(f"Surum: {'AI' if ai else 'AI-siz (classic)'}")

    try:
        from littleprince import companion  # noqa: F401
        from littleprince import prince  # noqa: F401
        from littleprince import platforms  # noqa: F401

        platforms.refresh()
        add("Moduller: OK")
        add(f"Platform: {platforms.NAME}")
        add(f"Ayar dosyasi: {config.path()}")
        cfg = config.load()
        add(f"Ayar yuklendi: dil={cfg['language']} olcek={cfg['scale']}")
    except Exception as exc:
        add(f"Modul HATA: {exc!r}", True)

    if not ai:
        add("Yapay zeka: bu surumde yok (beklenen)")
    else:
        try:
            from littleprince import llm

            ready = llm.local_model_ready(config.load())
            add(f"Yerlesik model hazir mi: {ready}")
            if ready:
                import llama_cpp

                add(f"llama_cpp surum: {getattr(llama_cpp, '__version__', '?')}")
                model = llama_cpp.Llama(
                    model_path=llm.local_model_path(config.load()),
                    n_ctx=512,
                    n_threads=4,
                    verbose=False,
                )
                out = model.create_chat_completion(
                    messages=[{"role": "user", "content": "Say one word."}],
                    max_tokens=24,
                )
                answer = out["choices"][0]["message"]["content"].strip()
                add(f"Yerlesik model cevabi: {answer[:120]!r}")
        except Exception as exc:
            add(f"Yerlesik model HATA: {exc!r}", True)

    lines.append("SONUC: " + ("BASARILI" if ok else "HATALI"))
    path = os.path.join(tempfile.gettempdir(), "lp_selftest.txt")
    try:
        with open(path, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))
    except Exception:
        pass
    return 0 if ok else 1


def main() -> int:
    if os.environ.get("LP_SELFTEST") or os.environ.get("KP_SELFTEST"):
        return _selftest()

    app = QApplication(sys.argv)
    app.setApplicationName("Little Prince")
    app.setQuitOnLastWindowClosed(False)
    apply_app_font(app)

    pet = PetWindow()
    pet.show()
    pet.raise_()

    # Ayar dosyasinin yerinde oldugundan emin ol (ilk calistirmada olusturur)
    pet.save_ok = config.save(pet.cfg)

    # Acilista kucuk bir selamlama
    QTimer.singleShot(700, pet.greet)

    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
