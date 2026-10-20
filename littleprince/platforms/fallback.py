"""Baska uygulamalarin pencereleri okunamadiginda kullanilan yedek katman.

Wayland (ve X11 olmayan ortamlar) burada devreye girer: karakter yalnizca
ekran kenarlarinda yurur, pencere ustlerine cikamaz. Pencerenin kendisi
Qt'nin WindowStaysOnTopHint bayragi ile ustte tutulur.
"""
from __future__ import annotations

NAME = "fallback"


def _qt_screen_rect() -> tuple[int, int, int, int]:
    try:
        from PySide6.QtGui import QGuiApplication

        screens = QGuiApplication.screens()
        if not screens:
            return (0, 0, 0, 0)
        left = min(s.geometry().left() for s in screens)
        top = min(s.geometry().top() for s in screens)
        right = max(s.geometry().right() for s in screens)
        bottom = max(s.geometry().bottom() for s in screens)
        return (left, top, right - left + 1, bottom - top + 1)
    except Exception:
        return (0, 0, 0, 0)


def virtual_screen_rect() -> tuple[int, int, int, int]:
    return _qt_screen_rect()


def list_windows(exclude_hwnd: int | None = None) -> list[dict]:
    return []


def z_order_index(hwnd: int) -> int | None:
    return None


def set_topmost(hwnd: int, on: bool = True) -> None:
    return None


def is_topmost(hwnd: int) -> bool:
    return True


def find_window(class_name: str, title: str | None = None) -> int | None:
    return None
