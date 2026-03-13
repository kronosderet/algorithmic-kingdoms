"""
Proof-of-Concept: Fractal UI Elements for Algorithmic Kingdoms
Phase 4 — The Fractal Interface

Demonstrates:
  1. Fractal Typography (L-System Rune glyphs)
  2. Koch Border Panels
  3. Polar Rose Bloom Buttons
  4. Fibonacci Resource Display
  5. Spirograph HP / Progress Bars

Controls:
  Mouse hover  — button bloom effects
  Click        — visual press feedback
  1/2/3        — change displayed unit type
  UP/DOWN      — adjust HP bar value
  LEFT/RIGHT   — adjust resource amounts
  T            — cycle text/font size demos
  ESC          — quit
"""

import math
import sys
import time

import pygame

# ---------------------------------------------------------------------------
# Palette
# ---------------------------------------------------------------------------
COL_BG = (20, 20, 30)
COL_GUI_BG = (30, 30, 45)
COL_GUI_BORDER = (80, 80, 100)
COL_GOLD = (218, 165, 32)
COL_BRIGHT_GOLD = (240, 220, 110)
COL_DIM_GOLD = (200, 185, 80)
COL_DISABLED_GOLD = (80, 75, 60)
GLOW_WHITE = (240, 235, 220)
HP_GREEN = (0, 200, 0)
HP_YELLOW = (220, 200, 0)
HP_RED = (200, 40, 40)
COL_BUILD_BLUE = (0, 180, 255)
COL_STONE = (160, 160, 170)
COL_IRON = (120, 180, 220)
COL_WOOD = (100, 180, 60)

SCREEN_W, SCREEN_H = 1280, 720

# ---------------------------------------------------------------------------
# Fractal Glyph Definitions  (normalized 0..1 coords in char cell)
# ---------------------------------------------------------------------------
FRACTAL_GLYPHS: dict[str, list[list[tuple[float, float]]]] = {
    # Uppercase
    "A": [[(0.1, 1), (0.5, 0), (0.9, 1)], [(0.25, 0.6), (0.75, 0.6)]],
    "B": [
        [(0.15, 0), (0.15, 1)],
        [(0.15, 0), (0.7, 0), (0.8, 0.12), (0.8, 0.38), (0.7, 0.5), (0.15, 0.5)],
        [(0.15, 0.5), (0.75, 0.5), (0.85, 0.62), (0.85, 0.88), (0.75, 1), (0.15, 1)],
    ],
    "C": [[(0.85, 0.15), (0.6, 0), (0.3, 0), (0.15, 0.15), (0.15, 0.85), (0.3, 1), (0.6, 1), (0.85, 0.85)]],
    "D": [[(0.15, 0), (0.15, 1)], [(0.15, 0), (0.6, 0), (0.85, 0.2), (0.85, 0.8), (0.6, 1), (0.15, 1)]],
    "E": [[(0.8, 0), (0.15, 0), (0.15, 1), (0.8, 1)], [(0.15, 0.5), (0.65, 0.5)]],
    "F": [[(0.8, 0), (0.15, 0), (0.15, 1)], [(0.15, 0.5), (0.65, 0.5)]],
    "G": [[(0.85, 0.15), (0.6, 0), (0.3, 0), (0.15, 0.15), (0.15, 0.85), (0.3, 1), (0.6, 1), (0.85, 0.85), (0.85, 0.5), (0.55, 0.5)]],
    "H": [[(0.15, 0), (0.15, 1)], [(0.85, 0), (0.85, 1)], [(0.15, 0.5), (0.85, 0.5)]],
    "I": [[(0.3, 0), (0.7, 0)], [(0.5, 0), (0.5, 1)], [(0.3, 1), (0.7, 1)]],
    "J": [[(0.35, 0), (0.75, 0)], [(0.6, 0), (0.6, 0.85), (0.45, 1), (0.25, 0.9)]],
    "K": [[(0.15, 0), (0.15, 1)], [(0.85, 0), (0.15, 0.5)], [(0.15, 0.5), (0.85, 1)]],
    "L": [[(0.15, 0), (0.15, 1), (0.8, 1)]],
    "M": [[(0.1, 1), (0.1, 0), (0.5, 0.45), (0.9, 0), (0.9, 1)]],
    "N": [[(0.15, 1), (0.15, 0), (0.85, 1), (0.85, 0)]],
    "O": [[(0.5, 0), (0.2, 0.15), (0.15, 0.5), (0.2, 0.85), (0.5, 1), (0.8, 0.85), (0.85, 0.5), (0.8, 0.15), (0.5, 0)]],
    "P": [[(0.15, 1), (0.15, 0), (0.7, 0), (0.85, 0.12), (0.85, 0.38), (0.7, 0.5), (0.15, 0.5)]],
    "Q": [[(0.5, 0), (0.2, 0.15), (0.15, 0.5), (0.2, 0.85), (0.5, 1), (0.8, 0.85), (0.85, 0.5), (0.8, 0.15), (0.5, 0)], [(0.6, 0.75), (0.9, 1.05)]],
    "R": [[(0.15, 1), (0.15, 0), (0.7, 0), (0.85, 0.12), (0.85, 0.38), (0.7, 0.5), (0.15, 0.5)], [(0.55, 0.5), (0.85, 1)]],
    "S": [[(0.8, 0.1), (0.6, 0), (0.3, 0), (0.15, 0.12), (0.15, 0.38), (0.3, 0.5), (0.7, 0.5), (0.85, 0.62), (0.85, 0.88), (0.7, 1), (0.3, 1), (0.15, 0.9)]],
    "T": [[(0.1, 0), (0.9, 0)], [(0.5, 0), (0.5, 1)]],
    "U": [[(0.15, 0), (0.15, 0.85), (0.3, 1), (0.7, 1), (0.85, 0.85), (0.85, 0)]],
    "V": [[(0.1, 0), (0.5, 1), (0.9, 0)]],
    "W": [[(0.05, 0), (0.25, 1), (0.5, 0.5), (0.75, 1), (0.95, 0)]],
    "X": [[(0.1, 0), (0.9, 1)], [(0.9, 0), (0.1, 1)]],
    "Y": [[(0.1, 0), (0.5, 0.45)], [(0.9, 0), (0.5, 0.45)], [(0.5, 0.45), (0.5, 1)]],
    "Z": [[(0.1, 0), (0.9, 0), (0.1, 1), (0.9, 1)]],
    # Digits
    "0": [[(0.5, 0), (0.2, 0.15), (0.15, 0.5), (0.2, 0.85), (0.5, 1), (0.8, 0.85), (0.85, 0.5), (0.8, 0.15), (0.5, 0)], [(0.3, 0.85), (0.7, 0.15)]],
    "1": [[(0.3, 0.15), (0.5, 0), (0.5, 1)], [(0.3, 1), (0.7, 1)]],
    "2": [[(0.15, 0.15), (0.3, 0), (0.7, 0), (0.85, 0.15), (0.85, 0.4), (0.15, 1), (0.85, 1)]],
    "3": [[(0.15, 0.1), (0.35, 0), (0.7, 0), (0.85, 0.12), (0.85, 0.38), (0.7, 0.5), (0.5, 0.5)], [(0.7, 0.5), (0.85, 0.62), (0.85, 0.88), (0.7, 1), (0.35, 1), (0.15, 0.9)]],
    "4": [[(0.7, 1), (0.7, 0), (0.1, 0.65), (0.9, 0.65)]],
    "5": [[(0.8, 0), (0.15, 0), (0.15, 0.45), (0.7, 0.45), (0.85, 0.58), (0.85, 0.88), (0.7, 1), (0.3, 1), (0.15, 0.9)]],
    "6": [[(0.7, 0), (0.35, 0), (0.15, 0.2), (0.15, 0.85), (0.3, 1), (0.7, 1), (0.85, 0.85), (0.85, 0.55), (0.7, 0.45), (0.15, 0.45)]],
    "7": [[(0.1, 0), (0.9, 0), (0.4, 1)]],
    "8": [[(0.5, 0), (0.25, 0), (0.15, 0.12), (0.15, 0.38), (0.25, 0.5), (0.75, 0.5), (0.85, 0.62), (0.85, 0.88), (0.75, 1), (0.25, 1), (0.15, 0.88), (0.15, 0.62), (0.25, 0.5), (0.75, 0.5), (0.85, 0.38), (0.85, 0.12), (0.75, 0), (0.5, 0)]],
    "9": [[(0.15, 1), (0.65, 1), (0.85, 0.8), (0.85, 0.15), (0.7, 0), (0.3, 0), (0.15, 0.15), (0.15, 0.45), (0.3, 0.55), (0.85, 0.55)]],
    # Punctuation
    ".": [[(0.45, 0.9), (0.55, 0.9), (0.55, 1), (0.45, 1), (0.45, 0.9)]],
    ",": [[(0.5, 0.85), (0.5, 1), (0.35, 1.1)]],
    ":": [[(0.45, 0.25), (0.55, 0.25), (0.55, 0.35), (0.45, 0.35), (0.45, 0.25)], [(0.45, 0.75), (0.55, 0.75), (0.55, 0.85), (0.45, 0.85), (0.45, 0.75)]],
    "-": [[(0.2, 0.5), (0.8, 0.5)]],
    "+": [[(0.2, 0.5), (0.8, 0.5)], [(0.5, 0.25), (0.5, 0.75)]],
    "/": [[(0.2, 1), (0.8, 0)]],
    "(": [[(0.6, 0), (0.35, 0.25), (0.3, 0.5), (0.35, 0.75), (0.6, 1)]],
    ")": [[(0.4, 0), (0.65, 0.25), (0.7, 0.5), (0.65, 0.75), (0.4, 1)]],
    "!": [[(0.5, 0), (0.5, 0.7)], [(0.45, 0.88), (0.55, 0.88), (0.55, 0.98), (0.45, 0.98), (0.45, 0.88)]],
    "?": [[(0.2, 0.15), (0.35, 0), (0.65, 0), (0.8, 0.15), (0.8, 0.35), (0.5, 0.55), (0.5, 0.7)], [(0.45, 0.88), (0.55, 0.88), (0.55, 0.98), (0.45, 0.98), (0.45, 0.88)]],
    "%": [[(0.2, 0.1), (0.3, 0.1), (0.3, 0.25), (0.2, 0.25), (0.2, 0.1)], [(0.8, 0), (0.2, 1)], [(0.7, 0.75), (0.8, 0.75), (0.8, 0.9), (0.7, 0.9), (0.7, 0.75)]],
    "'": [[(0.5, 0), (0.45, 0.15)]],
    " ": [],
}


# ---------------------------------------------------------------------------
# Serif helper
# ---------------------------------------------------------------------------
def _draw_serif(surf, x, y, angle, length, depth, color):
    if depth <= 0 or length < 1:
        return
    ex = x + math.cos(angle) * length
    ey = y + math.sin(angle) * length
    pygame.draw.line(surf, color, (int(x), int(y)), (int(ex), int(ey)), 1)
    _draw_serif(surf, ex, ey, angle + 0.6, length * 0.5, depth - 1, color)
    _draw_serif(surf, ex, ey, angle - 0.6, length * 0.5, depth - 1, color)


# ---------------------------------------------------------------------------
# FractalFont
# ---------------------------------------------------------------------------
class FractalFont:
    def __init__(self, size: int, color=(230, 205, 90)):
        self.size = size
        self.char_w = int(size * 0.6)
        self.char_h = size
        self.color = color
        self.glow_color = tuple(max(0, c - 80) for c in color)
        self.serif_depth = 0 if size < 24 else (1 if size < 36 else 2)
        self._cache: dict[tuple, pygame.Surface] = {}

    def render_text(self, surf, text: str, x: int, y: int, center=False):
        total_w = len(text) * self.char_w
        if center:
            x -= total_w // 2
        for ch in text:
            self._render_glyph(surf, ch, x, y)
            x += self.char_w
        return total_w

    def text_width(self, text: str) -> int:
        return len(text) * self.char_w

    def _render_glyph(self, surf, ch: str, x: int, y: int):
        if ch == " ":
            return
        key = (ch, self.size, self.color)
        if key not in self._cache:
            self._cache[key] = self._build_glyph_surface(ch)
        surf.blit(self._cache[key], (x, y))

    def _build_glyph_surface(self, ch: str) -> pygame.Surface:
        s = pygame.Surface((self.char_w + 4, self.char_h + 4), pygame.SRCALPHA)
        strokes = FRACTAL_GLYPHS.get(ch.upper(), FRACTAL_GLYPHS.get(ch, None))
        if not strokes:
            return s
        ox, oy = 2, 2
        glow_w = max(2, self.size // 10 + 1)
        core_w = max(1, self.size // 14)
        for polyline in strokes:
            pts = [(int(p[0] * self.char_w + ox), int(p[1] * self.char_h + oy)) for p in polyline]
            if len(pts) >= 2:
                pygame.draw.lines(s, (*self.glow_color, 100), False, pts, glow_w)
        for polyline in strokes:
            pts = [(int(p[0] * self.char_w + ox), int(p[1] * self.char_h + oy)) for p in polyline]
            if len(pts) >= 2:
                pygame.draw.lines(s, (*self.color, 255), False, pts, core_w)
        if self.serif_depth > 0:
            for polyline in strokes:
                for p in [polyline[0], polyline[-1]]:
                    px = int(p[0] * self.char_w + ox)
                    py = int(p[1] * self.char_h + oy)
                    _draw_serif(s, px, py, -math.pi / 4, self.size * 0.08, self.serif_depth, (*self.color, 200))
        return s


# ---------------------------------------------------------------------------
# Koch Curve helpers
# ---------------------------------------------------------------------------
def _koch_subdivide(p1, p2, depth):
    if depth <= 0:
        return [p1, p2]
    dx = p2[0] - p1[0]
    dy = p2[1] - p1[1]
    a = (p1[0] + dx / 3, p1[1] + dy / 3)
    b = (p1[0] + 2 * dx / 3, p1[1] + 2 * dy / 3)
    # peak point
    px = (p1[0] + p2[0]) / 2 + (dy) * 0.2887  # sqrt(3)/6 ~ 0.2887
    py = (p1[1] + p2[1]) / 2 - (dx) * 0.2887
    peak = (px, py)
    pts = []
    for seg in [
        _koch_subdivide(p1, a, depth - 1),
        _koch_subdivide(a, peak, depth - 1),
        _koch_subdivide(peak, b, depth - 1),
        _koch_subdivide(b, p2, depth - 1),
    ]:
        if pts and seg:
            pts.extend(seg[1:])
        else:
            pts.extend(seg)
    return pts


def koch_border(surf, rect, depth, color, line_width=1):
    x, y, w, h = rect
    corners = [(x, y), (x + w, y), (x + w, y + h), (x, y + h)]
    for i in range(4):
        p1 = corners[i]
        p2 = corners[(i + 1) % 4]
        points = _koch_subdivide(p1, p2, depth)
        ipts = [(int(round(px)), int(round(py))) for (px, py) in points]
        if len(ipts) >= 2:
            pygame.draw.lines(surf, color, False, ipts, line_width)


def koch_panel(surf, rect, depth, border_color, bg_alpha=180):
    x, y, w, h = rect
    bg = pygame.Surface((w, h), pygame.SRCALPHA)
    # radial-ish gradient fill
    cx, cy = w // 2, h // 2
    for r in range(max(cx, cy), 0, -2):
        t = r / max(cx, cy, 1)
        c = (
            int(35 * (1 - t) + 20 * t),
            int(32 * (1 - t) + 18 * t),
            int(50 * (1 - t) + 30 * t),
            bg_alpha,
        )
        pygame.draw.circle(bg, c, (cx, cy), r)
    surf.blit(bg, (x, y))
    koch_border(surf, rect, depth, border_color, 2)


# ---------------------------------------------------------------------------
# Polar Rose drawing
# ---------------------------------------------------------------------------
def draw_polar_rose(surf, cx, cy, radius, k, n_pts, color, rotation=0.0, width=1):
    pts = []
    for i in range(n_pts):
        theta = rotation + 2 * math.pi * i / n_pts
        rv = radius * abs(math.cos(k * theta))
        rv = max(rv, radius * 0.15)
        pts.append((int(cx + rv * math.cos(theta)), int(cy + rv * math.sin(theta))))
    if len(pts) >= 3:
        pygame.draw.lines(surf, color, True, pts, width)


# ---------------------------------------------------------------------------
# Spirograph / sine-wave HP bar
# ---------------------------------------------------------------------------
def draw_fractal_bar(surf, x, y, w, h, ratio, color, t_time):
    bg_color = (25, 22, 35)
    pygame.draw.rect(surf, bg_color, (x, y, w, h))
    fill_w = int(w * max(0, min(1, ratio)))
    if fill_w < 1:
        koch_border(surf, (x, y, w, h), 1, (50, 48, 60), 1)
        return
    bar_surf = pygame.Surface((fill_w, h), pygame.SRCALPHA)
    for px in range(fill_w):
        wave = math.sin(px * 0.25 + t_time * 2.0) * (h * 0.15)
        for py_off in range(h):
            py_center = h / 2
            dist = abs(py_off - py_center + wave)
            if dist < h / 2:
                bri = 1.0 - (dist / (h / 2)) * 0.5
                c = (
                    int(color[0] * bri),
                    int(color[1] * bri),
                    int(color[2] * bri),
                    220,
                )
                bar_surf.set_at((px, py_off), c)
    surf.blit(bar_surf, (x, y))
    koch_border(surf, (x, y, w, h), 1, (80, 75, 60), 1)


# ---------------------------------------------------------------------------
# Build progress bar (gear-tooth style)
# ---------------------------------------------------------------------------
def draw_build_bar(surf, x, y, w, h, ratio, t_time):
    bg_color = (25, 22, 35)
    pygame.draw.rect(surf, bg_color, (x, y, w, h))
    fill_w = int(w * max(0, min(1, ratio)))
    if fill_w < 1:
        return
    freq = 0.4 + ratio * 0.4
    bar_surf = pygame.Surface((fill_w, h), pygame.SRCALPHA)
    for px in range(fill_w):
        wave = math.sin(px * freq + t_time * 3.0) * (h * 0.2)
        for py_off in range(h):
            py_center = h / 2
            dist = abs(py_off - py_center + wave)
            if dist < h / 2:
                bri = 0.7 + 0.3 * (1.0 - dist / (h / 2))
                c = (0, int(180 * bri), int(255 * bri), 200)
                bar_surf.set_at((px, py_off), c)
    surf.blit(bar_surf, (x, y))
    koch_border(surf, (x, y, w, h), 1, (60, 80, 100), 1)


# ---------------------------------------------------------------------------
# Resource icon shapes
# ---------------------------------------------------------------------------
def draw_gold_spiral(surf, cx, cy, size, t_time):
    """Golden spiral icon for gold resource."""
    pts = []
    for i in range(40):
        theta = i * 0.3 + t_time * 0.5
        r = size * 0.1 * math.exp(0.08 * theta) * 0.3
        if r > size * 0.5:
            break
        pts.append((int(cx + r * math.cos(theta)), int(cy + r * math.sin(theta))))
    if len(pts) >= 2:
        pygame.draw.lines(surf, COL_GOLD, False, pts, 2)


def draw_hex_icon(surf, cx, cy, size, color):
    """Hexagon icon for stone."""
    pts = []
    for i in range(6):
        theta = math.pi / 6 + i * math.pi / 3
        pts.append((int(cx + size * 0.4 * math.cos(theta)), int(cy + size * 0.4 * math.sin(theta))))
    pygame.draw.polygon(surf, color, pts, 2)


def draw_crystal_icon(surf, cx, cy, size, color):
    """Crystal / diamond icon for iron."""
    s2 = size * 0.4
    pts = [(cx, cy - s2), (cx + s2 * 0.6, cy), (cx, cy + s2), (cx - s2 * 0.6, cy)]
    pts_i = [(int(p[0]), int(p[1])) for p in pts]
    pygame.draw.polygon(surf, color, pts_i, 2)
    pygame.draw.line(surf, color, pts_i[0], pts_i[2], 1)


def draw_tree_icon(surf, cx, cy, size, color):
    """Simple tree icon for wood."""
    s = size * 0.35
    pygame.draw.line(surf, color, (int(cx), int(cy + s)), (int(cx), int(cy - s * 0.3)), 2)
    for angle_off in [-0.4, 0, 0.4]:
        a = -math.pi / 2 + angle_off
        pygame.draw.line(
            surf, color,
            (int(cx), int(cy - s * 0.1)),
            (int(cx + math.cos(a) * s * 0.7), int(cy - s * 0.1 + math.sin(a) * s * 0.7)),
            2,
        )


# ---------------------------------------------------------------------------
# Button class
# ---------------------------------------------------------------------------
class FractalButton:
    def __init__(self, x, y, w, h, label, enabled=True):
        self.rect = pygame.Rect(x, y, w, h)
        self.label = label
        self.enabled = enabled
        self.state = "idle"  # idle, hover, pressed
        self.hover_t = 0.0
        self.press_t = 0.0

    def update(self, mx, my, pressed, dt):
        inside = self.rect.collidepoint(mx, my)
        if not self.enabled:
            self.state = "disabled"
            self.hover_t = max(0, self.hover_t - dt * 4)
            return False
        clicked = False
        if inside:
            if pressed:
                self.state = "pressed"
                self.press_t = 0.3
                clicked = True
            else:
                self.state = "hover"
            self.hover_t = min(1.0, self.hover_t + dt * 4)
        else:
            self.state = "idle"
            self.hover_t = max(0, self.hover_t - dt * 4)
        self.press_t = max(0, self.press_t - dt * 3)
        return clicked

    def draw(self, surf, font_sm, t_time):
        r = self.rect
        if self.state == "disabled":
            pygame.draw.rect(surf, (28, 26, 35), r)
            pygame.draw.rect(surf, (40, 38, 45), r, 1)
            f = FractalFont(font_sm.size, COL_DISABLED_GOLD)
            tw = f.text_width(self.label)
            f.render_text(surf, self.label, r.centerx - tw // 2, r.y + (r.h - f.char_h) // 2)
            return

        # background gradient via lerp
        ht = self.hover_t
        center_c = (int(40 + 10 * ht), int(38 + 7 * ht), int(55 + 10 * ht))
        edge_c = (int(25 + 5 * ht), int(22 + 6 * ht), int(35 + 7 * ht))
        if self.press_t > 0:
            center_c = tuple(max(0, c - 10) for c in center_c)
            edge_c = tuple(max(0, c - 7) for c in edge_c)

        # simple rect bg
        pygame.draw.rect(surf, center_c, r)

        # Koch border
        depth = 2 if ht > 0.5 else 1
        bcolor_base = (60, 55, 45)
        bcolor = tuple(int(b + (120 - b) * ht) for b in bcolor_base)
        koch_border(surf, (r.x, r.y, r.w, r.h), depth, bcolor, 2)

        # polar rose corners on hover
        if ht > 0.2:
            rose_alpha = int(255 * min(1, ht))
            rose_r = 6 + 4 * ht
            rot = t_time * 0.8
            for cx, cy in [(r.x + 8, r.y + 8), (r.right - 8, r.y + 8),
                           (r.x + 8, r.bottom - 8), (r.right - 8, r.bottom - 8)]:
                rose_surf = pygame.Surface((int(rose_r * 2 + 4), int(rose_r * 2 + 4)), pygame.SRCALPHA)
                draw_polar_rose(rose_surf, int(rose_r + 2), int(rose_r + 2), rose_r, 3, 48,
                                (*COL_BRIGHT_GOLD, rose_alpha), rot, 1)
                surf.blit(rose_surf, (int(cx - rose_r - 2), int(cy - rose_r - 2)))

        # text
        text_color = COL_BRIGHT_GOLD if ht > 0.5 else COL_DIM_GOLD
        f = FractalFont(font_sm.size, text_color)
        tw = f.text_width(self.label)
        ty = r.y + (r.h - f.char_h) // 2
        tx = r.centerx - tw // 2
        if self.press_t > 0:
            ty += 1
        f.render_text(surf, self.label, tx, ty)


# ---------------------------------------------------------------------------
# Main application
# ---------------------------------------------------------------------------
def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
    pygame.display.set_caption("Fractal UI PoC — Algorithmic Kingdoms Phase 4")
    clock = pygame.time.Clock()

    # fonts
    font_title = FractalFont(40, COL_GOLD)
    font_panel = FractalFont(28, COL_GOLD)
    font_body = FractalFont(20, GLOW_WHITE)
    font_small = FractalFont(16, COL_DIM_GOLD)
    font_hp_label = FractalFont(14, GLOW_WHITE)

    # state
    hp_ratio = 0.75
    build_ratio = 0.4
    resources = {"GOLD": 350, "STONE": 120, "IRON": 45, "WOOD": 210}
    unit_types = ["SOLDIER", "ARCHER", "WORKER"]
    unit_idx = 0
    unit_stats = {
        "SOLDIER": {"hp": 100, "atk": 12, "def": 8, "spd": 2},
        "ARCHER": {"hp": 60, "atk": 18, "def": 3, "spd": 3},
        "WORKER": {"hp": 40, "atk": 2, "def": 2, "spd": 4},
    }
    text_demo_mode = 0
    text_demos = [
        ("FRACTAL RUNE SCRIPT", font_title),
        ("Panel Labels 28px", font_panel),
        ("Body text at 20px - stats!", font_body),
        ("tiny hud labels 16px", font_small),
    ]

    # buttons
    btn_w, btn_h = 120, 44
    btn_y = SCREEN_H - 180
    buttons = [
        FractalButton(SCREEN_W // 2 - 200, btn_y, btn_w, btn_h, "BUILD"),
        FractalButton(SCREEN_W // 2 - 65, btn_y, btn_w, btn_h, "TRAIN"),
        FractalButton(SCREEN_W // 2 + 70, btn_y, btn_w, btn_h, "RALLY"),
        FractalButton(SCREEN_W // 2 + 205, btn_y, btn_w, btn_h, "CANCEL", enabled=False),
    ]

    running = True
    start_time = time.time()
    mouse_clicked = False

    while running:
        dt = clock.tick(60) / 1000.0
        t_time = time.time() - start_time
        mx, my = pygame.mouse.get_pos()
        mouse_clicked = False

        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                running = False
            elif ev.type == pygame.KEYDOWN:
                if ev.key == pygame.K_ESCAPE:
                    running = False
                elif ev.key == pygame.K_1:
                    unit_idx = 0
                elif ev.key == pygame.K_2:
                    unit_idx = 1
                elif ev.key == pygame.K_3:
                    unit_idx = 2
                elif ev.key == pygame.K_UP:
                    hp_ratio = min(1.0, hp_ratio + 0.05)
                elif ev.key == pygame.K_DOWN:
                    hp_ratio = max(0.0, hp_ratio - 0.05)
                elif ev.key == pygame.K_RIGHT:
                    for k in resources:
                        resources[k] = min(9999, resources[k] + 25)
                    build_ratio = min(1.0, build_ratio + 0.1)
                elif ev.key == pygame.K_LEFT:
                    for k in resources:
                        resources[k] = max(0, resources[k] - 25)
                    build_ratio = max(0.0, build_ratio - 0.1)
                elif ev.key == pygame.K_t:
                    text_demo_mode = (text_demo_mode + 1) % len(text_demos)
            elif ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
                mouse_clicked = True

        # update buttons
        for btn in buttons:
            btn.update(mx, my, mouse_clicked, dt)

        # ---- RENDER ----
        screen.fill(COL_BG)

        # === TOP RESOURCE BAR ===
        bar_rect = (10, 8, SCREEN_W - 20, 48)
        koch_panel(screen, bar_rect, 1, (80, 75, 55), 200)

        res_items = [
            ("GOLD", resources["GOLD"], COL_GOLD, draw_gold_spiral),
            ("STONE", resources["STONE"], COL_STONE, lambda s, cx, cy, sz, t: draw_hex_icon(s, cx, cy, sz, COL_STONE)),
            ("IRON", resources["IRON"], COL_IRON, lambda s, cx, cy, sz, t: draw_crystal_icon(s, cx, cy, sz, COL_IRON)),
            ("WOOD", resources["WOOD"], COL_WOOD, lambda s, cx, cy, sz, t: draw_tree_icon(s, cx, cy, sz, COL_WOOD)),
        ]
        rx = 40
        for name, val, color, icon_fn in res_items:
            # icon with breathing scale
            scale = 1.0 + 0.03 * math.sin(t_time * 1.5 + hash(name))
            icon_fn(screen, rx, 32, int(20 * scale), t_time)
            # number
            f_res = FractalFont(20, color)
            f_res.render_text(screen, str(val), rx + 18, 22)
            rx += 160

        # === TEXT DEMO AREA ===
        demo_text, demo_font = text_demos[text_demo_mode]
        ty = 80
        demo_font.render_text(screen, demo_text, 40, ty)
        hint_f = FractalFont(14, (100, 95, 80))
        hint_f.render_text(screen, "PRESS T TO CYCLE FONTS", 40, ty + demo_font.char_h + 8)

        # === COLOR VARIANT SAMPLES ===
        cy_base = 170
        samples = [
            ("GOLD TITLE", COL_GOLD),
            ("WHITE BODY", GLOW_WHITE),
            ("GREEN +50", HP_GREEN),
            ("RED -25", HP_RED),
            ("DISABLED", COL_DISABLED_GOLD),
        ]
        sx = 40
        for label, col in samples:
            f = FractalFont(18, col)
            f.render_text(screen, label, sx, cy_base)
            sx += f.text_width(label) + 20

        # === BOTTOM PANEL (unit info) ===
        panel_rect = (60, SCREEN_H - 260, 500, 230)
        panel_depth_f = 1.0 + 0.5 * math.sin(t_time * 0.3)
        panel_depth = int(panel_depth_f + 0.5)
        koch_panel(screen, panel_rect, panel_depth, COL_GUI_BORDER, 200)

        uname = unit_types[unit_idx]
        stats = unit_stats[uname]
        font_panel.render_text(screen, uname, panel_rect[0] + 20, panel_rect[1] + 12)

        # unit rose icon in panel
        rose_cx = panel_rect[0] + panel_rect[2] - 60
        rose_cy = panel_rect[1] + 55
        k_vals = {"SOLDIER": 2.5, "ARCHER": 3, "WORKER": 4}
        draw_polar_rose(screen, rose_cx, rose_cy, 30, k_vals[uname], 80,
                        COL_GOLD, t_time * 0.5, 2)

        # stats
        stat_y = panel_rect[1] + 50
        for label, val in stats.items():
            text = f"{label.upper()}: {val}"
            font_body.render_text(screen, text, panel_rect[0] + 20, stat_y)
            stat_y += 28

        # HP bar
        hp_y = panel_rect[1] + 170
        font_hp_label.render_text(screen, "HP", panel_rect[0] + 20, hp_y + 1)
        hp_color = HP_GREEN
        if hp_ratio < 0.3:
            hp_color = HP_RED
        elif hp_ratio < 0.6:
            hp_color = HP_YELLOW
        draw_fractal_bar(screen, panel_rect[0] + 55, hp_y, 200, 16, hp_ratio, hp_color, t_time)
        hp_text = f"{int(hp_ratio * stats['hp'])}/{stats['hp']}"
        font_hp_label.render_text(screen, hp_text, panel_rect[0] + 265, hp_y + 1)

        # Build progress bar
        bp_y = hp_y + 26
        font_hp_label.render_text(screen, "BLD", panel_rect[0] + 14, bp_y + 1)
        draw_build_bar(screen, panel_rect[0] + 55, bp_y, 200, 16, build_ratio, t_time)
        pct_text = f"{int(build_ratio * 100)}%"
        font_hp_label.render_text(screen, pct_text, panel_rect[0] + 265, bp_y + 1)

        # === BUTTONS ===
        for btn in buttons:
            btn.draw(screen, font_small, t_time)

        # === RIGHT PANEL — HP bar demo at different ratios ===
        rp_rect = (620, SCREEN_H - 260, 340, 230)
        koch_panel(screen, rp_rect, 1, (70, 70, 90), 190)
        font_panel.render_text(screen, "BAR DEMOS", rp_rect[0] + 16, rp_rect[1] + 10)
        demo_ratios = [1.0, 0.75, 0.5, 0.25, 0.1]
        by = rp_rect[1] + 48
        for dr in demo_ratios:
            c = HP_GREEN if dr > 0.6 else (HP_YELLOW if dr > 0.3 else HP_RED)
            draw_fractal_bar(screen, rp_rect[0] + 20, by, 200, 12, dr, c, t_time)
            pct = f"{int(dr * 100)}%"
            font_hp_label.render_text(screen, pct, rp_rect[0] + 230, by - 1)
            by += 24
        # build bar demo
        by += 10
        font_small.render_text(screen, "BUILD", rp_rect[0] + 20, by)
        draw_build_bar(screen, rp_rect[0] + 20, by + 22, 200, 14, build_ratio, t_time)

        # === CONTROLS HINT ===
        hint_y = SCREEN_H - 22
        hint_f2 = FractalFont(13, (90, 85, 70))
        hint_f2.render_text(screen, "1/2/3:UNIT  UP/DN:HP  L/R:RES  T:FONT  ESC:QUIT", 10, hint_y)

        pygame.display.flip()

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
