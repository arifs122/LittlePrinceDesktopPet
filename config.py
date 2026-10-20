"""Ayarlarin okunmasi / kaydedilmesi.

Ayar dosyasinin yeri:
  1) exe (veya kaynak) klasorunde `ayarlar.json` VARSA  -> orasi kullanilir
     (tasinabilir / portable mod: dosyayi exe'nin yanina koymak yeterli)
  2) yoksa -> %APPDATA%\\KucukPrens\\ayarlar.json

Boylece exe'yi baska bir klasore/masaustune tasisaniz, guncelleseniz ya da
exe klasoru salt-okunur olsa bile ayarlariniz kaybolmaz.
"""
from __future__ import annotations

import json
import os
import sys

APP_DIR_NAME = "LittlePrince"
FILE_NAME = "settings.json"

DEFAULTS = {
    "scale": 1.5,             # karakter boyutu (0.7 - 3.5)
    "walk_speed": 1.9,        # yurume hizi (px / kare)
    "companion_chance": 0.5,  # oturunca yardimci gelme sansi (0.0 - 1.0)
    "always_on_top": True,    # her zaman ustte
    "language": "auto",       # arayuz/karakter dili: auto | en | tr | ...
    "sleep_enabled": True,    # bosta kalinca uyusun mu
    "sleep_after": 90,        # kac saniye bosta kalinca uyusun
    "teleport_chance": 0.30,  # bos zamanlarda baska yuzeye isinlanma olasiligi
    "teleport_cooldown": 20,  # isinlanmalar arasi en az kac saniye
    "sit_min_seconds": 10,    # kendiliginden oturunca en az kac saniye otursun
    "follow_cursor": False,   # fare imlecine tepki ver
    # --- yapay zeka ---
    "llm_provider": "auto",              # auto | ollama | openai | local | off
    "llm_base_url": "http://localhost:11434",
    "llm_model": "",                     # bos ise otomatik secilir
    "llm_api_key": "",
    "local_model": "qwen1.5",            # yerlesik model anahtari (llm.LOCAL_MODELS)
}


def _local_dir() -> str:
    """exe'nin (paketliyse) ya da kaynak dosyalarin bulundugu klasor."""
    if getattr(sys, "frozen", False):
        return os.path.dirname(os.path.abspath(sys.executable))
    return os.path.dirname(os.path.abspath(__file__))


def _appdata_path() -> str:
    base = os.environ.get("APPDATA") or os.path.expanduser("~")
    return os.path.join(base, APP_DIR_NAME, FILE_NAME)


def _resolve_path() -> str:
    local = os.path.join(_local_dir(), FILE_NAME)
    if os.path.isfile(local):
        return local          # tasinabilir mod
    return _appdata_path()    # kalici (onerilen) konum


PATH = _resolve_path()
LAST_ERROR: str | None = None


def path() -> str:
    return PATH


def is_portable() -> bool:
    return os.path.abspath(PATH).startswith(os.path.abspath(_local_dir()))


def load() -> dict:
    data = dict(DEFAULTS)
    try:
        with open(PATH, "r", encoding="utf-8") as f:
            saved = json.load(f)
        if isinstance(saved, dict):
            for key in DEFAULTS:
                if key in saved:
                    data[key] = saved[key]
    except FileNotFoundError:
        pass
    except Exception as exc:
        global LAST_ERROR
        LAST_ERROR = f"Ayarlar okunamadi: {exc}"

    # Degerleri guvenli araliklara cek
    try:
        data["scale"] = max(0.7, min(3.5, float(data["scale"])))
        data["walk_speed"] = max(0.5, min(6.0, float(data["walk_speed"])))
        data["companion_chance"] = max(0.0, min(1.0, float(data["companion_chance"])))
        data["sleep_after"] = max(15, min(3600, int(float(data.get("sleep_after", 90)))))
        data["teleport_chance"] = max(0.0, min(1.0, float(data.get("teleport_chance", 0.3))))
        data["teleport_cooldown"] = max(0, min(3600, int(float(data.get("teleport_cooldown", 20)))))
        data["sit_min_seconds"] = max(0, min(600, int(float(data.get("sit_min_seconds", 10)))))
        data["always_on_top"] = bool(data["always_on_top"])
        data["language"] = str(data.get("language", "auto")).strip().lower()
        data["sleep_enabled"] = bool(data.get("sleep_enabled", True))
        data["follow_cursor"] = bool(data.get("follow_cursor", False))
        provider = str(data.get("llm_provider", "auto")).lower()
        data["llm_provider"] = (
            provider if provider in ("auto", "ollama", "openai", "local", "off") else "auto"
        )
        data["llm_base_url"] = str(data.get("llm_base_url", "")).strip()
        data["llm_model"] = str(data.get("llm_model", "")).strip()
        data["llm_api_key"] = str(data.get("llm_api_key", "")).strip()
        data["local_model"] = str(data.get("local_model", "qwen1.5")).strip()
    except Exception:
        pass
    return data


def save(data: dict) -> bool:
    """Ayarlari diske yazar. Basarili olursa True doner.

    Once gecici dosyaya yazip sonra yerine tasir; boylece yazma sirasinda
    uygulama kapansa bile ayar dosyasi bozulmaz.
    """
    global LAST_ERROR
    try:
        folder = os.path.dirname(PATH)
        if folder:
            os.makedirs(folder, exist_ok=True)
        tmp = PATH + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        os.replace(tmp, PATH)
        LAST_ERROR = None
        return True
    except Exception as exc:
        LAST_ERROR = f"Ayarlar kaydedilemedi: {exc}"
        return False
