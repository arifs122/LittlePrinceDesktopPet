"""Iki surumu de (AI'li / AI'siz) kaynaktan dogrular."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def check(no_ai: bool):
    os.environ["LP_NO_AI"] = "1" if no_ai else "0"
    for mod in list(sys.modules):
        if mod in ("chat", "llm", "features", "pet", "settings_dialog", "i18n", "config"):
            del sys.modules[mod]

    from PySide6.QtWidgets import QApplication

    app = QApplication.instance() or QApplication(sys.argv)

    import features
    import pet as pet_mod

    ai = features.ai_enabled()
    w = pet_mod.PetWindow()
    w.open_settings()
    d = w._settings
    w.open_chat()

    print(f"--- {'AI-SIZ' if no_ai else 'AI-LI'} surum ---")
    print(f"  ai_enabled        : {ai}")
    print(f"  ayar sekmeleri    : {d._ai} (AI sekmesi var mi)")
    print(f"  sohbet acildi mi  : {w.chat is not None}")
    print(f"  chat modulu yuklendi mi : {'chat' in sys.modules}")
    print(f"  llm modulu yuklendi mi  : {'llm' in sys.modules}")
    print(f"  dil / alinti sayisi     : {w.tr['menu']['sit']!r} / {len(w.tr['quotes'])}")
    print(f"  ayar dosyasi            : {__import__('config').path()}")
    d.close()
    w._timer.stop()
    w.close()
    return ai


ok1 = check(True)
ok2 = check(False)
print()
print("SONUC:", "BASARILI" if (ok1 is False and ok2 is True) else "HATALI")
