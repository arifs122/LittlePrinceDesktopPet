"""Derleme ozellikleri.

Iki ayri surum uretiliyor:
  LittlePrince(.exe)    -> yapay zeka YOK (kucuk, hizli, ai'siz)
  LittlePrinceAI(.exe)  -> yerlesik model + Ollama + API destegi

AI destegi, paketleme sirasinda binary'nin icine konan `ai_enabled.flag`
dosyasinin varligina bakilarak belirlenir. Kaynaktan calisirken varsayilan
olarak aciktir (LP_NO_AI=1 ile kapatilabilir).
"""
from __future__ import annotations

import os
import sys

AI_FLAG = "ai_enabled.flag"


def _bundle_dir() -> str:
    if getattr(sys, "frozen", False):
        return getattr(sys, "_MEIPASS", os.path.dirname(sys.executable))
    return os.path.dirname(os.path.abspath(__file__))


def ai_enabled() -> bool:
    """Bu surumde yapay zeka var mi?"""
    if getattr(sys, "frozen", False):
        return os.path.isfile(os.path.join(_bundle_dir(), AI_FLAG))
    return os.environ.get("LP_NO_AI") != "1"
