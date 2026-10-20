"""Platform secimi.

Uygulamanin ihtiyac duydugu kucuk platform API'si:

    virtual_screen_rect()            -> (x, y, genislik, yukseklik)
    list_windows(exclude)            -> [{hwnd, left, top, right, bottom, title}]
    z_order_index(hwnd)              -> int | None   (0 = en onde)
    set_topmost(hwnd, on=True)       -> None
    is_topmost(hwnd)                 -> bool
    find_window(class_name, title)   -> int | None
    open_folder(path)                -> None

Windows'ta Win32, Linux'ta X11 kullanilir. Wayland'da baska uygulamalarin
pencereleri okunamadigi icin yalnizca ekran kenarlari platform olur.
"""
from __future__ import annotations

import os
import subprocess
import sys


def _use_x11() -> bool:
    if not sys.platform.startswith("linux"):
        return False
    qpa = os.environ.get("QT_QPA_PLATFORM", "").lower()
    if qpa.startswith("wayland") or qpa == "offscreen":
        return False
    if os.environ.get("WAYLAND_DISPLAY") and not os.environ.get("DISPLAY"):
        return False
    return bool(os.environ.get("DISPLAY"))


def _select_backend():
    if sys.platform == "win32":
        from . import win32 as backend

        return backend
    if _use_x11():
        try:
            from . import x11 as backend

            if backend.available():
                return backend
        except Exception:
            pass
    from . import fallback as backend

    return backend


_backend = _select_backend()
NAME = getattr(_backend, "NAME", "unknown")

virtual_screen_rect = _backend.virtual_screen_rect
list_windows = _backend.list_windows
z_order_index = _backend.z_order_index
set_topmost = _backend.set_topmost
is_topmost = _backend.is_topmost
find_window = _backend.find_window


def _bind(backend) -> None:
    """Backend fonksiyonlarini modul seviyesine baglar."""
    global _backend, NAME
    global virtual_screen_rect, list_windows, z_order_index
    global set_topmost, is_topmost, find_window

    _backend = backend
    NAME = getattr(backend, "NAME", "unknown")
    virtual_screen_rect = backend.virtual_screen_rect
    list_windows = backend.list_windows
    z_order_index = backend.z_order_index
    set_topmost = backend.set_topmost
    is_topmost = backend.is_topmost
    find_window = backend.find_window


def refresh() -> str:
    """QApplication olustuktan sonra gercek Qt platformuna gore backend secer.

    Ozellikle Wayland + XWayland karisikligini onler: Qt Wayland ile calisiyorsa
    winId() bir X11 kimligi degildir, bu yuzden X11 katmani kullanilmamalidir.
    """
    name = ""
    try:
        from PySide6.QtGui import QGuiApplication

        name = QGuiApplication.platformName().lower()
    except Exception:
        return NAME

    if not name:
        return NAME
    if name == "xcb" and sys.platform.startswith("linux"):
        try:
            from . import x11

            if x11.available():
                _bind(x11)
        except Exception:
            pass
    elif name not in ("windows", "cocoa"):
        from . import fallback

        _bind(fallback)
    return NAME


def open_folder(path: str) -> None:
    """Ayar klasorunu isletim sisteminin dosya yoneticisinde acar."""
    if sys.platform == "win32":
        os.startfile(path)  # type: ignore[attr-defined]
    elif sys.platform == "darwin":
        subprocess.Popen(["open", path])
    else:
        subprocess.Popen(["xdg-open", path])
