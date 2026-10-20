"""Kucuk Prens'in yanina gelen yardimcilar.

Turler:
  fox         - Tilki
  rose        - Gul (cam fanus icinde)
  lamplighter - Fenerci (feneri yanip soner)
  snake       - Yilan
  baobab      - Baobap agaci

Karakterler prince.py ile ayni uslupla, tamamen kod ile cizilir.
"""
from __future__ import annotations

import math

from PySide6.QtCore import QPointF, Qt
from PySide6.QtGui import (
    QColor,
    QPainter,
    QPainterPath,
    QPen,
    QPixmap,
    QRadialGradient,
)
from PySide6.QtWidgets import QWidget

from . import platforms as platform_api

# ---------------------------------------------------------------------------
# Tur tanimlari: (genislik, yukseklik, gelis sekli)
# ---------------------------------------------------------------------------
SPECIES = {
    "fox": (62, 56, "walk"),
    "rose": (48, 84, "grow"),
    "lamplighter": (58, 76, "walk"),
    "snake": (66, 62, "grow"),
    "baobab": (62, 78, "grow"),
}

# ---------------------------------------------------------------------------
# Renkler
# ---------------------------------------------------------------------------
FOX = QColor("#E8843C")
FOX_DARK = QColor("#C2651F")
FOX_LIGHT = QColor("#FBE6CE")
FOX_TIP = QColor("#5A3418")
FOX_EYE = QColor("#2E1A0F")

POT = QColor("#C1613C")
POT_DARK = QColor("#9E4C2C")
SOIL = QColor("#4A3628")
STEM = QColor("#3E8E41")
STEM_DARK = QColor("#2E6B31")
PETAL = QColor("#DC3B3B")
PETAL_DARK = QColor("#B32525")
PETAL_LIGHT = QColor("#EE6A6A")
GLASS = QColor(206, 232, 244, 44)
GLASS_EDGE = QColor(255, 255, 255, 125)
GLASS_HL = QColor(255, 255, 255, 78)

COAT = QColor("#33475B")
COAT_DARK = QColor("#25333F")
HAT = QColor("#22333B")
SKIN = QColor("#F6CDA6")
SKIN_DARK = QColor("#D9A97C")
LANTERN = QColor("#C9A227")
LANTERN_DARK = QColor("#8A6D14")
FLAME = QColor("#FFD54F")
FLAME_HOT = QColor("#FFF6C9")
FLAME_OFF = QColor("#7A7A7A")

SNAKE = QColor("#5C9E4E")
SNAKE_DARK = QColor("#3F7534")
SNAKE_BELLY = QColor("#CBD98A")
SNAKE_TONGUE = QColor("#D64545")
SNAKE_EYE = QColor("#2E1A0F")

BAOBAB_TRUNK = QColor("#A98868")
BAOBAB_TRUNK_DARK = QColor("#8A6B4E")
BAOBAB_LEAF = QColor("#4C8C4A")
BAOBAB_LEAF_DARK = QColor("#37703A")
BAOBAB_ROOT = QColor("#7B5E45")


def size_for(species: str, scale: float) -> tuple[int, int]:
    w, h, _ = SPECIES.get(species, SPECIES["fox"])
    return int(round(w * scale)), int(round(h * scale))


def arrive_mode(species: str) -> str:
    return SPECIES.get(species, SPECIES["fox"])[2]


def render(species: str, state: str, frame: int, facing: int = 1, scale: float = 1.0) -> QPixmap:
    w, h, _ = SPECIES.get(species, SPECIES["fox"])
    pm = QPixmap(int(round(w * scale)), int(round(h * scale)))
    pm.fill(Qt.transparent)

    p = QPainter(pm)
    p.setRenderHint(QPainter.Antialiasing, True)
    p.scale(scale, scale)
    if facing < 0:
        p.translate(w, 0)
        p.scale(-1, 1)

    if species == "fox":
        _draw_fox(p, state, frame)
    elif species == "rose":
        _draw_rose(p, frame)
    elif species == "lamplighter":
        _draw_lamplighter(p, state, frame)
    elif species == "snake":
        _draw_snake(p, frame)
    elif species == "baobab":
        _draw_baobab(p, frame)
    p.end()
    return pm


def frame_count(species: str, state: str) -> int:
    if species == "fox":
        return 6 if state == "walk" else 1
    return 1


# ---------------------------------------------------------------------------
# Cizim yardimcilari
# ---------------------------------------------------------------------------
def _limb(p: QPainter, x0, y0, x1, y1, width, color, mid=None):
    p.setPen(QPen(color, width, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
    p.setBrush(Qt.NoBrush)
    if mid is None:
        p.drawLine(QPointF(x0, y0), QPointF(x1, y1))
    else:
        path = QPainterPath(QPointF(x0, y0))
        path.quadTo(QPointF(mid[0], mid[1]), QPointF(x1, y1))
        p.drawPath(path)


def _dot(p: QPainter, x, y, r, color):
    p.setPen(Qt.NoPen)
    p.setBrush(color)
    p.drawEllipse(QPointF(x, y), r, r)


def _triangle(p: QPainter, pts, color):
    poly = QPainterPath(QPointF(*pts[0]))
    for pt in pts[1:]:
        poly.lineTo(QPointF(*pt))
    poly.closeSubpath()
    p.setPen(Qt.NoPen)
    p.setBrush(color)
    p.drawPath(poly)


# ---------------------------------------------------------------------------
# TILKI
# ---------------------------------------------------------------------------
def _ears(p: QPainter, head_cx, head_cy, head_r, wag):
    for dx, tilt in ((-head_r * 0.42, -1), (head_r * 0.36, 1)):
        bx = head_cx + dx
        by = head_cy - head_r * 0.72
        tipx = bx + tilt * 3.0 + wag * tilt
        tipy = by - head_r * 0.95
        _triangle(p, [(bx - 5, by + 2), (bx + 5, by + 2), (tipx, tipy)], FOX)
        _triangle(
            p, [(tipx - 2.2, tipy + 4.4), (tipx + 2.2, tipy + 4.4), (tipx, tipy)], FOX_TIP
        )


def _fox_head(p, head_cx, head_cy, head_r, blink, wag):
    _dot(p, head_cx, head_cy, head_r, FOX)
    muzzle = QPainterPath(QPointF(head_cx + head_r * 0.25, head_cy - 2.2))
    muzzle.quadTo(
        QPointF(head_cx + head_r * 1.55, head_cy + 0.4),
        QPointF(head_cx + head_r * 0.30, head_cy + 5.0),
    )
    muzzle.closeSubpath()
    p.setPen(Qt.NoPen)
    p.setBrush(FOX_LIGHT)
    p.drawPath(muzzle)
    _dot(p, head_cx + head_r * 1.42, head_cy + 0.6, 1.9, FOX_TIP)
    _ears(p, head_cx, head_cy, head_r, wag)
    if blink:
        p.setPen(QPen(FOX_EYE, 1.5, Qt.SolidLine, Qt.RoundCap))
        p.drawLine(
            QPointF(head_cx + 1.0, head_cy - 1.4), QPointF(head_cx + 5.2, head_cy - 1.4)
        )
    else:
        _dot(p, head_cx + 3.1, head_cy - 1.4, 1.8, FOX_EYE)


def _draw_fox(p: QPainter, state: str, frame: int):
    ground = SPECIES["fox"][1] - 1
    walking = state == "walk"

    if walking:
        t = (frame % 6) / 6.0
        swing = math.sin(t * 2 * math.pi)
        bob = -abs(math.sin(t * math.pi)) * 1.4
    else:
        swing = 0.0
        bob = math.sin(frame / 40.0 * 2 * math.pi) * 0.5

    wag = math.sin(frame / 4.0) * 0.8
    blink = (frame % 90) in (0, 1, 2)

    if walking:
        body_cy = 31 + bob
        tail = QPainterPath(QPointF(18, body_cy + 1))
        tail.cubicTo(
            QPointF(4, body_cy - 2),
            QPointF(2, body_cy - 18),
            QPointF(10, body_cy - 20 + wag),
        )
        tail.cubicTo(
            QPointF(13, body_cy - 10), QPointF(17, body_cy - 3), QPointF(24, body_cy - 1)
        )
        tail.closeSubpath()
        p.setPen(Qt.NoPen)
        p.setBrush(FOX)
        p.drawPath(tail)
        _dot(p, 9, body_cy - 17 + wag, 4.2, FOX_LIGHT)

        for i, lx in enumerate((16, 21, 32, 38)):
            near = i in (1, 2)
            col = FOX if near else FOX_DARK
            sw = (swing * 3.2) * (1 if i % 2 == 0 else -1)
            _limb(p, lx, body_cy + 8, lx + sw, ground, 4.6, col)

        p.setBrush(FOX)
        p.drawEllipse(QPointF(26, body_cy), 15.0, 10.0)
        p.setBrush(FOX_LIGHT)
        p.drawEllipse(QPointF(28, body_cy + 4.0), 11.0, 5.6)
        _fox_head(p, 45, 24 + bob, 9.5, blink, wag)
    else:
        haunch_cy = 41 + bob
        tail = QPainterPath(QPointF(16, haunch_cy - 4))
        tail.cubicTo(
            QPointF(2, haunch_cy - 8),
            QPointF(-1, haunch_cy - 24),
            QPointF(9, haunch_cy - 26 + wag),
        )
        tail.cubicTo(
            QPointF(12, haunch_cy - 16), QPointF(14, haunch_cy - 8), QPointF(22, haunch_cy - 6)
        )
        tail.closeSubpath()
        p.setPen(Qt.NoPen)
        p.setBrush(FOX)
        p.drawPath(tail)
        _dot(p, 8, haunch_cy - 23 + wag, 4.4, FOX_LIGHT)

        for lx in (32.0, 37.0):
            _limb(p, lx, 36 + bob, lx, ground, 4.8, FOX)

        p.setBrush(FOX)
        p.drawEllipse(QPointF(20, haunch_cy), 11.5, 11.5)
        p.drawEllipse(QPointF(30, 33 + bob), 11.0, 9.5)
        p.setBrush(FOX_LIGHT)
        p.drawEllipse(QPointF(31, 36 + bob), 7.0, 6.0)
        _fox_head(p, 41, 21 + bob, 9.5, blink, wag)


# ---------------------------------------------------------------------------
# GUL (cam fanus icinde)
# ---------------------------------------------------------------------------
def _leaf(p: QPainter, x, y, angle_deg, size, color):
    p.save()
    p.translate(x, y)
    p.rotate(angle_deg)
    p.setPen(Qt.NoPen)
    p.setBrush(color)
    path = QPainterPath(QPointF(0, 0))
    path.quadTo(QPointF(size * 0.55, -size * 0.42), QPointF(size, 0))
    path.quadTo(QPointF(size * 0.55, size * 0.42), QPointF(0, 0))
    p.drawPath(path)
    p.restore()


def _draw_rose(p: QPainter, frame: int):
    w, h = SPECIES["rose"][0], SPECIES["rose"][1]
    cx = w / 2.0
    base = h - 2.0

    t = frame / 60.0
    sway = math.sin(t * 2 * math.pi) * 1.6
    wob = math.sin(t * 2 * math.pi + 0.6) * 0.3

    pot_top = 64.0

    # --- saksinin govdesi ---
    p.setPen(Qt.NoPen)
    p.setBrush(POT)
    body = QPainterPath(QPointF(cx - 11, pot_top + 3))
    body.lineTo(QPointF(cx + 11, pot_top + 3))
    body.lineTo(QPointF(cx + 8, base - 1))
    body.lineTo(QPointF(cx - 8, base - 1))
    body.closeSubpath()
    p.drawPath(body)
    p.setBrush(SOIL)
    p.drawEllipse(QPointF(cx, pot_top + 4), 10.5, 3.0)
    p.setBrush(POT_DARK)
    p.drawRoundedRect(cx - 12.5, pot_top - 1.0, 25.0, 5.5, 2.0, 2.0)

    # --- sap ---
    p.setBrush(Qt.NoBrush)
    p.setPen(QPen(STEM, 3.0, Qt.SolidLine, Qt.RoundCap))
    stem = QPainterPath(QPointF(cx, pot_top))
    stem.quadTo(QPointF(cx + sway * 0.4, 48), QPointF(cx + sway, 32))
    p.drawPath(stem)

    # --- yapraklar ---
    _leaf(p, cx + sway * 0.6, 50, -22, 11.0, STEM)
    _leaf(p, cx + sway * 0.8, 43, 200, 10.0, STEM_DARK)

    # --- cicek ---
    fx = cx + sway
    fy = 28 + wob
    for ang in (-90, -30, 30, 90, 150, 210):
        a = math.radians(ang)
        px = fx + math.cos(a) * 3.3
        py = fy + math.sin(a) * 3.3
        p.setPen(Qt.NoPen)
        p.setBrush(PETAL)
        p.drawEllipse(QPointF(px, py), 4.3, 4.3)
    p.setBrush(PETAL_DARK)
    p.drawEllipse(QPointF(fx, fy), 5.1, 5.1)
    p.setBrush(PETAL_LIGHT)
    p.drawEllipse(QPointF(fx - 1.2, fy - 1.4), 2.5, 2.3)

    # ---------------------------------------------------------------
    # CAM FANUS
    # ---------------------------------------------------------------
    dome = QPainterPath(QPointF(4, base))
    dome.cubicTo(QPointF(4, 40), QPointF(9, 11), QPointF(cx, 11))
    dome.cubicTo(QPointF(w - 9, 11), QPointF(w - 4, 40), QPointF(w - 4, base))
    dome.closeSubpath()

    p.setPen(Qt.NoPen)
    p.setBrush(GLASS)
    p.drawPath(dome)

    # cam kenari
    p.setBrush(Qt.NoBrush)
    p.setPen(QPen(GLASS_EDGE, 1.6, Qt.SolidLine, Qt.RoundCap))
    p.drawPath(dome)

    # taban halkasi
    p.setPen(QPen(GLASS_EDGE, 2.2, Qt.SolidLine, Qt.RoundCap))
    p.drawLine(QPointF(4, base), QPointF(w - 4, base))

    # isik yansimasi
    p.setPen(Qt.NoPen)
    p.setBrush(GLASS_HL)
    hl = QPainterPath(QPointF(11, 56))
    hl.quadTo(QPointF(8, 34), QPointF(14, 20))
    hl.quadTo(QPointF(15, 34), QPointF(15, 56))
    hl.closeSubpath()
    p.drawPath(hl)

    # tepedeki tutamak
    p.setBrush(GLASS_EDGE)
    p.drawEllipse(QPointF(cx, 10), 3.2, 3.2)
    p.setBrush(GLASS)
    p.drawEllipse(QPointF(cx, 10), 2.0, 2.0)


# ---------------------------------------------------------------------------
# FENERCI
# ---------------------------------------------------------------------------
def _draw_lamplighter(p: QPainter, state: str, frame: int):
    ground = SPECIES["lamplighter"][1] - 1
    walking = state == "walk"
    cx = 24.0

    if walking:
        t = (frame % 6) / 6.0
        swing = math.sin(t * 2 * math.pi)
        bob = -abs(math.sin(t * math.pi)) * 1.2
    else:
        swing = 0.0
        bob = math.sin(frame / 45.0 * 2 * math.pi) * 0.7

    # fener 1 saniyede bir yanip soner
    lit = (frame // 62) % 2 == 0

    shoulder_y = 29 + bob
    hem_y = 56 + bob

    # --- bacaklar ---
    for side in (-1, 1):
        off = swing * 3.5 * side if walking else 0.0
        x0 = cx + side * 5.0
        _limb(p, x0, hem_y - 4, x0 + off, ground, 5.5, COAT_DARK)
        _dot(p, x0 + off, ground, 3.2, HAT)

    # --- paltosu ---
    p.setPen(Qt.NoPen)
    p.setBrush(COAT)
    coat = QPainterPath(QPointF(cx - 10, shoulder_y))
    coat.lineTo(QPointF(cx + 10, shoulder_y))
    coat.lineTo(QPointF(cx + 12, hem_y))
    coat.lineTo(QPointF(cx - 12, hem_y))
    coat.closeSubpath()
    p.drawPath(coat)
    # kemer
    p.setBrush(COAT_DARK)
    p.drawRect(cx - 11, hem_y - 18, 22, 3.5)

    # --- kollar ---
    # sol kol asagida
    _limb(p, cx - 9, shoulder_y + 3, cx - 13, hem_y - 10, 5.0, COAT)
    _dot(p, cx - 13, hem_y - 10, 2.7, SKIN)

    # sag kol feneri tutuyor
    hand_x, hand_y = cx + 15, hem_y - 14
    _limb(p, cx + 9, shoulder_y + 3, hand_x, hand_y, 5.0, COAT, mid=(cx + 14, shoulder_y + 12))
    _dot(p, hand_x, hand_y, 2.7, SKIN)

    # --- fener ---
    lx, ly = hand_x + 2.5, hand_y + 12
    if lit:
        g = QRadialGradient(QPointF(lx, ly), 17)
        g.setColorAt(0.0, QColor(255, 226, 130, 150))
        g.setColorAt(1.0, QColor(255, 226, 130, 0))
        p.setBrush(g)
        p.setPen(Qt.NoPen)
        p.drawEllipse(QPointF(lx, ly), 17, 17)

    # tutamak teli
    p.setPen(QPen(LANTERN_DARK, 1.4, Qt.SolidLine, Qt.RoundCap))
    p.drawLine(QPointF(hand_x, hand_y + 2), QPointF(lx, ly - 8))
    # fener govdesi (cam)
    p.setPen(Qt.NoPen)
    p.setBrush(FLAME if lit else FLAME_OFF)
    p.drawRoundedRect(lx - 5, ly - 7, 10, 12, 3.0, 3.0)
    if lit:
        p.setBrush(FLAME_HOT)
        p.drawEllipse(QPointF(lx, ly - 1), 2.6, 3.4)
    # ust ve alt kapaklar
    p.setBrush(LANTERN_DARK)
    p.drawRoundedRect(lx - 6, ly - 10, 12, 4, 1.5, 1.5)
    p.drawRoundedRect(lx - 6, ly + 4, 12, 4, 1.5, 1.5)

    # --- kafa ---
    head_cy = 17 + bob
    _dot(p, cx, head_cy, 8.5, SKIN)
    # kep
    p.setBrush(HAT)
    p.drawRoundedRect(cx - 9.5, head_cy - 15, 19.0, 6.0, 2.0, 2.0)
    p.drawRoundedRect(cx - 7.0, head_cy - 10.5, 14.0, 4.0, 1.5, 1.5)
    # yuz
    _dot(p, cx - 3.0, head_cy + 0.5, 1.4, SNAKE_EYE)
    _dot(p, cx + 3.0, head_cy + 0.5, 1.4, SNAKE_EYE)
    p.setPen(QPen(SKIN_DARK, 1.2, Qt.SolidLine, Qt.RoundCap))
    p.drawLine(QPointF(cx - 2.0, head_cy + 4.2), QPointF(cx + 2.0, head_cy + 4.2))


# ---------------------------------------------------------------------------
# YILAN
# ---------------------------------------------------------------------------
def _draw_snake(p: QPainter, frame: int):
    ground = SPECIES["snake"][1] - 1
    sway = math.sin(frame / 34.0 * 2 * math.pi) * 2.0
    head_bob = math.sin(frame / 34.0 * 2 * math.pi + 1.0) * 1.2
    flick = (frame % 58) < 16

    hx = 48 + sway
    hy = 24 + head_bob

    # --- govde (kivrimli) ---
    p.setBrush(Qt.NoBrush)
    p.setPen(QPen(SNAKE_DARK, 12.5, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
    body = QPainterPath(QPointF(11, ground - 3))
    body.cubicTo(QPointF(38, ground + 2), QPointF(54, 50), QPointF(34, 44))
    body.cubicTo(QPointF(14, 38), QPointF(26, 26), QPointF(hx - 4, hy + 1))
    p.drawPath(body)

    p.setPen(QPen(SNAKE, 9.0, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
    p.drawPath(body)

    # --- kafa ---
    p.setPen(Qt.NoPen)
    p.setBrush(SNAKE)
    p.drawEllipse(QPointF(hx, hy), 8.6, 6.6)
    p.setBrush(SNAKE_DARK)
    p.drawEllipse(QPointF(hx + 1.5, hy - 1.2), 5.4, 3.9)

    # dil
    if flick:
        p.setPen(QPen(SNAKE_TONGUE, 1.5, Qt.SolidLine, Qt.RoundCap))
        tx = hx + 8.0
        p.drawLine(QPointF(hx + 6.5, hy + 0.5), QPointF(tx, hy + 0.5))
        p.drawLine(QPointF(tx, hy + 0.5), QPointF(tx + 4.0, hy - 2.0))
        p.drawLine(QPointF(tx, hy + 0.5), QPointF(tx + 4.0, hy + 3.0))

    # goz
    _dot(p, hx + 2.2, hy - 2.4, 1.5, FLAME_HOT)
    _dot(p, hx + 2.2, hy - 2.4, 0.9, SNAKE_EYE)


# ---------------------------------------------------------------------------
# BAOBAP AGACI
# ---------------------------------------------------------------------------
def _draw_baobab(p: QPainter, frame: int):
    ground = SPECIES["baobab"][1] - 1
    cx = SPECIES["baobab"][0] / 2.0
    sway = math.sin(frame / 48.0 * 2 * math.pi) * 1.3

    # --- kokler ---
    p.setBrush(Qt.NoBrush)
    for x1, x2, y2 in ((cx - 6, 6, ground - 1), (cx + 6, 54, ground - 1), (cx, cx + 2, ground)):
        _limb(p, cx + (x1 - cx) * 0.4, ground - 8, x2, y2, 5.0, BAOBAB_ROOT)

    # --- govde ---
    p.setPen(Qt.NoPen)
    p.setBrush(BAOBAB_TRUNK)
    trunk = QPainterPath(QPointF(cx - 15, ground - 3))
    trunk.cubicTo(QPointF(cx - 16, 52), QPointF(cx - 8, 44), QPointF(cx - 7, 34))
    trunk.lineTo(QPointF(cx + 7, 34))
    trunk.cubicTo(QPointF(cx + 8, 44), QPointF(cx + 16, 52), QPointF(cx + 15, ground - 3))
    trunk.closeSubpath()
    p.drawPath(trunk)

    # govde dokusu
    p.setBrush(BAOBAB_TRUNK_DARK)
    p.drawEllipse(QPointF(cx - 4, ground - 18), 2.0, 5.5)
    p.drawEllipse(QPointF(cx + 5, ground - 26), 1.8, 4.5)

    # --- dallar ---
    tips = [(-20, -26), (-9, -32), (9, -32), (20, -26)]
    p.setBrush(Qt.NoBrush)
    for dx, dy in tips:
        _limb(
            p,
            cx + dx * 0.25,
            36,
            cx + dx + sway,
            36 + dy,
            4.2,
            BAOBAB_TRUNK,
            mid=(cx + dx * 0.7, 30 + dy * 0.2),
        )

    # --- tac (yapraklar) ---
    p.setPen(Qt.NoPen)
    for i, (dx, dy) in enumerate(tips):
        lx = cx + dx + sway
        ly = 36 + dy
        p.setBrush(BAOBAB_LEAF if i % 2 == 0 else BAOBAB_LEAF_DARK)
        p.drawEllipse(QPointF(lx, ly), 8.0, 6.5)
    p.setBrush(BAOBAB_LEAF)
    p.drawEllipse(QPointF(cx + sway * 0.6, 3), 9.5, 6.0)


# ---------------------------------------------------------------------------
# Yoldas penceresi
# ---------------------------------------------------------------------------
class Companion(QWidget):
    """Kucuk Prens otururken yanina gelen karakter."""

    def __init__(self, species: str, pet, side: int, plat_x1: float, plat_x2: float):
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

        self.species = species
        self.pet = pet
        self.scale = pet.scale
        self.side = side                 # +1: sagdan, -1: soldan gelir
        self.facing = -side
        self.arrive = arrive_mode(species)
        self.vanish = 0.0 if self.arrive == "grow" else 1.0
        self.frame = 0
        self.anim = 0
        self._last_pos: tuple[int, int] | None = None

        self.W, self.H = size_for(species, self.scale)
        self.resize(self.W, self.H)

        if side > 0:
            self.target_x = pet.x + pet.W + 6
        else:
            self.target_x = pet.x - self.W - 6
        self.target_x = max(plat_x1 + 1, min(self.target_x, plat_x2 - self.W - 1))

        self.state = self.arrive
        self.pose = "walk" if self.arrive == "walk" else "idle"
        if self.arrive == "walk":
            start = self.target_x + 150 * side
            if plat_x2 - plat_x1 > self.W:
                self.x = max(plat_x1, min(start, plat_x2 - self.W))
            else:
                self.x = start
        else:
            self.x = self.target_x
        self.y = pet.support_y - self.H

        self.base_support = pet.support_y

        from PySide6.QtCore import QTimer

        self._timer = QTimer(self)
        self._timer.timeout.connect(self.tick)
        self._timer.start(pet.tick_ms)

    # ------------------------------------------------------------------
    def tick(self):
        self.frame += 1
        pet = self.pet

        if self.state == "walk":
            self.facing = -self.side
            if abs(self.x - self.target_x) <= 2.5:
                self.x = self.target_x
                self.state = "sit" if self.species == "fox" else "idle"
                self.pose = "sit" if self.species == "fox" else "idle"
                self.anim = 0
            else:
                self.x += self.facing * pet.walk_speed
            self.y = pet.support_y - self.H

        elif self.state == "grow":
            self.vanish = min(1.0, self.vanish + 0.07)
            if self.vanish >= 1.0:
                self.state = "idle"
            self.y = pet.support_y - self.H

        elif self.state in ("sit", "idle"):
            self.y = pet.support_y - self.H
            if pet.state != "sit" or abs(pet.support_y - self.base_support) > 8:
                self.leave()

        elif self.state == "leave":
            self.vanish -= 0.09
            if self.vanish <= 0.0:
                self._timer.stop()
                self.hide()
                self.deleteLater()
                return

        self.anim += 1
        if self.frame % 15 == 0:
            try:
                platform_api.set_topmost(int(self.winId()), True)
            except Exception:
                pass
        pos = (int(round(self.x)), int(round(self.y)))
        if pos != self._last_pos:
            self.move(*pos)
            self._last_pos = pos
        self.update()

    def leave(self):
        if self.state != "leave":
            self.state = "leave"
            self.anim = 0

    # ------------------------------------------------------------------
    def paintEvent(self, _e):
        pm = self._pixmap()
        p = QPainter(self)
        p.drawPixmap((self.width() - pm.width()) // 2, self.height() - pm.height(), pm)

    def _pixmap(self) -> QPixmap:
        scale = max(0.02, self.scale * self.vanish)
        return render(self.species, self.pose, self.anim, facing=self.facing, scale=scale)
