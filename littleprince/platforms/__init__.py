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


def open_folder(path: str) -> None:
    """Ayar klasorunu isletim sisteminin dosya yoneticisinde acar."""
    if sys.platform == "win32":
        os.startfile(path)  # type: ignore[attr-defined]
    elif sys.platform == "darwin":
        subprocess.Popen(["open", path])
    else:
        subprocess.Popen(["xdg-open", path])
