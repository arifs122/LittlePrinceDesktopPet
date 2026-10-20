"""Kucuk Prens karakterinin cizimi.

Gorsel dosya gerektirmez; karakter tamamen kod ile (vektor) cizilir.
Boylece hazir sprite bulmadan da calisir, sonradan PNG sprite'a gecilebilir.
"""
from __future__ import annotations

import math

from PySide6.QtCore import QPointF, Qt
from PySide6.QtGui import QColor, QPainter, QPainterPath, QPen, QPixmap

# Taban tuval olcusu. Karakterin ayaklari H hizasindadir.
W = 64
H = 72

# Renkler
SKIN = QColor("#F6CDA6")
SKIN_SHADE = QColor("#E2B183")
HAIR = QColor("#F8DE72")
HAIR_SHADE = QColor("#E6C33F")
SUIT = QColor("#43A047")
SUIT_SHADE = QColor("#2E7D32")
SCARF = QColor("#FFC107")
SCARF_SHADE = QColor("#E3A90A")
BOOT = QColor("#7B4B2A")
EYE = QColor("#3E2723")
MOUTH = QColor("#B5653C")

# Her durumun kare sayisi
FRAMES = {
    "walk": 8,
    "idle": 6,
    "sit": 8,
    "sleep": 12,
    "fall": 2,
    "drag": 6,
}

# Karakterin "destek noktasi"nin pencere icindeki y konumu.
# Pencere, destek noktasi platformun uzerine gelecek sekilde konumlanir.
ANCHOR = {
    "walk": H,
    "idle": H,
    "fall": H,
    "drag": H,
    # Oturunca/uyuyunca kalcalar platform kenarinda olur, bacaklar asagi sarkar.
    "sit": 55,
    "sleep": 55,
}


def render(state: str, frame: int, facing: int = 1, scale: float = 1.0) -> QPixmap:
    """Belirli bir durum/kare icin hazir QPixmap dondurur."""
    pw, ph = int(round(W * scale)), int(round(H * scale))
    pm = QPixmap(pw, ph)
    pm.fill(Qt.transparent)

    p = QPainter(pm)
    p.setRenderHint(QPainter.Antialiasing, True)
    p.scale(scale, scale)
    if facing < 0:
        # Saga bakan cizimi aynalayarak sola cevir
        p.translate(W, 0)
        p.scale(-1, 1)

    _draw(p, state, frame)
    p.end()
    return pm


def frame_count(state: str) -> int:
    return FRAMES.get(state, 1)


# --------------------------------------------------------------------------
# Cizim yardimcilari
# --------------------------------------------------------------------------

def _limb(p: QPainter, x0, y0, x1, y1, width, color, mid=None):
    pen = QPen(color, width, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin)
    p.setPen(pen)
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


def _draw(p: QPainter, state: str, frame: int):
    cx = W / 2.0
    walking = state == "walk"
    sitting = state in ("sit", "sleep")
    sleeping = state == "sleep"
    falling = state == "fall"
    dragging = state == "drag"

    # Animasyon fazlari
    bob = 0.0
    swing = 0.0
    kick = 0.0
    if walking:
        t = frame / FRAMES["walk"]
        swing = math.sin(t * 2 * math.pi)
        bob = -abs(math.sin(t * math.pi)) * 1.6
    elif sleeping:
        i = frame % FRAMES["sleep"]
        swing = 0.0
        bob = math.sin(i / FRAMES["sleep"] * 2 * math.pi) * 0.9
    elif sitting:
        i = frame % FRAMES["sit"]
        swing = math.sin(i / FRAMES["sit"] * 2 * math.pi) * 0.4
        bob = 0.0
    elif dragging:
        kick = math.sin(frame / 3.0)
        bob = -1.5
    elif falling:
        bob = -1.5
    else:
        i = frame % FRAMES["idle"]
        bob = math.sin(i / FRAMES["idle"] * 2 * math.pi) * 1.2

    head_y = 21 + bob
    shoulder_y = 34 + bob
    hip_y = 55
    foot_y = H - 1

    # --- Esarp kuyrugu (govdenin arkasinda) ---
    p.setPen(Qt.NoPen)
    p.setBrush(SCARF)
    wave = swing * 4.0 + math.sin(frame / 3.0) * 1.5
    tail = QPainterPath(QPointF(cx - 2, shoulder_y - 5))
    tail.cubicTo(
        QPointF(cx - 14, shoulder_y - 8 + wave),
        QPointF(cx - 24, shoulder_y + 6 - wave),
        QPointF(cx - 15, shoulder_y + 18 + wave),
    )
    tail.cubicTo(
        QPointF(cx - 22, shoulder_y + 8 - wave),
        QPointF(cx - 14, shoulder_y + 2 + wave),
        QPointF(cx - 2, shoulder_y + 2),
    )
    tail.closeSubpath()
    p.drawPath(tail)

    # --- Bacaklar ---
    if sitting:
        # Kenara oturmus: kalcalar kenarda, bacaklar asagi sarkar.
        for side in (-1, 1):
            kx = cx + side * 8.0
            kx += swing * side * 1.5
            hipx = cx + side * 4.0
            _limb(p, hipx, hip_y, kx, hip_y + 6.5, 6.0, SUIT)       # uyluk
            _limb(p, kx, hip_y + 6.0, kx, H - 2, 5.5, SUIT)          # baldur
            _dot(p, kx, H - 2, 3.4, BOOT)
    else:
        for side in (-1, 1):
            if dragging:
                off = kick * 5.0 * side
                lift = max(0.0, kick * side) * 4.0
            else:
                off = swing * 6.0 * side if walking else 0.0
                lift = max(0.0, swing * side) * 3.0 if walking else 0.0
            x0 = cx + side * 4.5
            x1 = cx + side * 4.5 + off
            y1 = foot_y - lift
            _limb(p, x0, hip_y, x1, y1, 5.5, SUIT)
            _dot(p, x1, y1, 3.4, BOOT)

    # --- Govde (yesil tulum) ---
    body = QPainterPath()
    body.moveTo(cx - 9.5, shoulder_y)
    body.lineTo(cx + 9.5, shoulder_y)
    body.lineTo(cx + 11, hip_y + 1)
    body.lineTo(cx - 11, hip_y + 1)
    body.closeSubpath()
    p.setBrush(SUIT)
    p.setPen(QPen(SUIT, 7, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
    p.drawPath(body)
    p.setPen(Qt.NoPen)
    p.drawPath(body)

    # --- Kollar ---
    for side in (-1, 1):
        sx = cx + side * 9.0
        if falling or dragging:
            wobble = kick * 3.0 * side if dragging else 0.0
            hx, hy = cx + side * 15.0, shoulder_y - 5.0 + wobble
            mid = (cx + side * 14.0, shoulder_y + 4.0)
        elif sitting:
            hx, hy = cx + side * 12.0, hip_y + 3.0
            mid = None
        elif walking:
            hx = cx + side * 11.5 - swing * side * 3.0
            hy = hip_y - 2.0 + swing * side * 1.5
            mid = None
        else:
            hx, hy = cx + side * 12.0, hip_y - 2.0
            mid = None
        _limb(p, sx, shoulder_y + 3, hx, hy, 5.0, SUIT, mid=mid)
        _dot(p, hx, hy, 2.8, SKIN)

    # --- Boyun atkisi (bant) ---
    p.setPen(Qt.NoPen)
    p.setBrush(SCARF)
    p.drawRoundedRect(
        QPointF(cx - 10.5, shoulder_y - 3.5).x(),
        QPointF(cx - 10.5, shoulder_y - 3.5).y(),
        21.0, 7.0, 3.2, 3.2,
    )

    # --- Kafa ---
    head_r = 12.0

    # Sac (arka katman + dikenler)
    p.setBrush(HAIR)
    p.setPen(Qt.NoPen)
    p.drawEllipse(QPointF(cx, head_y - 0.5), head_r + 1.6, head_r + 1.6)

    for deg in (148, 120, 92, 64, 36):
        a = math.radians(deg)
        bx = cx + math.cos(a) * head_r
        by = head_y - 0.5 - math.sin(a) * head_r
        tx = cx + math.cos(a) * (head_r + 4.5)
        ty = head_y - 0.5 - math.sin(a) * (head_r + 4.5)
        perp = a + math.pi / 2
        w = 3.2
        tri = QPainterPath(QPointF(bx + math.cos(perp) * w, by - math.sin(perp) * w))
        tri.lineTo(QPointF(bx - math.cos(perp) * w, by + math.sin(perp) * w))
        tri.lineTo(QPointF(tx, ty))
        tri.closeSubpath()
        p.drawPath(tri)

    # Yuz
    p.setBrush(SKIN)
    p.drawEllipse(QPointF(cx, head_y + 1.2), head_r, head_r)

    # Yuz cizgileri
    p.setPen(QPen(EYE, 1.5, Qt.SolidLine, Qt.RoundCap))
    p.setBrush(Qt.NoBrush)
    if sleeping:
        # kapali gozler (kivrik cizgi)
        for side in (-1, 1):
            eye = QPainterPath(QPointF(cx + side * 6.0, head_y + 1.6))
            eye.quadTo(
                QPointF(cx + side * 4.4, head_y + 3.6),
                QPointF(cx + side * 2.8, head_y + 1.6),
            )
            p.drawPath(eye)
    elif state == "sit" and frame % 8 in (4, 5):
        p.drawLine(QPointF(cx - 5.5, head_y + 1.5), QPointF(cx - 3.0, head_y + 1.5))
        p.drawLine(QPointF(cx + 3.0, head_y + 1.5), QPointF(cx + 5.5, head_y + 1.5))
    else:
        p.setPen(Qt.NoPen)
        _dot(p, cx - 4.4, head_y + 1.2, 1.7, EYE)
        _dot(p, cx + 4.4, head_y + 1.2, 1.7, EYE)

    p.setBrush(Qt.NoBrush)
    p.setPen(QPen(MOUTH, 1.3, Qt.SolidLine, Qt.RoundCap))
    if falling or dragging:
        p.setBrush(MOUTH)
        p.setPen(Qt.NoPen)
        p.drawEllipse(QPointF(cx, head_y + 6.2), 2.1, 2.7)
    elif sleeping:
        mouth = QPainterPath(QPointF(cx - 1.8, head_y + 6.0))
        mouth.quadTo(QPointF(cx, head_y + 7.2), QPointF(cx + 1.8, head_y + 6.0))
        p.drawPath(mouth)
    else:
        mouth = QPainterPath(QPointF(cx - 2.6, head_y + 5.4))
        mouth.quadTo(QPointF(cx, head_y + 8.0), QPointF(cx + 2.6, head_y + 5.4))
        p.drawPath(mouth)
