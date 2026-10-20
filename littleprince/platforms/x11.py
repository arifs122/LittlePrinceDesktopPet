"""X11 (Linux) pencerelerini okumak icin ince bir ctypes katmani.

Harici kutuphane gerektirmez; dogrudan libX11 kullanir. EWMH (_NET_*)
ozellikleri okunur, boylece pencere yoneticisiyle uyumlu calisir.

Wayland'da baska uygulamalarin pencerelerine erisilemedigi icin bu katman
devre disi kalir (bkz. fallback.py).
"""
from __future__ import annotations

import atexit
import ctypes
import ctypes.util
from ctypes import (
    POINTER,
    Structure,
    Union,
    byref,
    c_char_p,
    c_int,
    c_long,
    c_uint,
    c_ulong,
    c_void_p,
)

NAME = "x11"

XA_ATOM = 4
XA_CARDINAL = 6
XA_STRING = 31
XA_WINDOW = 33

IS_VIEWABLE = 2
CLIENT_MESSAGE = 33

SUBSTRUCTURE_NOTIFY = 1 << 19
SUBSTRUCTURE_REDIRECT = 1 << 20

ANY_DESKTOP = 0xFFFFFFFF


class XWindowAttributes(Structure):
    _fields_ = [
        ("x", c_int),
        ("y", c_int),
        ("width", c_int),
        ("height", c_int),
        ("border_width", c_int),
        ("depth", c_int),
        ("visual", c_void_p),
        ("root", c_ulong),
        ("class", c_int),
        ("bit_gravity", c_int),
        ("win_gravity", c_int),
        ("backing_store", c_int),
        ("backing_planes", c_ulong),
        ("backing_pixel", c_ulong),
        ("save_under", c_int),
        ("colormap", c_ulong),
        ("map_installed", c_int),
        ("map_state", c_int),
        ("all_event_masks", c_long),
        ("your_event_mask", c_long),
        ("do_not_propagate_mask", c_long),
        ("override_redirect", c_int),
        ("screen", c_void_p),
    ]


class XClientMessageEvent(Structure):
    _fields_ = [
        ("type", c_int),
        ("serial", c_ulong),
        ("send_event", c_int),
        ("display", c_void_p),
        ("window", c_ulong),
        ("message_type", c_ulong),
        ("format", c_int),
        ("data", c_long * 5),
    ]


class XEvent(Union):
    _fields_ = [
        ("type", c_int),
        ("xclient", XClientMessageEvent),
        ("pad", c_long * 24),
    ]


_xlib = None
_dpy = None
_root = None
_open_failed = False
_atoms: dict[str, int] = {}

# Bu turdeki pencereler platform degildir: panel, masaustu, menu, ipucu,
# bildirim, arac penceresi (bizim yoldaslar da arac penceresidir)...
_SKIP_TYPES = {
    "_NET_WM_WINDOW_TYPE_DOCK",
    "_NET_WM_WINDOW_TYPE_DESKTOP",
    "_NET_WM_WINDOW_TYPE_TOOLBAR",
    "_NET_WM_WINDOW_TYPE_MENU",
    "_NET_WM_WINDOW_TYPE_DROPDOWN_MENU",
    "_NET_WM_WINDOW_TYPE_POPUP_MENU",
    "_NET_WM_WINDOW_TYPE_TOOLTIP",
    "_NET_WM_WINDOW_TYPE_NOTIFICATION",
    "_NET_WM_WINDOW_TYPE_COMBO",
    "_NET_WM_WINDOW_TYPE_DND",
    "_NET_WM_WINDOW_TYPE_SPLASH",
    "_NET_WM_WINDOW_TYPE_UTILITY",
}

_SKIP_STATES = {
    "_NET_WM_STATE_HIDDEN",
    "_NET_WM_STATE_SKIP_TASKBAR",
}


def _load():
    """libX11'i yukler ve baglantiyi acar. Basarisizsa None doner."""
    global _xlib, _dpy, _root, _open_failed

    if _dpy is not None:
        return _dpy
    if _open_failed:
        return None

    try:
        lib_name = ctypes.util.find_library("X11") or "libX11.so.6"
        lib = ctypes.CDLL(lib_name)

        lib.XOpenDisplay.argtypes = [c_char_p]
        lib.XOpenDisplay.restype = c_void_p
        lib.XCloseDisplay.argtypes = [c_void_p]
        lib.XCloseDisplay.restype = c_int
        lib.XDefaultRootWindow.argtypes = [c_void_p]
        lib.XDefaultRootWindow.restype = c_ulong
        lib.XInternAtom.argtypes = [c_void_p, c_char_p, c_int]
        lib.XInternAtom.restype = c_ulong
        lib.XGetWindowProperty.argtypes = [
            c_void_p,
            c_ulong,
            c_ulong,
            c_long,
            c_long,
            c_int,
            c_ulong,
            POINTER(c_ulong),
            POINTER(c_int),
            POINTER(c_ulong),
            POINTER(c_ulong),
            POINTER(c_void_p),
        ]
        lib.XGetWindowProperty.restype = c_int
        lib.XFree.argtypes = [c_void_p]
        lib.XFree.restype = c_int
        lib.XGetWindowAttributes.argtypes = [
            c_void_p,
            c_ulong,
            POINTER(XWindowAttributes),
        ]
        lib.XGetWindowAttributes.restype = c_int
        lib.XQueryTree.argtypes = [
            c_void_p,
            c_ulong,
            POINTER(c_ulong),
            POINTER(c_ulong),
            POINTER(POINTER(c_ulong)),
            POINTER(c_uint),
        ]
        lib.XQueryTree.restype = c_int
        lib.XTranslateCoordinates.argtypes = [
            c_void_p,
            c_ulong,
            c_ulong,
            c_int,
            c_int,
            POINTER(c_int),
            POINTER(c_int),
            POINTER(c_ulong),
        ]
        lib.XTranslateCoordinates.restype = c_int
        lib.XRaiseWindow.argtypes = [c_void_p, c_ulong]
        lib.XRaiseWindow.restype = c_int
        lib.XLowerWindow.argtypes = [c_void_p, c_ulong]
        lib.XLowerWindow.restype = c_int
        lib.XFlush.argtypes = [c_void_p]
        lib.XFlush.restype = c_int
        lib.XSendEvent.argtypes = [c_void_p, c_ulong, c_int, c_long, POINTER(XEvent)]
        lib.XSendEvent.restype = c_int
        lib.XFetchName.argtypes = [c_void_p, c_ulong, POINTER(c_char_p)]
        lib.XFetchName.restype = c_int

        dpy = lib.XOpenDisplay(None)
        if not dpy:
            _open_failed = True
            return None

        _xlib = lib
        _dpy = dpy
        _root = int(lib.XDefaultRootWindow(dpy))
        atexit.register(_close)
        return _dpy
    except Exception:
        _open_failed = True
        return None


def _close():
    global _dpy
    if _dpy is not None and _xlib is not None:
        try:
            _xlib.XCloseDisplay(_dpy)
        except Exception:
            pass
    _dpy = None


def available() -> bool:
    return _load() is not None


def _atom(name: str) -> int:
    if name in _atoms:
        return _atoms[name]
    dpy = _load()
    if dpy is None:
        return 0
    atom = int(_xlib.XInternAtom(dpy, name.encode("ascii"), False))
    _atoms[name] = atom
    return atom


def _prop(win: int, name: str, req_type: int = 0, length: int = 1024):
    """Bir X ozelligini okur: (tur, veri) veya None."""
    dpy = _load()
    if dpy is None:
        return None
    atom = _atom(name)
    if not atom:
        return None

    actual_type = c_ulong(0)
    actual_format = c_int(0)
    nitems = c_ulong(0)
    bytes_after = c_ulong(0)
    data = c_void_p()

    try:
        status = _xlib.XGetWindowProperty(
            dpy,
            c_ulong(win),
            c_ulong(atom),
            0,
            length,
            False,
            c_ulong(req_type),
            byref(actual_type),
            byref(actual_format),
            byref(nitems),
            byref(bytes_after),
            byref(data),
        )
    except Exception:
        return None

    if status != 0 or not data.value:
        return None

    try:
        count = int(nitems.value)
        fmt = actual_format.value
        if fmt == 32:
            values = ctypes.cast(data, POINTER(c_ulong))
            return int(actual_type.value), [int(values[i]) for i in range(count)]
        if fmt == 8:
            return int(actual_type.value), ctypes.string_at(data, count)
        return int(actual_type.value), None
    finally:
        try:
            _xlib.XFree(data)
        except Exception:
            pass


def _atom_names(values: list[int] | None) -> set[str]:
    if not values:
        return set()
    return {name for name, atom in _atoms.items() if atom in values}


def _attributes(win: int) -> XWindowAttributes | None:
    dpy = _load()
    if dpy is None:
        return None
    attrs = XWindowAttributes()
    try:
        if not _xlib.XGetWindowAttributes(dpy, c_ulong(win), byref(attrs)):
            return None
    except Exception:
        return None
    return attrs


def _title(win: int) -> str:
    for name, req_type in (
        ("_NET_WM_VISIBLE_NAME", _atom("UTF8_STRING")),
        ("_NET_WM_NAME", _atom("UTF8_STRING")),
    ):
        prop = _prop(win, name, req_type)
        if prop and isinstance(prop[1], bytes) and prop[1]:
            return prop[1].decode("utf-8", "replace")
    prop = _prop(win, "WM_NAME", XA_STRING)
    if prop and isinstance(prop[1], bytes) and prop[1]:
        return prop[1].decode("utf-8", "replace")
    dpy = _load()
    if dpy is not None:
        try:
            text = c_char_p()
            if _xlib.XFetchName(dpy, c_ulong(win), byref(text)) and text.value:
                try:
                    return text.value.decode("utf-8", "replace")
                finally:
                    _xlib.XFree(ctypes.cast(text, c_void_p))
        except Exception:
            pass
    return ""


def _class_name(win: int) -> str:
    prop = _prop(win, "WM_CLASS", XA_STRING)
    if prop and isinstance(prop[1], bytes):
        parts = [p for p in prop[1].split(b"\x00") if p]
        if parts:
            return parts[-1].decode("utf-8", "replace")
    return ""


def _types(win: int) -> set[str]:
    prop = _prop(win, "_NET_WM_WINDOW_TYPE", XA_ATOM, length=32)
    if not prop or not isinstance(prop[1], list):
        return set()
    return _atom_names(prop[1])


def _states(win: int) -> list[int]:
    prop = _prop(win, "_NET_WM_STATE", XA_ATOM, length=64)
    if not prop or not isinstance(prop[1], list):
        return []
    return prop[1]


def _on_current_desktop(win: int) -> bool:
    current = _prop(_root, "_NET_CURRENT_DESKTOP", XA_CARDINAL)
    if not current or not current[1]:
        return True
    desktop = _prop(win, "_NET_WM_DESKTOP", XA_CARDINAL)
    if not desktop or not desktop[1]:
        return True
    return desktop[1][0] in (ANY_DESKTOP, current[1][0])


def _client_windows() -> list[int]:
    """EWMH istemci listesi; yoksa kok pencerenin cocuklari."""
    prop = _prop(_root, "_NET_CLIENT_LIST", XA_WINDOW, length=4096)
    if prop and isinstance(prop[1], list) and prop[1]:
        return prop[1]

    dpy = _load()
    if dpy is None:
        return []
    root_return = c_ulong()
    parent_return = c_ulong()
    children = POINTER(c_ulong)()
    count = c_uint()
    try:
        if not _xlib.XQueryTree(
            dpy,
            c_ulong(_root),
            byref(root_return),
            byref(parent_return),
            byref(children),
            byref(count),
        ):
            return []
        try:
            return [int(children[i]) for i in range(count.value)]
        finally:
            if children:
                _xlib.XFree(children)
    except Exception:
        return []


def _top_level(win: int) -> int | None:
    """Pencere yoneticisinin cercevesi dahil en ust seviye pencere."""
    dpy = _load()
    if dpy is None:
        return None
    current = int(win)
    for _ in range(32):
        root_return = c_ulong()
        parent = c_ulong()
        children = POINTER(c_ulong)()
        count = c_uint()
        try:
            if not _xlib.XQueryTree(
                dpy,
                c_ulong(current),
                byref(root_return),
                byref(parent),
                byref(children),
                byref(count),
            ):
                return current
        except Exception:
            return None
        finally:
            if children:
                try:
                    _xlib.XFree(children)
                except Exception:
                    pass
        if not parent.value or int(parent.value) == _root:
            return current
        current = int(parent.value)
    return current


def _frame_rect(win: int) -> tuple[int, int, int, int] | None:
    """Baslik cubugu ve cerceve dahil gercek dikdortgen.

    Pencere yoneticisi istemciyi bir cerceve icine aliyorsa (Mutter, KWin,
    Xfwm, ...) cercevenin kendi geometrisi kullanilir; boylece baslik cubugu
    da platformun parcasi olur.
    """
    dpy = _load()
    if dpy is None:
        return None

    top = _top_level(win)
    if top is None:
        return None
    attrs = _attributes(top)
    if attrs is None or attrs.map_state != IS_VIEWABLE:
        return None

    x, y = attrs.x, attrs.y
    child = c_ulong()
    dest_x = c_int()
    dest_y = c_int()
    try:
        if _xlib.XTranslateCoordinates(
            dpy,
            c_ulong(top),
            c_ulong(_root),
            0,
            0,
            byref(dest_x),
            byref(dest_y),
            byref(child),
        ):
            x, y = dest_x.value, dest_y.value
    except Exception:
        pass

    return (x, y, x + attrs.width, y + attrs.height)


def virtual_screen_rect() -> tuple[int, int, int, int]:
    """Tum ekranlari kapsayan sanal masaustu: (x, y, genislik, yukseklik)."""
    if _load() is None:
        from .fallback import virtual_screen_rect as fallback_rect

        return fallback_rect()
    attrs = _attributes(_root)
    if attrs is None:
        from .fallback import virtual_screen_rect as fallback_rect

        return fallback_rect()
    return (attrs.x, attrs.y, attrs.width, attrs.height)


def is_topmost(hwnd: int) -> bool:
    above = _atom("_NET_WM_STATE_ABOVE")
    if above and above in _states(int(hwnd)):
        return True
    return z_order_index(int(hwnd)) == 0


def find_window(class_name: str, title: str | None = None) -> int | None:
    for win in list_windows():
        if title is not None and title not in win.get("title", ""):
            continue
        if class_name and class_name in win.get("class_name", ""):
            return int(win["hwnd"])
        if title is not None:
            return int(win["hwnd"])
    return None


def z_order_index(hwnd: int) -> int | None:
    """Pencerenin gorunur yigin sirasindaki yeri. Kucuk deger = daha onde.

    Paneller, masaustu, menuler ve minik tepsi pencereleri sayilmaz; boylece
    "ustumde gercek bir pencere var mi?" sorusuna dogru cevap verilir.
    """
    dpy = _load()
    if dpy is None:
        return None
    top = _top_level(int(hwnd))
    if top is None:
        return None

    root_return = c_ulong()
    parent_return = c_ulong()
    children = POINTER(c_ulong)()
    count = c_uint()
    try:
        if not _xlib.XQueryTree(
            dpy,
            c_ulong(_root),
            byref(root_return),
            byref(parent_return),
            byref(children),
            byref(count),
        ):
            return None
        try:
            ids = [int(children[i]) for i in range(count.value)]
        finally:
            if children:
                _xlib.XFree(children)
    except Exception:
        return None

    # XQueryTree cocuklari alttan uste verir; en onde olan listenin sonudur.
    ids.reverse()
    skip_types = {_atom(name) for name in _SKIP_TYPES}
    index = 0
    for win in ids:
        if win == top:
            return index
        attrs = _attributes(win)
        if attrs is None or attrs.map_state != IS_VIEWABLE:
            continue
        if attrs.override_redirect:
            continue
        if attrs.width < 40 or attrs.height < 40:
            continue
        if skip_types and _types(win) & skip_types:
            continue
        index += 1
    return None


def _set_above(win: int, on: bool) -> None:
    dpy = _load()
    if dpy is None:
        return
    message_type = _atom("_NET_WM_STATE")
    above = _atom("_NET_WM_STATE_ABOVE")
    if not message_type or not above:
        return

    event = XEvent()
    event.xclient.type = CLIENT_MESSAGE
    event.xclient.serial = 0
    event.xclient.send_event = True
    event.xclient.display = dpy
    event.xclient.window = c_ulong(win)
    event.xclient.message_type = message_type
    event.xclient.format = 32
    event.xclient.data[0] = 1 if on else 0   # _NET_WM_STATE_ADD / _REMOVE
    event.xclient.data[1] = above
    event.xclient.data[2] = 0
    event.xclient.data[3] = 2                # kaynak: araç/pager

    try:
        _xlib.XSendEvent(
            dpy,
            c_ulong(_root),
            False,
            SUBSTRUCTURE_REDIRECT | SUBSTRUCTURE_NOTIFY,
            byref(event),
        )
        _xlib.XFlush(dpy)
    except Exception:
        pass


def set_topmost(hwnd: int, on: bool = True) -> None:
    """Pencereyi tasimadan/aktiflestirmeden yiginin en ustune tasir."""
    dpy = _load()
    if dpy is None:
        return
    win = int(hwnd)
    top = _top_level(win) or win
    try:
        if on:
            _xlib.XRaiseWindow(dpy, c_ulong(top))
        else:
            _xlib.XLowerWindow(dpy, c_ulong(top))
        _xlib.XFlush(dpy)
    except Exception:
        pass
    _set_above(win, on)


def list_windows(exclude_hwnd: int | None = None) -> list[dict]:
    """Ekranda gorunen, uzerine konulabilecek pencerelerin dikdortgenleri."""
    if _load() is None:
        return []

    result: list[dict] = []
    skip = int(exclude_hwnd) if exclude_hwnd else 0
    skip_types = {_atom(name) for name in _SKIP_TYPES}
    skip_states = {_atom(name) for name in _SKIP_STATES}

    for win in _client_windows():
        try:
            if win == skip:
                continue
            attrs = _attributes(win)
            if attrs is None or attrs.map_state != IS_VIEWABLE:
                continue
            if attrs.override_redirect:
                continue
            if skip_types and _types(win) & skip_types:
                continue
            states = _states(win)
            if skip_states and set(states) & skip_states:
                continue
            if not _on_current_desktop(win):
                continue

            rect = _frame_rect(win)
            if rect is None:
                continue
            left, top, right, bottom = rect
            width, height = right - left, bottom - top
            if width < 80 or height < 60:
                continue
            if left < -20000 or top < -20000:
                continue

            result.append(
                {
                    "hwnd": win,
                    "left": left,
                    "top": top,
                    "right": right,
                    "bottom": bottom,
                    "title": _title(win),
                    "class_name": _class_name(win),
                }
            )
        except Exception:
            continue
    return result
