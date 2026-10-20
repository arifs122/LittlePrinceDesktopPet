"""Cok dilli metinler icin font secimi.

Qt, istenen ailede bir harf yoksa sistemdeki baska bir fonttan tamamlar
(font fallback). Yine de CJK, Hint ve Tay dilleri icin dogru aileleri
listeye koymak garanti olur.
"""
from __future__ import annotations

from PySide6.QtGui import QFont

# Sirayla denenecek fontlar. Ilk bulunan kullanilir, eksik harfler
# sonrakilerden tamamlanir.
FAMILIES = [
    "Segoe UI",            # Latin, Kiril, Yunan, Arapca, Ibranice
    "Microsoft YaHei UI",  # Cince
    "Yu Gothic UI",        # Japonca
    "Malgun Gothic",       # Korece
    "Nirmala UI",          # Hint dilleri (Devanagari, Bengalce, Tamil...)
    "Leelawadee UI",       # Tayca
    "Arial Unicode MS",    # son care
]


def make_font(size: int = 10, bold: bool = False) -> QFont:
    font = QFont()
    font.setFamilies(FAMILIES)
    font.setPointSize(size)
    font.setBold(bold)
    return font


def apply_app_font(app) -> None:
    """Uygulamanin varsayilan fontuna fallback listesini ekler."""
    try:
        font = app.font()
        font.setFamilies(FAMILIES)
        app.setFont(font)
    except Exception:
        pass
