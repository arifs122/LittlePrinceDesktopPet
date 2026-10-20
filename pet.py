"""Masaustu Kucuk Prens: seffaf, her zaman ustte pencere + basit fizik + yoldaslar."""
from __future__ import annotations

import math
import os
import random

from PySide6.QtCore import QPoint, QPointF, QRectF, Qt, QTimer
from PySide6.QtGui import (
    QAction,
    QColor,
    QFontMetrics,
    QGuiApplication,
    QPainter,
    QPen,
    QPixmap,
    QPolygonF,
)
from PySide6.QtWidgets import QApplication, QMenu, QWidget

import companion as companion_mod
import config
import features
import i18n
import prince
import win32_windows
from ui_font import make_font

# ---------------------------------------------------------------------------
# Sabitler
# ---------------------------------------------------------------------------
TICK_MS = 16                 # ~60 FPS
GRAVITY = 1.15
MAX_FALL = 22.0
PLATFORM_REFRESH_TICKS = 30  # ~0.5 sn
TOPMOST_REFRESH_TICKS = 15   # ~0.25 sn: gorev cubugu one gecerse geri al
RECKLESS_CHANCE = 0.15       # pencereden asagi atlama cesareti
MAX_JUMP_HEIGHT = 150        # bu yukseklige kadar yukari ziplayabilir
JUMP_COOLDOWN = 140          # basarisiz denemeden sonra bekleme (tik)

ANIM_SPEED = {"walk": 5, "idle": 12, "sit": 14, "sleep": 4, "fall": 20, "drag": 8}

DEBUG = bool(os.environ.get("KP_DEBUG"))

SLEEP_AFTER_MIN = 15       # en az bu kadar saniye bosta kalinca uyur


class Bubble(QWidget):
    """Konusma balonu. Fare olaylarini engellemez, kendi kendine kapanir."""

    MAX_W = 250

    def __init__(self):
        super().__init__(
            None,
            Qt.Window
            | Qt.FramelessWindowHint
            | Qt.WindowStaysOnTopHint
            | Qt.Tool
            | Qt.WindowDoesNotAcceptFocus
            | Qt.NoDropShadowWindowHint,
        )
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setAttribute(Qt.WA_TransparentForMouseEvents)
        self.setAttribute(Qt.WA_ShowWithoutActivating)
        self._text = ""
        self._font = make_font(10)
        self._anchor = None
        self._timer = QTimer(self)
        self._timer.setSingleShot(True)
        self._timer.timeout.connect(self.hide)

    def say(self, text: str, seconds: float = 4.5, anchor=None):
        """anchor: x, y, W, H olan bir pencere (yoldas). None ise karakter."""
        self._anchor = anchor
        self._text = text
        fm = QFontMetrics(self._font)
        rect = fm.boundingRect(
            QRectF(0, 0, self.MAX_W, 400).toRect(),
            Qt.TextWordWrap | Qt.AlignLeft | Qt.AlignVCenter,
            text,
        )
        self.resize(max(80, rect.width() + 26), rect.height() + 22)
        self.show()
        self.raise_()
        self.update()
        self._timer.start(int(seconds * 1000))

    def retarget(self):
        """Konusan kisi gittiyse balonu tekrar karaktere bagla."""
        self._anchor = None

    def follow(self, pet: "PetWindow"):
        target = self._anchor if self._anchor is not None else pet
        x = target.x + target.W / 2 - self.width() / 2
        y = target.y - self.height() - 4
        scr = QGuiApplication.primaryScreen().availableGeometry()
        x = max(scr.left() + 2, min(x, scr.right() - self.width() - 2))
        if y < scr.top() + 2:
            y = target.y + target.H + 4
        self.move(int(x), int(y))

    def paintEvent(self, _e):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing, True)
        r = QRectF(1, 1, self.width() - 2, self.height() - 6)

        p.setPen(QPen(QColor("#4E342E"), 1.5))
        p.setBrush(QColor(255, 255, 255, 242))
        p.drawRoundedRect(r, 9, 9)

        tail = QPolygonF(
            [
                QPoint(int(self.width() / 2) - 7, int(r.bottom())),
                QPoint(int(self.width() / 2) + 7, int(r.bottom())),
                QPoint(int(self.width() / 2), int(r.bottom()) + 6),
            ]
        )
        p.setPen(QPen(QColor("#4E342E"), 1.2))
        p.setBrush(QColor(255, 255, 255, 242))
        p.drawPolygon(tail)

        p.setPen(QColor("#3E2723"))
        p.setFont(self._font)
        p.drawText(self.rect().adjusted(13, 8, -13, -12), Qt.TextWordWrap, self._text)


class PetWindow(QWidget):
    BASE_FLAGS = (
        Qt.Window
        | Qt.FramelessWindowHint
        | Qt.Tool
        | Qt.WindowDoesNotAcceptFocus
        | Qt.NoDropShadowWindowHint
    )

    def __init__(self):
        super().__init__(None, self.BASE_FLAGS | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setAttribute(Qt.WA_ShowWithoutActivating)
        self.setWindowTitle("Küçük Prens")

        self.cfg = config.load()
        self.save_ok = True
        self.tr = i18n.get(self.cfg.get("language", "auto"))
        self.scale = float(self.cfg["scale"])
        self.walk_speed = float(self.cfg["walk_speed"])
        self.tick_ms = TICK_MS
        self.W = int(round(prince.W * self.scale))
        self.H = int(round(prince.H * self.scale))
        self.resize(self.W, self.H)
        self._on_top = bool(self.cfg["always_on_top"])

        # --- durum ---
        self.x = 0.0
        self.y = 0.0
        self.vy = 0.0
        self.facing = 1
        self.state = "idle"
        self.anim_frame = 0
        self.action_frames = 30
        self.reckless = False
        self.sit_locked = False
        self.frame_counter = 0
        self.support_y = 0.0
        self.support_hwnd = None
        self.jump_cooldown = 0
        self.platforms: list[dict] = []
        self.companion = None
        self.chat = None

        # --- uyku / tepki / isinlanma ---
        self.idle_seconds = 0.0
        self.cursor_check = 0
        self.fall_from_y: float | None = None
        self.land_frames = 0
        self.tp_phase = 0          # 0: yok, 1: kuculuyor, 2: buyuyor
        self.tp_scale = 1.0
        self.tp_target = None
        self.tp_cooldown = 0.0

        # --- fare ---
        self._press_global = QPoint()
        self._drag_offset = QPoint()
        self._dragging = False

        self._cache: dict[tuple, QPixmap] = {}
        self._last_pos: tuple[int, int] | None = None
        self._last_paint: tuple | None = None
        self.bubble = Bubble()
        self._settings = None

        self._update_scaling()
        self.refresh_platforms()
        self.spawn()

        self._timer = QTimer(self)
        self._timer.timeout.connect(self.tick)
        self._timer.start(TICK_MS)

    # ------------------------------------------------------------------
    # DPI / koordinat donusumu
    # ------------------------------------------------------------------
    def _update_scaling(self):
        vx, vy, vw, vh = win32_windows.virtual_screen_rect()
        screens = QGuiApplication.screens()
        qx = min(s.geometry().left() for s in screens)
        qy = min(s.geometry().top() for s in screens)
        qr = max(s.geometry().right() for s in screens)
        qb = max(s.geometry().bottom() for s in screens)
        qw = max(1, qr - qx + 1)
        qh = max(1, qb - qy + 1)
        self._scale_x = (vw / qw) if qw else 1.0
        self._scale_y = (vh / qh) if qh else 1.0
        self._phys_ox, self._phys_oy = vx, vy
        self._qt_ox, self._qt_oy = qx, qy

    def _lx(self, phys_x: float) -> float:
        return (phys_x - self._phys_ox) / self._scale_x + self._qt_ox

    def _ly(self, phys_y: float) -> float:
        return (phys_y - self._phys_oy) / self._scale_y + self._qt_oy

    def _anchor(self, state: str) -> float:
        return prince.ANCHOR.get(state, prince.H) * self.scale

    def _screen_bottom_at(self, px: float):
        """Verilen x'teki ekranin gercek alt kenari (logical).

        Not: availableGeometry() gorev cubugunun USTUNU verir; bacaklar gorev
        cubugunun uzerine sarkabilsin diye gercek ekran kenarini kullaniyoruz.
        """
        best = None
        for scr in QGuiApplication.screens():
            g = scr.geometry()
            if g.left() <= px <= g.right() + 1:
                b = g.bottom() + 1
                if best is None or b > best:
                    best = b
        return best

    def _rest_y(self) -> float:
        """Karakterin ayakta/otururken durmasi gereken pencere ust konumu.

        Oturma pozunda bacaklar platformun altina sarkar; ekranin en altina
        oturursa pencere ekrandan tasip bacaklar kirpilmasin diye yukari kaydirilir.
        """
        a = self._anchor(self.state)
        bottom = self._screen_bottom_at(self.x + self.W / 2)
        if bottom is not None:
            a = max(a, self.support_y + self.H - float(bottom))
        return self.support_y - a

    def _assert_topmost(self):
        """Gorev cubugu / baska ustte pencereler one gecmisse tekrar one gecir.

        Zaten en ust sirada isek HICBIR SEY yapmayiz; boylece gereksiz
        SetWindowPos cagrilari (ve olasi imlec/odak titremesi) olmaz.
        """
        if not self._on_top or self.state == "drag":
            return
        try:
            hwnd = int(self.winId())
            if win32_windows.z_order_index(hwnd) == 0:
                return
            win32_windows.set_topmost(hwnd, True)
        except Exception:
            pass

    # ------------------------------------------------------------------
    # Platformlar
    # ------------------------------------------------------------------
    def refresh_platforms(self):
        plats: list[dict] = []
        try:
            for win in win32_windows.list_windows(int(self.winId())):
                lx1, lx2 = self._lx(win["left"]), self._lx(win["right"])
                ly = self._ly(win["top"])
                if any(
                    -6 <= ly - s.availableGeometry().top() <= 6
                    for s in QGuiApplication.screens()
                ):
                    continue  # tam ekran / tepede yasli pencere
                plats.append({"x1": lx1, "x2": lx2, "y": ly, "hwnd": win["hwnd"]})
        except Exception:
            pass
        for scr in QGuiApplication.screens():
            g = scr.availableGeometry()
            plats.append(
                {"x1": g.left(), "x2": g.right() + 1, "y": g.bottom() + 1, "hwnd": None}
            )
        self.platforms = plats

    def _support_at(self, px: float, ref_y: float, tol: float):
        best = None
        best_d = None
        for pl in self.platforms:
            if pl["x1"] <= px <= pl["x2"]:
                d = abs(pl["y"] - ref_y)
                if d <= tol and (best_d is None or d < best_d):
                    best_d, best = d, pl
        return best

    def _landing(self, px: float, prev_feet: float, new_feet: float):
        best = None
        for pl in self.platforms:
            if pl["x1"] <= px <= pl["x2"]:
                if prev_feet <= pl["y"] <= new_feet + 1:
                    if best is None or pl["y"] < best["y"]:
                        best = pl
        return best

    def _refresh_support(self) -> bool:
        center = self.x + self.W / 2
        if self.support_hwnd is None:
            for pl in self.platforms:
                if pl["hwnd"] is None and pl["x1"] <= center <= pl["x2"]:
                    self.support_y = pl["y"]
                    return True
            return False
        for pl in self.platforms:
            if pl["hwnd"] == self.support_hwnd:
                if pl["x1"] <= center <= pl["x2"] and abs(pl["y"] - self.support_y) < 250:
                    self.support_y = pl["y"]
                    return True
        return False

    def _platform_under_pet(self):
        center = self.x + self.W / 2
        for pl in self.platforms:
            if pl["x1"] <= center <= pl["x2"] and abs(pl["y"] - self.support_y) < 4:
                return pl
        return None

    # ------------------------------------------------------------------
    # Baslangic / yeniden konumlandirma
    # ------------------------------------------------------------------
    def spawn(self):
        scr = QGuiApplication.primaryScreen().availableGeometry()
        floor_y = float(scr.bottom() + 1)

        self.support_hwnd = None
        self.support_y = floor_y
        self.x = float(scr.right() - self.W - 80)
        self.facing = -1

        cands = [
            pl
            for pl in self.platforms
            if pl["hwnd"] is not None
            and (pl["x2"] - pl["x1"]) >= self.W + 40
            and 40 <= pl["y"] <= floor_y - 80
        ]
        if cands:
            pl = min(cands, key=lambda p: p["y"])
            self.support_hwnd = pl["hwnd"]
            self.support_y = pl["y"]
            self.x = float(pl["x1"] + (pl["x2"] - pl["x1"]) / 2 - self.W / 2)
            self.facing = 1

        self.reckless = False
        self.jump_cooldown = 0
        self.sit_locked = False
        self._dismiss_companion()
        self.set_state("idle", frames=60)
        self._last_pos = None
        self.move(int(self.x), int(self.y))

    def respawn(self):
        self.refresh_platforms()
        self.spawn()
        self.raise_()

    # ------------------------------------------------------------------
    # Ayarlar
    # ------------------------------------------------------------------
    def apply_settings(self, values: dict):
        old_scale = self.scale
        self.cfg.update(values)
        self.save_ok = config.save(self.cfg)
        self.tr = i18n.get(self.cfg.get("language", "auto"))

        self.walk_speed = float(self.cfg["walk_speed"])
        new_scale = float(self.cfg["scale"])
        if abs(new_scale - old_scale) > 1e-6:
            self.scale = new_scale
            self.W = int(round(prince.W * self.scale))
            self.H = int(round(prince.H * self.scale))
            self._cache.clear()
            self._dismiss_companion()
            self.resize(self.W, self.H)
            if self.state not in ("fall", "drag"):
                self.y = self._rest_y()
            self._last_pos = None
            self.move(int(round(self.x)), int(round(self.y)))

        want_top = bool(self.cfg["always_on_top"])
        if want_top != self._on_top:
            self._on_top = want_top
            self.setWindowFlag(Qt.WindowStaysOnTopHint, want_top)
            self.show()
        self._assert_topmost()

    def open_settings(self):
        from settings_dialog import SettingsDialog

        if self._settings is None:
            self._settings = SettingsDialog(self)
        self._settings.show()
        self._settings.raise_()
        self._settings.activateWindow()

    # ------------------------------------------------------------------
    # Durum yonetimi
    # ------------------------------------------------------------------
    def set_state(self, state: str, frames: int | None = None):
        prev = self.state
        self.state = state
        if frames is not None:
            self.action_frames = frames
        if state not in ("fall", "drag"):
            self.y = self._rest_y()

        if state == "sit" and prev != "sit":
            self._summon_companion()
            self._assert_topmost()
        elif prev == "sit" and state != "sit":
            self._dismiss_companion()

    def choose_action(self):
        if self.sit_locked:
            return

        # Arada bir, baska bir yuzey varsa oraya isinlanir (bekleme suresi dolduysa)
        try:
            tp_chance = float(self.cfg.get("teleport_chance", 0.3))
            tp_cool = float(self.cfg.get("teleport_cooldown", 20))
        except Exception:
            tp_chance, tp_cool = 0.3, 20.0
        if self.tp_cooldown <= 0 and random.random() < tp_chance and self._start_teleport():
            self.tp_cooldown = max(0.0, tp_cool)
            return

        r = random.random()
        on_window = self.support_hwnd is not None
        try:
            sit_min = float(self.cfg.get("sit_min_seconds", 10))
        except Exception:
            sit_min = 10.0
        sit_frames_min = int(max(0.0, sit_min) * 1000 / TICK_MS)

        if r < (0.28 if on_window else 0.12):
            self.set_state("sit", frames=sit_frames_min + random.randint(0, 200))
            self.reckless = False
        elif r < 0.72:
            self.set_state("walk", frames=random.randint(80, 220))
            if random.random() < 0.6:
                self.facing *= -1
            self.reckless = random.random() < RECKLESS_CHANCE
        else:
            self.set_state("idle", frames=random.randint(60, 160))
            self.reckless = False

    def sit_down(self):
        """'Otur' komutu: kullanici kaldirana kadar oturur."""
        self._touch()
        self.sit_locked = True
        self.reckless = False
        self.set_state("sit")

    def stand_up(self):
        """'Kalk' komutu."""
        self._touch()
        self.sit_locked = False
        self.choose_action()

    # ------------------------------------------------------------------
    # Uyku
    # ------------------------------------------------------------------
    def _touch(self):
        """Kullanici etkilesimi oldu: uyku sayacini sifirla, uyuyorsa uyandir."""
        self.idle_seconds = 0.0
        if self.state == "sleep":
            self.wake()

    def wake(self):
        if self.state != "sleep":
            return
        self.anim_frame = 0
        self.state = "idle"
        self.action_frames = random.randint(30, 70)
        self.y = self._rest_y()
        self._last_paint = None
        self.bubble.say(random.choice(self.tr["wake"]), 2.8)

    def _cursor_check(self):
        """Fare karaktere yaklastiysa uyandir."""
        if self.state != "sleep":
            return
        from PySide6.QtGui import QCursor

        c = QCursor.pos()
        cx = self.x + self.W / 2
        cy = self.y + self.H / 2
        if abs(c.x() - cx) < 90 + self.W and abs(c.y() - cy) < 90 + self.H:
            self.idle_seconds = 0.0
            self.wake()

    def _sleep_after_seconds(self) -> float:
        try:
            return max(SLEEP_AFTER_MIN, float(self.cfg.get("sleep_after", 90)))
        except Exception:
            return 90.0

    def _check_sleep(self):
        if not self.cfg.get("sleep_enabled", True):
            return
        if self.sit_locked or self.tp_phase:
            return
        if self.chat is not None and self.chat.isVisible():
            return
        if self.state in ("sleep", "drag", "fall"):
            return
        if self.idle_seconds >= self._sleep_after_seconds():
            self.reckless = False
            self.set_state("sleep")
            self.anim_frame = 0

    # ------------------------------------------------------------------
    # Sohbet penceresi
    # ------------------------------------------------------------------
    def open_chat(self):
        if not features.ai_enabled():
            return
        from chat import ChatWindow

        self._touch()
        if self.state == "sleep":
            self.wake()
        if self.chat is None:
            self.chat = ChatWindow(self)
        self.chat.show_chat()

    # ------------------------------------------------------------------
    # Yoldaslar (tilki / gul)
    # ------------------------------------------------------------------
    def _summon_companion(self):
        if self.companion is not None:
            return
        if random.random() > float(self.cfg["companion_chance"]):
            return
        species = random.choice(list(companion_mod.SPECIES.keys()))
        side = random.choice([-1, 1])
        plat = self._platform_under_pet()
        x1 = plat["x1"] if plat else self.x - 300
        x2 = plat["x2"] if plat else self.x + self.W + 300
        try:
            comp = companion_mod.Companion(species, self, side, x1, x2)
        except Exception:
            return
        self.companion = comp
        comp.show()

        # Ya yoldasin kendi sozu, ya da Prens'in onun hakkinda soyledigi soz
        options = [(False, line) for line in self.tr.get(species, [])]
        said = self.tr.get(species + "_said")
        if said:
            options.append((True, said))
        if options:
            own, text = random.choice(options)
            QTimer.singleShot(700, lambda: self._companion_says(text, own))

    def _companion_says(self, text: str, own: bool):
        """own=True ise balon yoldasin, degilse Kucuk Prens'in uzerinde cikar."""
        if own:
            comp = self.companion
            if comp is None:
                return
            self.bubble.say(text, 4.5, anchor=comp)
        else:
            self.bubble.say(text, 4.5)

    def _dismiss_companion(self):
        if self.companion is not None:
            try:
                self.companion.leave()
            except Exception:
                pass
        self.companion = None
        try:
            self.bubble.retarget()
        except Exception:
            pass

    # ------------------------------------------------------------------
    def start_fall(self):
        prev = self.state
        self.state = "fall"
        self.vy = 0.0
        self.anim_frame = 0
        if prev in ("sit", "sleep"):
            self.y = self.support_y - self.H
        self.fall_from_y = self.y
        self.support_hwnd = None
        self._dismiss_companion()

    def land_on(self, pl: dict):
        from_y = self.fall_from_y if self.fall_from_y is not None else pl["y"] - self.H
        drop = pl["y"] - (from_y + self.H)

        self.support_y = pl["y"]
        self.support_hwnd = pl["hwnd"]
        self.vy = 0.0
        self.anim_frame = 0
        self.state = "idle"
        self.action_frames = random.randint(20, 45)
        self.y = self._rest_y()
        self.fall_from_y = None
        self._assert_topmost()

        # Sert inis: kisa bir yaylanma + tepki
        if drop > 120:
            self.land_frames = 16
            if random.random() < 0.7:
                QTimer.singleShot(
                    140, lambda: self.bubble.say(random.choice(self.tr["land"]), 2.0)
                )

    # ------------------------------------------------------------------
    # Dongu
    # ------------------------------------------------------------------
    def tick(self):
        self.frame_counter += 1
        if self.frame_counter % PLATFORM_REFRESH_TICKS == 0:
            self.refresh_platforms()
        if self.frame_counter % TOPMOST_REFRESH_TICKS == 0:
            self._assert_topmost()
        if self.jump_cooldown > 0:
            self.jump_cooldown -= 1
        if self.tp_cooldown > 0:
            self.tp_cooldown = max(0.0, self.tp_cooldown - TICK_MS / 1000.0)
        if self.land_frames > 0:
            self.land_frames -= 1

        if self.state != "drag":
            self.idle_seconds += TICK_MS / 1000.0

        # fare yaklasinca uyan
        self.cursor_check += 1
        if self.cursor_check % 12 == 0:
            self._cursor_check()

        if self.tp_phase:
            self._tick_teleport()
        elif self.state == "drag":
            pass
        elif self.state == "fall":
            self._tick_fall()
        else:
            self._tick_grounded()

        self._check_sleep()

        self.anim_frame += 1

        pos = (int(round(self.x)), int(round(self.y)))
        if pos != self._last_pos:
            self.move(*pos)
            self._last_pos = pos

        if self.bubble.isVisible():
            self.bubble.follow(self)

        speed = ANIM_SPEED.get(self.state, 12)
        paint_key = (
            self.state,
            self.anim_frame // speed,
            self.facing,
            round(self.tp_scale, 2),
            self.land_frames,
        )
        if paint_key != self._last_paint:
            self._last_paint = paint_key
            self.update()

        if DEBUG and self.frame_counter % 60 == 0:
            print(
                f"[{self.frame_counter}] state={self.state} x={self.x:.0f} y={self.y:.0f} "
                f"facing={self.facing} support_y={self.support_y:.0f} "
                f"hwnd={self.support_hwnd} plats={len(self.platforms)} "
                f"comp={self.companion.species if self.companion else '-'} "
                f"idle={self.idle_seconds:.0f}s tp={self.tp_phase}"
            )

    def _tick_fall(self):
        self.vy = min(self.vy + GRAVITY, MAX_FALL)
        prev_feet = self.y + self.H
        self.y += self.vy
        new_feet = self.y + self.H
        pl = self._landing(self.x + self.W / 2, prev_feet, new_feet)
        if pl is not None:
            self.land_on(pl)
            return

        floors = [s.availableGeometry().bottom() + 1 for s in QGuiApplication.screens()]
        if floors and self.y + self.H > max(floors) + 400:
            self._snap_to_floor()

    def _snap_to_floor(self):
        cx = self.x + self.W / 2
        best = None
        for s in QGuiApplication.screens():
            g = s.availableGeometry()
            dx = 0.0 if g.left() <= cx <= g.right() else min(
                abs(cx - g.left()), abs(cx - g.right())
            )
            if best is None or dx < best[0]:
                best = (dx, g)
        g = best[1] if best else QGuiApplication.primaryScreen().availableGeometry()

        self.x = float(max(g.left(), min(self.x, g.right() - self.W)))
        self.vy = 0.0
        self.anim_frame = 0
        self.state = "idle"
        self.action_frames = 30
        self.support_hwnd = None
        self.support_y = float(g.bottom() + 1)
        self.y = self.support_y - self.H

    def _tick_grounded(self):
        if not self._refresh_support():
            self.start_fall()
            return

        self.y = self._rest_y()

        if not self.sit_locked and self.state != "sleep":
            self.action_frames -= 1
            if self.action_frames <= 0:
                self.choose_action()

            if self.state == "walk":
                nx = self.x + self.facing * self.walk_speed
                ahead = nx + self.W / 2 + (self.W / 2 - 8) * self.facing
                supported = self._support_at(ahead, self.support_y, 4) is not None
                if supported:
                    self.x = nx
                elif self.reckless and self.support_hwnd is not None:
                    self.x = nx  # pencereden asagi atlar
                else:
                    self.facing *= -1
                self._try_jump()

    def _try_jump(self) -> bool:
        if self.jump_cooldown > 0:
            return False
        feet = self.support_y
        center = self.x + self.W / 2
        target = None
        for pl in self.platforms:
            dy = feet - pl["y"]
            if not (30 <= dy <= MAX_JUMP_HEIGHT):
                continue
            if pl["hwnd"] == self.support_hwnd and abs(pl["y"] - feet) < 1:
                continue
            near_left = pl["x1"] + 2 <= center <= pl["x1"] + 45
            near_right = pl["x2"] - 45 <= center <= pl["x2"] - 2
            if not (near_left or near_right):
                continue
            if target is None or pl["y"] > target["y"]:
                target = pl
        if target is None or random.random() > 0.30:
            return False

        dy = feet - target["y"]
        self.vy = -math.sqrt(2 * GRAVITY * (dy + 16))
        self.state = "fall"
        self.anim_frame = 0
        self.jump_cooldown = JUMP_COOLDOWN
        return True

    # ------------------------------------------------------------------
    # Isinlanma (baska bir yuzeye atlama)
    # ------------------------------------------------------------------
    def _pick_teleport_target(self):
        """Uzerinde durulabilecek, baska bir platform secer."""
        if not self.platforms:
            return None
        center = self.x + self.W / 2
        cands = []
        for pl in self.platforms:
            if (pl["x2"] - pl["x1"]) < self.W + 24:
                continue
            same = (
                abs(pl["y"] - self.support_y) < 6
                and pl["x1"] <= center <= pl["x2"]
            )
            if same:
                continue
            cands.append(pl)
        if not cands:
            return None
        pl = random.choice(cands)
        x = random.uniform(pl["x1"] + 10, pl["x2"] - self.W - 10)
        return pl, x

    def _start_teleport(self) -> bool:
        target = self._pick_teleport_target()
        if target is None:
            return False
        self.tp_target = target
        self.tp_phase = 1
        self.tp_scale = 1.0
        self.anim_frame = 0
        self.reckless = False
        self.sit_locked = False
        self._dismiss_companion()
        self._last_paint = None
        return True

    def _tick_teleport(self):
        if self.tp_phase == 1:
            self.tp_scale -= 0.11
            if self.tp_scale <= 0.02:
                pl, x = self.tp_target
                self.support_hwnd = pl["hwnd"]
                self.support_y = pl["y"]
                self.x = x
                self.facing = random.choice([-1, 1])
                self.state = "idle"
                self.action_frames = random.randint(60, 150)
                self.y = self._rest_y()
                self._last_pos = None
                self.tp_phase = 2
                self._assert_topmost()
        else:
            self.tp_scale = min(1.0, self.tp_scale + 0.11)
            if self.tp_scale >= 1.0:
                self.tp_scale = 1.0
                self.tp_phase = 0
                self.anim_frame = 0

    # ------------------------------------------------------------------
    # Cizim
    # ------------------------------------------------------------------
    def _pixmap(self, state: str, frame: int, facing: int) -> QPixmap:
        key = (state, frame, facing)
        pm = self._cache.get(key)
        if pm is None:
            pm = prince.render(state, frame, facing=facing, scale=self.scale)
            self._cache[key] = pm
        return pm

    def paintEvent(self, _e):
        speed = ANIM_SPEED.get(self.state, 12)
        frame = (self.anim_frame // speed) % prince.frame_count(self.state)
        pm = self._pixmap(self.state, frame, self.facing)

        p = QPainter(self)
        p.setRenderHint(QPainter.SmoothPixmapTransform, True)

        # Isinlanma: kuculup kaybolma / buyuyerek belirme
        scale = max(0.02, self.tp_scale)
        # Sert inis: kisa bir yaylanma
        squash = 1.0
        if self.land_frames > 0:
            t = self.land_frames / 16.0
            squash = 0.80 + 0.20 * (1.0 - t) * (1.0 - t)

        w = pm.width() * scale
        h = pm.height() * scale * squash
        x = (self.width() - w) / 2.0
        y = self.height() - h
        p.drawPixmap(QRectF(x, y, w, h), pm, QRectF(pm.rect()))

        if self.tp_phase:
            self._paint_sparkles(p)
        if self.state == "sleep":
            self._paint_zzz(p)
        if self.land_frames > 9:
            self._paint_dust(p)

    def _paint_zzz(self, p: QPainter):
        font = make_font(max(7, int(8 * self.scale)), bold=True)
        font.setBold(True)
        p.setFont(font)
        for i in range(3):
            t = ((self.anim_frame / 45.0) + i / 3.0) % 1.0
            size = 0.55 + 0.6 * t
            alpha = int(210 * (1.0 - t))
            p.setPen(QPen(QColor(150, 185, 215, max(0, alpha)), 2))
            p.save()
            p.translate(
                self.W * 0.60 + t * self.W * 0.36,
                self.H * 0.46 - t * self.H * 0.34,
            )
            p.scale(size, size)
            p.drawText(QPointF(0, 0), "z")
            p.restore()

    def _paint_sparkles(self, p: QPainter):
        cx, cy = self.W / 2.0, self.H / 2.0
        radius = self.W * (0.55 + 0.45 * (1.0 - self.tp_scale))
        p.setPen(Qt.NoPen)
        for i in range(8):
            a = (i / 8.0) * 2 * math.pi + self.anim_frame / 7.0
            r = radius * (0.65 + 0.35 * ((i % 3) / 2.0))
            px = cx + math.cos(a) * r
            py = cy + math.sin(a) * r * 0.75
            s = max(1.5, 3.4 * (0.4 + self.tp_scale))
            alpha = int(235 * (1.0 - self.tp_scale * 0.55))
            p.setBrush(QColor(255, 236, 150, max(60, alpha)))
            p.drawPolygon(
                QPolygonF(
                    [
                        QPointF(px, py - s),
                        QPointF(px + s * 0.36, py),
                        QPointF(px, py + s),
                        QPointF(px - s * 0.36, py),
                    ]
                )
            )

    def _paint_dust(self, p: QPainter):
        t = 1.0 - self.land_frames / 16.0
        p.setPen(Qt.NoPen)
        for side in (-1, 1):
            for k in range(3):
                px = self.W / 2 + side * self.W * (0.16 + 0.20 * k) * (0.35 + t)
                py = self.H - 3 - k * 2.5
                r = max(0.8, (3.2 - k * 0.7) * (1.0 - t))
                p.setBrush(QColor(225, 230, 235, int(150 * (1.0 - t))))
                p.drawEllipse(QPointF(px, py), r, r)

    # ------------------------------------------------------------------
    # Fare
    # ------------------------------------------------------------------
    def mousePressEvent(self, e):
        self._touch()
        if e.button() == Qt.LeftButton:
            self._press_global = e.globalPosition().toPoint()
            self._drag_offset = self._press_global - self.pos()
            self._dragging = False
            e.accept()

    def mouseMoveEvent(self, e):
        if e.buttons() & Qt.LeftButton:
            gp = e.globalPosition().toPoint()
            if not self._dragging:
                if (gp - self._press_global).manhattanLength() < 5:
                    return
                self._dragging = True
                self._touch()
                self.sit_locked = False
                self.tp_phase = 0
                self.tp_scale = 1.0
                self.state = "drag"
                self.anim_frame = 0
                self._dismiss_companion()
            self.move(gp - self._drag_offset)
            self.x = float(self.pos().x())
            self.y = float(self.pos().y())
            e.accept()

    def mouseReleaseEvent(self, e):
        if e.button() != Qt.LeftButton:
            return
        if self._dragging:
            self._dragging = False
            self.start_fall()
        else:
            self.react()
        e.accept()

    def mouseDoubleClickEvent(self, e):
        if e.button() == Qt.LeftButton:
            self.greet()
            e.accept()

    def react(self):
        from PySide6.QtGui import QCursor

        self._touch()
        c = QCursor.pos()
        self.facing = 1 if c.x() >= self.x + self.W / 2 else -1
        if self.state in ("idle", "sit") and not self.sit_locked:
            self.action_frames = max(self.action_frames, 40)
        self.update()

    def greet(self, text: str | None = None):
        self.bubble.say(text or random.choice(self.tr["quotes"]))

    # ------------------------------------------------------------------
    def contextMenuEvent(self, e):
        self._touch()
        m = self.tr["menu"]
        menu = QMenu()
        title = QAction("Küçük Prens", menu)
        title.setEnabled(False)
        menu.addAction(title)
        menu.addSeparator()

        if features.ai_enabled():
            menu.addAction(m["chat"], self.open_chat)
            menu.addSeparator()

        if self.state == "sleep":
            menu.addAction(m["wake"], self.wake)
        elif self.sit_locked:
            menu.addAction(m["stand"], self.stand_up)
        else:
            menu.addAction(m["sit"], self.sit_down)
        menu.addAction(m["quote"], self.greet)
        if not self.sit_locked:
            menu.addAction(m["walk"], self._start_walking)
            menu.addAction(m["teleport"], self._menu_teleport)
        menu.addSeparator()
        menu.addAction(m["settings"], self.open_settings)
        menu.addAction(m["respawn"], self.respawn)
        menu.addSeparator()
        menu.addAction(m["quit"], QApplication.quit)
        menu.exec(e.globalPos())
        e.accept()

    def _menu_teleport(self):
        self._touch()
        if not self._start_teleport():
            self.bubble.say(self.tr["no_surface"], 2.5)

    def _start_walking(self):
        self.sit_locked = False
        self.reckless = False
        self.set_state("walk", frames=random.randint(120, 260))
