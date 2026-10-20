"""Windows'ta acik pencerelerin konumlarini okumak icin ince bir ctypes katmani.

Harici kutuphane gerektirmez; sadece user32/dwmapi kullanir.
"""
from __future__ import annotations

import ctypes
from ctypes import wintypes

user32 = ctypes.WinDLL("user32", use_last_error=True)
dwmapi = ctypes.WinDLL("dwmapi", use_last_error=True)

DWMWA_EXTENDED_FRAME_BOUNDS = 9
DWMWA_CLOAKED = 14

GWL_EXSTYLE = -20
WS_EX_TOOLWINDOW = 0x00000080
WS_EX_NOACTIVATE = 0x08000000
WS_EX_TOPMOST = 0x00000008

HWND_TOPMOST = -1
HWND_NOTOPMOST = -2
SWP_NOSIZE = 0x0001
SWP_NOMOVE = 0x0002
SWP_NOACTIVATE = 0x0010
SWP_NOOWNERZORDER = 0x0200

GA_ROOT = 2

SM_XVIRTUALSCREEN = 76
SM_YVIRTUALSCREEN = 77
SM_CXVIRTUALSCREEN = 78
SM_CYVIRTUALSCREEN = 79


class RECT(ctypes.Structure):
    _fields_ = [
        ("left", wintypes.LONG),
        ("top", wintypes.LONG),
        ("right", wintypes.LONG),
        ("bottom", wintypes.LONG),
    ]


WNDENUMPROC = ctypes.WINFUNCTYPE(wintypes.BOOL, wintypes.HWND, wintypes.LPARAM)

user32.IsWindowVisible.argtypes = [wintypes.HWND]
user32.IsWindowVisible.restype = wintypes.BOOL

user32.IsIconic.argtypes = [wintypes.HWND]
user32.IsIconic.restype = wintypes.BOOL

user32.GetAncestor.argtypes = [wintypes.HWND, wintypes.UINT]
user32.GetAncestor.restype = wintypes.HWND

user32.GetWindowRect.argtypes = [wintypes.HWND, ctypes.POINTER(RECT)]
user32.GetWindowRect.restype = wintypes.BOOL

user32.GetWindowTextLengthW.argtypes = [wintypes.HWND]
user32.GetWindowTextLengthW.restype = ctypes.c_int

user32.GetWindowTextW.argtypes = [wintypes.HWND, wintypes.LPWSTR, ctypes.c_int]
user32.GetWindowTextW.restype = ctypes.c_int

user32.GetClassNameW.argtypes = [wintypes.HWND, wintypes.LPWSTR, ctypes.c_int]
user32.GetClassNameW.restype = ctypes.c_int

if hasattr(user32, "GetWindowLongPtrW"):
    _get_long = user32.GetWindowLongPtrW
else:
    _get_long = user32.GetWindowLongW
_get_long.argtypes = [wintypes.HWND, ctypes.c_int]
_get_long.restype = ctypes.c_ssize_t

user32.EnumWindows.argtypes = [WNDENUMPROC, wintypes.LPARAM]
user32.EnumWindows.restype = wintypes.BOOL

user32.SetWindowPos.argtypes = [
    wintypes.HWND,
    wintypes.HWND,
    ctypes.c_int,
    ctypes.c_int,
    ctypes.c_int,
    ctypes.c_int,
    wintypes.UINT,
]
user32.SetWindowPos.restype = wintypes.BOOL

user32.GetTopWindow.argtypes = [wintypes.HWND]
user32.GetTopWindow.restype = wintypes.HWND
user32.GetWindow.argtypes = [wintypes.HWND, wintypes.UINT]
user32.GetWindow.restype = wintypes.HWND
user32.FindWindowW.argtypes = [wintypes.LPCWSTR, wintypes.LPCWSTR]
user32.FindWindowW.restype = wintypes.HWND

dwmapi.DwmGetWindowAttribute.argtypes = [
    wintypes.HWND,
    wintypes.DWORD,
    ctypes.c_void_p,
    wintypes.DWORD,
]
dwmapi.DwmGetWindowAttribute.restype = ctypes.c_long

# Kabuk / masaustu pencereleri: bunlar "uzerine konulacak pencere" degildir.
_SHELL_CLASSES = {
    "Progman",
    "WorkerW",
    "Shell_TrayWnd",
    "Shell_SecondaryTrayWnd",
    "Windows.UI.Core.CoreWindow",
    "ApplicationFrameWindow_Tray",
    "TaskListThumbnailWnd",
    "ForegroundStaging",
    "XamlExplorerHostIslandWindow",
    "Windows.Internal.Shell.TabProxyWindow",
    "SysShadow",
    "MSCTFIME UI",
    "IME",
}


def _is_cloaked(hwnd) -> bool:
    cloaked = ctypes.c_int(0)
    try:
        res = dwmapi.DwmGetWindowAttribute(
            hwnd, DWMWA_CLOAKED, ctypes.byref(cloaked), ctypes.sizeof(cloaked)
        )
    except OSError:
        return False
    return res == 0 and cloaked.value != 0


def _rect_of(hwnd) -> RECT | None:
    """Cerceve golgelerini disarida birakan gercek pencere dikdortgeni."""
    rect = RECT()
    res = dwmapi.DwmGetWindowAttribute(
        hwnd,
        DWMWA_EXTENDED_FRAME_BOUNDS,
        ctypes.byref(rect),
        ctypes.sizeof(rect),
    )
    if res != 0:
        if not user32.GetWindowRect(hwnd, ctypes.byref(rect)):
            return None
    if rect.right <= rect.left or rect.bottom <= rect.top:
        return None
    return rect


def _text_of(hwnd) -> str:
    length = user32.GetWindowTextLengthW(hwnd)
    if length <= 0:
        return ""
    buf = ctypes.create_unicode_buffer(length + 1)
    user32.GetWindowTextW(hwnd, buf, length + 1)
    return buf.value


def _class_of(hwnd) -> str:
    buf = ctypes.create_unicode_buffer(256)
    user32.GetClassNameW(hwnd, buf, 256)
    return buf.value


def virtual_screen_rect() -> tuple[int, int, int, int]:
    """Tum ekranlari kapsayan sanal masaustu: (x, y, genislik, yukseklik)."""
    return (
        user32.GetSystemMetrics(SM_XVIRTUALSCREEN),
        user32.GetSystemMetrics(SM_YVIRTUALSCREEN),
        user32.GetSystemMetrics(SM_CXVIRTUALSCREEN),
        user32.GetSystemMetrics(SM_CYVIRTUALSCREEN),
    )


def is_topmost(hwnd: int) -> bool:
    """Pencere 'her zaman ustte' katmaninda mi?"""
    try:
        return bool(_get_long(wintypes.HWND(hwnd), GWL_EXSTYLE) & WS_EX_TOPMOST)
    except Exception:
        return False


def find_window(class_name: str, title: str | None = None) -> int | None:
    try:
        h = user32.FindWindowW(class_name, title)
        return int(h) if h else None
    except Exception:
        return None


def z_order_index(hwnd: int) -> int | None:
    """Pencerenin yigin sirasindaki yeri. Kucuk deger = daha onde."""
    try:
        target = int(hwnd)
        h = user32.GetTopWindow(None)
        i = 0
        while h:
            if int(h) == target:
                return i
            h = user32.GetWindow(h, 2)  # GW_HWNDNEXT
            i += 1
    except Exception:
        pass
    return None


def set_topmost(hwnd: int, on: bool = True) -> None:
    """Pencereyi tasimadan/aktiflestirmeden 'en ustte' katmanina tasir.

    Baska bir 'her zaman ustte' penceresi one gecmisse, bunu periyodik
    cagirinca kendimizi tekrar onune aliriz.
    """
    try:
        user32.SetWindowPos(
            wintypes.HWND(hwnd),
            wintypes.HWND(HWND_TOPMOST if on else HWND_NOTOPMOST),
            0,
            0,
            0,
            0,
            SWP_NOSIZE | SWP_NOMOVE | SWP_NOACTIVATE | SWP_NOOWNERZORDER,
        )
    except Exception:
        pass


def list_windows(exclude_hwnd: int | None = None) -> list[dict]:
    """Ekranda gorunen, uzerine konulabilecek pencerelerin dikdortgenleri."""
    result: list[dict] = []
    skip = int(exclude_hwnd) if exclude_hwnd else 0

    def callback(hwnd, _lparam):
        try:
            if hwnd == skip:
                return True
            if not user32.IsWindowVisible(hwnd):
                return True
            if user32.IsIconic(hwnd):
                return True
            if user32.GetAncestor(hwnd, GA_ROOT) != hwnd:
                return True

            ex = _get_long(hwnd, GWL_EXSTYLE)
            if ex & WS_EX_TOOLWINDOW:
                return True
            if ex & WS_EX_NOACTIVATE:
                return True

            if _class_of(hwnd) in _SHELL_CLASSES:
                return True
            if _is_cloaked(hwnd):
                return True

            rect = _rect_of(hwnd)
            if rect is None:
                return True

            w = rect.right - rect.left
            h = rect.bottom - rect.top
            # Cok kucuk veya tamamen ekran disi pencereleri ele
            if w < 80 or h < 60:
                return True
            if rect.left < -20000 or rect.top < -20000:
                return True

            result.append(
                {
                    "hwnd": int(hwnd),
                    "left": rect.left,
                    "top": rect.top,
                    "right": rect.right,
                    "bottom": rect.bottom,
                    "title": _text_of(hwnd),
                }
            )
        except Exception:
            pass
        return True

    user32.EnumWindows(WNDENUMPROC(callback), 0)
    return result
