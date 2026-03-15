"""
Proof-of-concept: Mock Game Window — The Fractal Interface Vision (Post-Sentinel Merge).

Renders a complete mock game screenshot showing the updated VDD GUI:
  - Koch-bordered panels (top bar, bottom info, minimap)
  - Fractal typography (L-system rune glyphs)
  - Resource icons (Fibonacci spiral, binary tree, octahedron, etc.)
  - Spirograph HP bars
  - Polar rose selection rings
  - Sentinels with Koch resonance fields + lattice amplification
  - Resonance defense in action (enemies bleaching inside field)
  - Harmonic Pulse expanding rings
  - Incident alert banner
  - Tension meter with pulse animation
  - Minimap with Koch border

Controls:
  1-7    Select different unit tones to see selection panel
  F      Toggle formation overlay
  D      Toggle depth layer (0-6)
  SPACE  Trigger harmonic pulse animation
  E      Toggle enemy wave active
  ESC    Quit
"""
import pygame
import math
import random
import sys

# --- Chromatic Heptarchy Palette ---
COL_BG = (20, 20, 30)
COL_GUI_BG = (30, 30, 45)
COL_GUI_BORDER = (80, 80, 100)
EARTH_GOLD = (218, 165, 32)
BOUNDARY_WHITE = (240, 235, 220)
GHOST_STONE = (80, 75, 60)
FRACTAL_DEEP = (10, 8, 25)
RESONANCE_GLOW = (180, 160, 255)
SENTINEL_STONE = (140, 130, 100)

TONE_COLORS = {
    "gatherer": (50, 130, 220), "soldier": (200, 60, 60),
    "archer": (140, 100, 200), "shield": (160, 150, 130),
    "knight": (218, 165, 32), "healer": (46, 139, 87),
    "sage": (100, 50, 150),
}
TONE_ACCENTS = {
    "gatherer": (80, 180, 255), "soldier": (255, 100, 80),
    "archer": (180, 130, 255), "shield": (200, 190, 170),
    "knight": (255, 200, 60), "healer": (80, 200, 120),
    "sage": (150, 80, 220),
}

# UI display names for code identifiers
TONE_DISPLAY = {
    "gatherer": "Harvester", "soldier": "Warden", "archer": "Ranger",
    "shield": "Bulwark", "knight": "Vanguard", "healer": "Mender",
    "sage": "Resonant",
}

# Resource colors (VDD Section 9.5)
RES_GOLD_COLOR = EARTH_GOLD
RES_WOOD_COLOR = (100, 180, 60)
RES_IRON_COLOR = (120, 180, 220)
RES_STONE_COLOR = (160, 160, 170)

W, H = 1280, 720
TERRAIN_GREEN = (38, 110, 72)


# --- Koch curve geometry ---
def _koch_curve_pts(x1, y1, x2, y2, depth):
    if depth == 0:
        return [(x1, y1)]
    dx, dy = x2 - x1, y2 - y1
    ax, ay = x1 + dx / 3, y1 + dy / 3
    bx, by = x1 + 2 * dx / 3, y1 + 2 * dy / 3
    px = (ax + bx) / 2 + math.sqrt(3) / 6 * (y1 - y2)
    py = (ay + by) / 2 + math.sqrt(3) / 6 * (x2 - x1)
    pts = []
    pts.extend(_koch_curve_pts(x1, y1, ax, ay, depth - 1))
    pts.extend(_koch_curve_pts(ax, ay, px, py, depth - 1))
    pts.extend(_koch_curve_pts(px, py, bx, by, depth - 1))
    pts.extend(_koch_curve_pts(bx, by, x2, y2, depth - 1))
    return pts


def _koch_snowflake(cx, cy, size, depth):
    r = size * 0.45
    angles = [math.pi / 2, math.pi / 2 + 2 * math.pi / 3,
              math.pi / 2 + 4 * math.pi / 3]
    verts = [(cx + r * math.cos(a), cy - r * math.sin(a)) for a in angles]
    all_pts = []
    for i in range(3):
        x1, y1 = verts[i]
        x2, y2 = verts[(i + 1) % 3]
        all_pts.extend(_koch_curve_pts(x1, y1, x2, y2, depth))
    return all_pts


# --- Koch border for UI panels ---
def koch_pts(x1, y1, x2, y2, depth):
    if depth == 0:
        return [(x1, y1)]
    dx, dy = x2 - x1, y2 - y1
    ax, ay = x1 + dx / 3, y1 + dy / 3
    bx, by = x1 + 2 * dx / 3, y1 + 2 * dy / 3
    px = (ax + bx) / 2 + math.sqrt(3) / 6 * (y1 - y2)
    py = (ay + by) / 2 + math.sqrt(3) / 6 * (x2 - x1)
    pts = []
    pts.extend(koch_pts(x1, y1, ax, ay, depth - 1))
    pts.extend(koch_pts(ax, ay, px, py, depth - 1))
    pts.extend(koch_pts(px, py, bx, by, depth - 1))
    pts.extend(koch_pts(bx, by, x2, y2, depth - 1))
    return pts


def draw_koch_rect(surf, rect, depth, color, width=1):
    x, y, w, h = rect
    corners = [(x, y), (x + w, y), (x + w, y + h), (x, y + h)]
    for i in range(4):
        pts = koch_pts(*corners[i], *corners[(i + 1) % 4], depth)
        pts.append(corners[(i + 1) % 4])
        int_pts = [(int(p[0]), int(p[1])) for p in pts]
        if len(int_pts) >= 2:
            pygame.draw.lines(surf, color, False, int_pts, width)


# --- Fractal glyph renderer ---
FRACTAL_GLYPHS = {
    "A": [[(0.1, 1), (0.5, 0), (0.9, 1)], [(0.25, 0.6), (0.75, 0.6)]],
    "B": [[(0.15, 0), (0.15, 1)], [(0.15, 0), (0.7, 0), (0.8, 0.12), (0.8, 0.38), (0.7, 0.5), (0.15, 0.5)],
          [(0.15, 0.5), (0.75, 0.5), (0.85, 0.62), (0.85, 0.88), (0.75, 1), (0.15, 1)]],
    "C": [[(0.85, 0.15), (0.5, 0), (0.15, 0.15), (0.15, 0.85), (0.5, 1), (0.85, 0.85)]],
    "D": [[(0.15, 0), (0.15, 1)], [(0.15, 0), (0.6, 0), (0.85, 0.3), (0.85, 0.7), (0.6, 1), (0.15, 1)]],
    "E": [[(0.8, 0), (0.15, 0), (0.15, 1), (0.8, 1)], [(0.15, 0.5), (0.65, 0.5)]],
    "F": [[(0.8, 0), (0.15, 0), (0.15, 1)], [(0.15, 0.5), (0.65, 0.5)]],
    "G": [[(0.85, 0.15), (0.5, 0), (0.15, 0.15), (0.15, 0.85), (0.5, 1), (0.85, 0.85), (0.85, 0.5), (0.55, 0.5)]],
    "H": [[(0.15, 0), (0.15, 1)], [(0.85, 0), (0.85, 1)], [(0.15, 0.5), (0.85, 0.5)]],
    "I": [[(0.3, 0), (0.7, 0)], [(0.5, 0), (0.5, 1)], [(0.3, 1), (0.7, 1)]],
    "K": [[(0.15, 0), (0.15, 1)], [(0.85, 0), (0.15, 0.5)], [(0.15, 0.5), (0.85, 1)]],
    "L": [[(0.15, 0), (0.15, 1), (0.8, 1)]],
    "M": [[(0.1, 1), (0.1, 0), (0.5, 0.45), (0.9, 0), (0.9, 1)]],
    "N": [[(0.15, 1), (0.15, 0), (0.85, 1), (0.85, 0)]],
    "O": [[(0.5, 0), (0.2, 0.15), (0.15, 0.5), (0.2, 0.85), (0.5, 1), (0.8, 0.85), (0.85, 0.5), (0.8, 0.15), (0.5, 0)]],
    "P": [[(0.15, 1), (0.15, 0), (0.7, 0), (0.85, 0.2), (0.85, 0.4), (0.7, 0.5), (0.15, 0.5)]],
    "R": [[(0.15, 1), (0.15, 0), (0.7, 0), (0.85, 0.2), (0.85, 0.4), (0.7, 0.5), (0.15, 0.5)], [(0.55, 0.5), (0.85, 1)]],
    "S": [[(0.8, 0.1), (0.5, 0), (0.15, 0.12), (0.15, 0.38), (0.5, 0.5), (0.85, 0.62), (0.85, 0.88), (0.5, 1), (0.15, 0.9)]],
    "T": [[(0.1, 0), (0.9, 0)], [(0.5, 0), (0.5, 1)]],
    "U": [[(0.15, 0), (0.15, 0.85), (0.3, 1), (0.7, 1), (0.85, 0.85), (0.85, 0)]],
    "W": [[(0.05, 0), (0.25, 1), (0.5, 0.5), (0.75, 1), (0.95, 0)]],
    "V": [[(0.1, 0), (0.5, 1), (0.9, 0)]],
    "Q": [[(0.5, 0), (0.2, 0.15), (0.15, 0.5), (0.2, 0.85), (0.5, 1), (0.8, 0.85), (0.85, 0.5), (0.8, 0.15), (0.5, 0)],
          [(0.6, 0.75), (0.9, 1.05)]],
}


def draw_fractal_text(surf, text, x, y, size, color, glow_color=None):
    char_w = size * 0.6
    for ch in text.upper():
        if ch == " ":
            x += char_w * 0.6
            continue
        strokes = FRACTAL_GLYPHS.get(ch)
        if strokes is None:
            x += char_w
            continue
        if glow_color:
            for stroke in strokes:
                pts = [(int(x + p[0] * char_w + 1), int(y + p[1] * size + 1)) for p in stroke]
                if len(pts) >= 2:
                    pygame.draw.lines(surf, glow_color, False, pts, max(1, size // 10))
        for stroke in strokes:
            pts = [(int(x + p[0] * char_w), int(y + p[1] * size)) for p in stroke]
            if len(pts) >= 2:
                pygame.draw.lines(surf, color, False, pts, max(1, size // 12))
        x += char_w


# --- Resource icons ---
def draw_fibonacci_spiral(surf, cx, cy, size, color):
    phi = (1 + math.sqrt(5)) / 2
    b = math.log(phi) / (math.pi / 2)
    pts = []
    for i in range(40):
        theta = i * 0.15
        r = 0.5 * math.exp(b * theta) * size / 5
        pts.append((int(cx + r * math.cos(theta)), int(cy - r * math.sin(theta))))
    if len(pts) >= 2:
        pygame.draw.lines(surf, color, False, pts, max(1, size // 6))


def draw_binary_tree(surf, cx, cy, size, color, depth=3, angle=-math.pi / 2, length=None):
    if length is None:
        length = size * 0.4
    if depth <= 0 or length < 1:
        return
    ex = cx + length * math.cos(angle)
    ey = cy + length * math.sin(angle)
    pygame.draw.line(surf, color, (int(cx), int(cy)), (int(ex), int(ey)), max(1, int(length / 5)))
    draw_binary_tree(surf, ex, ey, size, color, depth - 1, angle - 0.5, length * 0.65)
    draw_binary_tree(surf, ex, ey, size, color, depth - 1, angle + 0.5, length * 0.65)


def draw_octahedron(surf, cx, cy, size, color):
    s = size * 0.4
    pts = [(cx, cy - s), (cx + s, cy), (cx, cy + s), (cx - s, cy)]
    pygame.draw.polygon(surf, color, [(int(p[0]), int(p[1])) for p in pts], 1)
    pygame.draw.line(surf, color, (int(cx - s * 0.3), int(cy)), (int(cx + s * 0.3), int(cy)), 1)


def draw_voronoi_cluster(surf, cx, cy, size, color):
    rng = random.Random(77)
    seeds = [(cx + rng.randint(-size // 3, size // 3),
              cy + rng.randint(-size // 3, size // 3)) for _ in range(5)]
    for sx, sy in seeds:
        pygame.draw.circle(surf, color, (sx, sy), max(2, size // 5), 1)
        pygame.draw.circle(surf, color, (sx, sy), 1)


# --- Spirograph HP bar ---
def draw_hp_bar(surf, x, y, w, h, hp_pct, t=0.0):
    pygame.draw.rect(surf, (25, 25, 35), (x, y, w, h))
    if hp_pct > 0.6:
        color = (0, 200, 80)
    elif hp_pct > 0.3:
        color = (220, 200, 0)
    else:
        color = (200, 40, 40)
    fill_w = int(w * hp_pct)
    if fill_w > 0:
        for px in range(fill_w):
            wave = math.sin(px * 0.3 + t * 2) * 0.3 + 0.7
            col = tuple(int(c * wave) for c in color)
            pygame.draw.line(surf, col, (x + px, y), (x + px, y + h - 1))
    pygame.draw.rect(surf, COL_GUI_BORDER, (x, y, w, h), 1)


# --- Polar rose selection ring ---
def draw_selection_ring(surf, cx, cy, radius, n_petals, color, t=0.0):
    pts = []
    for i in range(100):
        theta = 2 * math.pi * i / 100 + t * 0.5
        r = radius + 2 * math.cos(n_petals * theta)
        pts.append((int(cx + r * math.cos(theta)), int(cy + r * math.sin(theta))))
    if len(pts) >= 3:
        pygame.draw.polygon(surf, color, pts, 1)


# --- Unit shapes ---
def draw_polar_shape(surf, cx, cy, radius, color, r_func, n_points=80, rotation=0.0, width=0):
    pts = []
    for i in range(n_points):
        theta = rotation + 2 * math.pi * i / n_points
        r = r_func(theta) * radius
        pts.append((cx + r * math.cos(theta), cy + r * math.sin(theta)))
    if len(pts) >= 3:
        if width == 0:
            pygame.draw.polygon(surf, color, pts)
        else:
            pygame.draw.polygon(surf, color, pts, width)
    return pts


def hex_r(theta):
    ct, st = abs(math.cos(theta)), abs(math.sin(theta))
    d = ct ** 4 + st ** 4
    return 1.0 / (d ** 0.25) if d > 1e-10 else 1.0


def blade_r(k, s=0.6):
    def f(theta):
        v = abs(math.cos(k * theta))
        return v ** s if v > 1e-10 else 0.0
    return f


# --- Sentinel drawing ---
def draw_sentinel_stone(surf, sx, sy, size=14, level=1):
    """Draw a Sentinel standing stone body."""
    h = int(size * 0.9)
    w = int(size * 0.45)
    body = [(sx - w, sy + h // 2), (sx - w + 2, sy - h // 2 + 3),
            (sx, sy - h // 2), (sx + w - 2, sy - h // 2 + 3),
            (sx + w, sy + h // 2)]
    pygame.draw.polygon(surf, SENTINEL_STONE, body)
    pygame.draw.polygon(surf, (0, 0, 0), body, 1)
    # Voronoi texture dots
    rng = random.Random(int(sx * 100 + sy))
    for _ in range(3):
        dx = rng.randint(-w + 2, w - 2)
        dy = rng.randint(-h // 2 + 4, h // 2 - 2)
        pygame.draw.circle(surf, (120, 110, 85), (sx + dx, sy + dy), 1)
    # Level 2 golden cap
    if level >= 2:
        pygame.draw.line(surf, EARTH_GOLD, (sx - w + 1, sy - h // 2 + 3),
                         (sx + w - 1, sy - h // 2 + 3), 2)


def draw_sentinel_with_field(surf, sx, sy, field_radius, level=1, t=0.0, breathing=True):
    """Draw a Sentinel with its Koch resonance field."""
    # Koch snowflake field
    koch_depth = min(level, 2)
    # Breathing animation
    breath = 1.0 + 0.03 * math.sin(t * 1.5) if breathing else 1.0
    animated_r = field_radius * breath

    field_pts = _koch_snowflake(sx, sy, animated_r * 2, koch_depth)
    int_field = [(int(p[0]), int(p[1])) for p in field_pts]

    if len(int_field) >= 3:
        # Field fill (faint)
        field_surf = pygame.Surface((W, H), pygame.SRCALPHA)
        fill_alpha = 14 if level == 1 else 22
        pygame.draw.polygon(field_surf, (*RESONANCE_GLOW, fill_alpha), int_field)
        # Koch outline
        border_alpha = 40 if level == 1 else 70
        border_color = RESONANCE_GLOW if level == 1 else EARTH_GOLD
        pygame.draw.polygon(field_surf, (*border_color, border_alpha), int_field,
                            max(1, int(field_radius) // 20))
        surf.blit(field_surf, (0, 0))

    # Level 2: golden interference rings
    if level >= 2:
        ring_surf = pygame.Surface((W, H), pygame.SRCALPHA)
        for ring_i in range(3):
            ring_r = int(field_radius * (0.5 + ring_i * 0.2) * breath)
            ring_alpha = max(0, 30 - ring_i * 10)
            pygame.draw.circle(ring_surf, (*EARTH_GOLD, ring_alpha),
                               (sx, sy), ring_r, 1)
        surf.blit(ring_surf, (0, 0))

    # Stone body on top
    draw_sentinel_stone(surf, sx, sy, level=level)


# --- Harmonic Pulse (expanding Koch rings) ---
def draw_harmonic_pulse(surf, cx, cy, progress, max_radius):
    """Draw an expanding Koch ring pulse. progress: 0.0 to 1.0."""
    if progress <= 0 or progress >= 1:
        return
    current_r = max_radius * progress
    alpha = int(180 * (1.0 - progress))
    ring_pts = _koch_snowflake(cx, cy, current_r * 2, 1)
    int_pts = [(int(p[0]), int(p[1])) for p in ring_pts]
    if len(int_pts) >= 3:
        pulse_surf = pygame.Surface((W, H), pygame.SRCALPHA)
        pygame.draw.polygon(pulse_surf, (*EARTH_GOLD, alpha), int_pts, 2)
        # Inner glow
        if progress < 0.5:
            inner_alpha = int(60 * (1.0 - progress * 2))
            pygame.draw.polygon(pulse_surf, (*RESONANCE_GLOW, inner_alpha), int_pts)
        surf.blit(pulse_surf, (0, 0))


# --- Enemy bleaching effect ---
def draw_bleached_enemy(surf, ex, ey, bleach_pct, t=0.0):
    """Draw an enemy with bleaching/destabilization from resonance field."""
    # Base color lerps toward white
    base = (80, 20, 20)
    bleached = tuple(int(base[i] + (255 - base[i]) * bleach_pct * 0.7) for i in range(3))

    # Jagged shape — more jagged as bleach increases
    pts = []
    n_verts = 8
    for i in range(n_verts):
        theta = 2 * math.pi * i / n_verts
        jag = 1.0 + bleach_pct * 0.4 * math.sin(7 * theta + t * 3)
        r = (8 + 3 * math.sin(5 * theta)) * jag
        pts.append((int(ex + r * math.cos(theta)), int(ey + r * math.sin(theta))))
    pygame.draw.polygon(surf, bleached, pts)
    pygame.draw.polygon(surf, (min(255, bleached[0] + 40), bleached[1], bleached[2]), pts, 1)

    # White shimmer overlay
    if bleach_pct > 0.2:
        shimmer = pygame.Surface((20, 20), pygame.SRCALPHA)
        shimmer_alpha = int(40 * bleach_pct)
        pygame.draw.circle(shimmer, (255, 255, 255, shimmer_alpha), (10, 10), 8)
        surf.blit(shimmer, (ex - 10, ey - 10))

    draw_hp_bar(surf, ex - 8, ey - 14, 16, 3, max(0.05, 1.0 - bleach_pct * 0.6), t)


# --- Spirograph absorption trail ---
def draw_absorption_trail(surf, start_x, start_y, target_x, target_y, progress, t=0.0):
    """Spirograph trail flowing TOWARD a Sentinel (absorption)."""
    if progress <= 0:
        return
    trail_surf = pygame.Surface((W, H), pygame.SRCALPHA)
    n_dots = int(20 * progress)
    for i in range(n_dots):
        frac = i / max(1, n_dots - 1)
        # Lerp from start toward target
        px = start_x + (target_x - start_x) * frac * progress
        py = start_y + (target_y - start_y) * frac * progress
        # Spirograph offset
        spiro_r = 6 * (1.0 - frac)
        px += spiro_r * math.cos(frac * 12 + t * 4)
        py += spiro_r * math.sin(frac * 8 + t * 4)
        dot_alpha = int(120 * (1.0 - frac))
        r_val = int(180 + 75 * frac)
        g_val = int(160 + 95 * frac)
        pygame.draw.circle(trail_surf, (r_val, g_val, 255, dot_alpha),
                           (int(px), int(py)), max(1, int(3 * (1.0 - frac))))
    surf.blit(trail_surf, (0, 0))


# --- Lissajous bloom (enemy death) ---
def draw_lissajous_bloom(surf, cx, cy, progress, t=0.0):
    """Lissajous figure bloom at enemy death point, contracting toward Sentinel."""
    if progress <= 0 or progress >= 1:
        return
    bloom_surf = pygame.Surface((W, H), pygame.SRCALPHA)
    r = 20 * (1.0 - progress * 0.6)
    alpha = int(150 * (1.0 - progress))
    pts = []
    for i in range(60):
        theta = 2 * math.pi * i / 60
        lx = cx + r * math.sin(3 * theta + t) * (1.0 - progress * 0.5)
        ly = cy + r * math.sin(2 * theta) * (1.0 - progress * 0.5)
        pts.append((int(lx), int(ly)))
    if len(pts) >= 3:
        pygame.draw.polygon(bloom_surf, (*RESONANCE_GLOW, alpha), pts, 1)
    surf.blit(bloom_surf, (0, 0))


# --- Main ---
def main():
    pygame.init()
    screen = pygame.display.set_mode((W, H))
    pygame.display.set_caption("VDD PoC: Mock Game Window — Sentinel Resonance Vision")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont(None, 20)
    font_sm = pygame.font.SysFont(None, 16)
    font_lg = pygame.font.SysFont(None, 24)
    font_alert = pygame.font.SysFont(None, 28)

    game_time = 0.0
    selected_tone = "soldier"
    show_formation = True
    depth_layer = 2
    combat_active = True

    # Pulse animation state
    pulse_active = False
    pulse_progress = 0.0
    pulse_sentinel_idx = 0  # which sentinel is pulsing

    # Incident alert state
    alert_timer = 0.0
    alert_direction = "EAST"

    # Mock game entities
    rng = random.Random(42)
    player_units = []
    for _ in range(12):
        tone = rng.choice(list(TONE_COLORS.keys()))
        x = rng.randint(180, 700)
        y = rng.randint(160, 480)
        player_units.append({"tone": tone, "x": x, "y": y, "hp": rng.uniform(0.4, 1.0)})

    # Enemies — some inside Sentinel field, some approaching
    enemies_in_field = [
        {"x": 560, "y": 310, "bleach": 0.6},
        {"x": 530, "y": 340, "bleach": 0.3},
        {"x": 580, "y": 360, "bleach": 0.85},  # nearly dead
    ]
    enemies_approaching = [
        {"x": 820, "y": 250, "hp": 0.8},
        {"x": 870, "y": 300, "hp": 0.9},
        {"x": 850, "y": 350, "hp": 0.7},
        {"x": 900, "y": 280, "hp": 0.6},
    ]

    # Sentinels — 3 forming a lattice triangle (D3 configuration)
    sentinels = [
        {"x": 540, "y": 280, "level": 2},  # main sentinel (Lv.2)
        {"x": 440, "y": 400, "level": 1},
        {"x": 640, "y": 400, "level": 1},
    ]
    sentinel_field_radius = 80

    # Buildings
    buildings = [
        {"type": "town_hall", "x": 280, "y": 350, "name": "Tree of Life"},
        {"type": "barracks", "x": 180, "y": 290, "name": "Resonance Forge"},
        {"type": "refinery", "x": 350, "y": 440, "name": "Harmonic Mill"},
    ]

    # Death bloom (static for demo)
    death_bloom = {"x": 590, "y": 350, "progress": 0.4}
    absorption_trail = {"start_x": 590, "start_y": 350,
                        "target_x": sentinels[0]["x"], "target_y": sentinels[0]["y"],
                        "progress": 0.6}

    tone_order = list(TONE_COLORS.keys())

    running = True
    while running:
        dt = clock.tick(30) / 1000.0
        game_time += dt

        # Update animations
        if pulse_active:
            pulse_progress += dt * 0.8
            if pulse_progress >= 1.0:
                pulse_active = False
                pulse_progress = 0.0

        if alert_timer > 0:
            alert_timer -= dt

        # Auto-cycle bleach for demo
        for e in enemies_in_field:
            e["bleach"] = min(1.0, e["bleach"] + dt * 0.05)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_f:
                    show_formation = not show_formation
                elif event.key == pygame.K_d:
                    depth_layer = (depth_layer + 1) % 7
                elif event.key == pygame.K_SPACE:
                    pulse_active = True
                    pulse_progress = 0.0
                    pulse_sentinel_idx = 0
                elif event.key == pygame.K_e:
                    combat_active = not combat_active
                    if combat_active:
                        alert_timer = 3.0
                        alert_direction = rng.choice(["NORTH", "EAST", "SOUTH"])
                elif pygame.K_1 <= event.key <= pygame.K_7:
                    idx = event.key - pygame.K_1
                    if idx < len(tone_order):
                        selected_tone = tone_order[idx]

        screen.fill(COL_BG)

        # === TERRAIN ===
        terrain_rng = random.Random(42)
        for ty in range(0, H, 32):
            for tx in range(0, W, 32):
                noise = terrain_rng.randint(-8, 8)
                c = tuple(max(0, min(255, TERRAIN_GREEN[i] + noise)) for i in range(3))
                pygame.draw.rect(screen, c, (tx, ty, 32, 32))

        # === SENTINEL LATTICE ===
        if depth_layer >= 2 and len(sentinels) >= 3:
            lattice_surf = pygame.Surface((W, H), pygame.SRCALPHA)
            # Lattice axes (gold lines between sentinels)
            for i in range(len(sentinels)):
                for j in range(i + 1, len(sentinels)):
                    s1, s2 = sentinels[i], sentinels[j]
                    pygame.draw.line(lattice_surf, (*EARTH_GOLD, 40),
                                     (s1["x"], s1["y"]), (s2["x"], s2["y"]), 1)
            # Lattice fill zone
            tri_pts = [(s["x"], s["y"]) for s in sentinels]
            pygame.draw.polygon(lattice_surf, (*EARTH_GOLD, 10), tri_pts)
            # Amplification text at centroid
            cx = sum(s["x"] for s in sentinels) // 3
            cy = sum(s["y"] for s in sentinels) // 3
            amp_label = font_sm.render("LATTICE D3", True, (*EARTH_GOLD,))
            lattice_surf.blit(amp_label, (cx - amp_label.get_width() // 2, cy - 6))
            screen.blit(lattice_surf, (0, 0))

        # === SENTINEL RESONANCE FIELDS ===
        for si, s in enumerate(sentinels):
            draw_sentinel_with_field(screen, s["x"], s["y"],
                                     sentinel_field_radius, s["level"],
                                     game_time, breathing=True)

        # === HARMONIC PULSE ===
        if pulse_active and pulse_sentinel_idx < len(sentinels):
            ps = sentinels[pulse_sentinel_idx]
            draw_harmonic_pulse(screen, ps["x"], ps["y"],
                                pulse_progress, sentinel_field_radius * 1.5)

        # === BUILDINGS ===
        for b in buildings:
            bx, by = b["x"], b["y"]
            if b["type"] == "town_hall":
                # Tree of Life — L-system tree silhouette
                pygame.draw.line(screen, (139, 90, 43), (bx, by + 15), (bx, by - 10), 3)
                pygame.draw.circle(screen, (30, 110, 50), (bx, by - 15), 14)
                pygame.draw.circle(screen, (40, 130, 60), (bx, by - 15), 14, 1)
            elif b["type"] == "barracks":
                # Resonance Forge — angular shape
                pts = [(bx, by - 15), (bx - 14, by + 10), (bx + 14, by + 10)]
                pygame.draw.polygon(screen, (140, 45, 45), pts)
                pygame.draw.polygon(screen, (180, 65, 65), pts, 1)
                # Forge glow
                glow = pygame.Surface((20, 20), pygame.SRCALPHA)
                pygame.draw.circle(glow, (255, 140, 40, 30), (10, 10), 8)
                screen.blit(glow, (bx - 10, by - 5))
            elif b["type"] == "refinery":
                # Harmonic Mill — octagonal
                pts = []
                for i in range(8):
                    a = 2 * math.pi * i / 8 - math.pi / 8
                    pts.append((int(bx + 12 * math.cos(a)), int(by + 12 * math.sin(a))))
                pygame.draw.polygon(screen, (100, 100, 130), pts)
                pygame.draw.polygon(screen, (130, 130, 160), pts, 1)

        # === ENEMIES INSIDE RESONANCE FIELD (bleaching) ===
        if combat_active:
            for e in enemies_in_field:
                draw_bleached_enemy(screen, e["x"], e["y"], e["bleach"], game_time)

            # Death bloom + absorption trail
            draw_lissajous_bloom(screen, death_bloom["x"], death_bloom["y"],
                                 0.3 + 0.2 * math.sin(game_time * 0.8), game_time)
            draw_absorption_trail(screen, absorption_trail["start_x"],
                                  absorption_trail["start_y"],
                                  absorption_trail["target_x"],
                                  absorption_trail["target_y"],
                                  0.5 + 0.3 * math.sin(game_time * 0.5), game_time)

        # === APPROACHING ENEMIES ===
        if combat_active:
            for eu in enemies_approaching:
                ex, ey = eu["x"], eu["y"]
                pts = []
                for i in range(8):
                    theta = 2 * math.pi * i / 8
                    r = 8 + 3 * math.sin(5 * theta)
                    pts.append((int(ex + r * math.cos(theta)),
                                int(ey + r * math.sin(theta))))
                pygame.draw.polygon(screen, (80, 20, 20), pts)
                pygame.draw.polygon(screen, (120, 30, 30), pts, 1)
                draw_hp_bar(screen, ex - 8, ey - 14, 16, 3, eu["hp"], game_time)

        # === PLAYER UNITS ===
        for u in player_units:
            ux, uy = u["x"], u["y"]
            tone = u["tone"]
            color = TONE_COLORS[tone]
            size = 10

            if tone == "gatherer":
                draw_polar_shape(screen, ux, uy, size, color, hex_r, rotation=math.pi / 6)
            elif tone == "soldier":
                draw_polar_shape(screen, ux, uy, size, color, blade_r(2.5), rotation=-math.pi / 2)
            elif tone == "archer":
                pygame.draw.arc(screen, color, (ux - 6, uy - 8, 12, 16), -1, 1, 2)
                pygame.draw.line(screen, color, (ux - 2, uy - 7), (ux - 2, uy + 7), 1)
            elif tone == "shield":
                draw_polar_shape(screen, ux, uy, size, color,
                                 lambda t: max(0.3, min(1.0, math.cos(t % (2 * math.pi / 3) - math.pi / 3) / math.cos(math.pi / 3))) if math.cos(math.pi / 3) > 0.01 else 1.0,
                                 n_points=60, rotation=-math.pi / 2)
            elif tone == "knight":
                draw_polar_shape(screen, ux, uy, size, color,
                                 lambda t: 0.6 + 0.4 * abs(math.cos(1.5 * t)),
                                 rotation=-math.pi / 2)
            elif tone == "healer":
                pygame.draw.circle(screen, color, (ux, uy), size - 2)
                pygame.draw.circle(screen, tuple(min(255, c + 60) for c in color),
                                   (ux, uy), size - 2, 1)
            elif tone == "sage":
                draw_polar_shape(screen, ux, uy, size, color,
                                 lambda t: 0.5 + 0.3 * math.sin(5 * t + 0.7 * math.cos(3 * t)),
                                 n_points=60)

            draw_hp_bar(screen, ux - 8, uy - size - 6, 16, 3, u["hp"], game_time)

            if tone == selected_tone:
                draw_selection_ring(screen, ux, uy, size + 3, 5, TONE_ACCENTS[tone], game_time)

        # === FORMATION OVERLAY ===
        if show_formation and depth_layer >= 2:
            soldiers = [u for u in player_units if u["tone"] == "soldier"]
            if len(soldiers) >= 3:
                avg_x = sum(s["x"] for s in soldiers[:5]) / min(5, len(soldiers))
                avg_y = sum(s["y"] for s in soldiers[:5]) / min(5, len(soldiers))
                aura = pygame.Surface((W, H), pygame.SRCALPHA)
                pts = []
                for i in range(100):
                    theta = 2 * math.pi * i / 100 + game_time * 0.2
                    r = 60 * abs(math.cos(2.5 * theta))
                    pts.append((int(avg_x + r * math.cos(theta)),
                                int(avg_y + r * math.sin(theta))))
                if len(pts) >= 3:
                    pygame.draw.polygon(aura, (*TONE_COLORS["soldier"], 20), pts)
                    pygame.draw.polygon(aura, (*TONE_COLORS["soldier"], 50), pts, 1)
                screen.blit(aura, (0, 0))

        # === ATTACK DIRECTION ARROWS (off-screen enemies) ===
        if combat_active:
            # Red chevron arrows pointing toward enemy cluster (right side)
            arrow_x = W - 180
            arrow_y = 300
            arrow_surf = pygame.Surface((W, H), pygame.SRCALPHA)
            pulse_alpha = int(160 + 80 * math.sin(game_time * 4))
            for offset in range(3):
                ax = arrow_x + offset * 12
                chevron = [(ax, arrow_y - 8), (ax + 10, arrow_y), (ax, arrow_y + 8)]
                pygame.draw.lines(arrow_surf, (255, 60, 40, pulse_alpha),
                                  False, chevron, 2)
            screen.blit(arrow_surf, (0, 0))

        # ============== GUI LAYER ==============
        gui_surf = pygame.Surface((W, H), pygame.SRCALPHA)

        # === TOP BAR ===
        top_h = 36
        pygame.draw.rect(gui_surf, (*COL_GUI_BG, 220), (0, 0, W, top_h))
        pygame.draw.rect(gui_surf, GHOST_STONE, (0, 0, W, top_h), 1)

        # Resources
        res_data = [
            ("Flux", 1247, RES_GOLD_COLOR, draw_fibonacci_spiral),
            ("Fiber", 834, RES_WOOD_COLOR, draw_binary_tree),
            ("Ore", 412, RES_IRON_COLOR, draw_octahedron),
            ("Crystal", 256, RES_STONE_COLOR, draw_voronoi_cluster),
        ]
        rx = 15
        for name, amount, color, icon_func in res_data:
            icon_func(gui_surf, rx + 8, 18, 14, color)
            text = font.render(f"{amount}", True, color)
            gui_surf.blit(text, (rx + 22, 10))
            rx += 100

        # Tension meter
        tension_x = rx + 30
        tension_w = 120
        tension_pct = 0.6 + 0.15 * math.sin(game_time * 1.5)
        pygame.draw.rect(gui_surf, (25, 25, 35), (tension_x, 8, tension_w, 20))
        fill_w = int(tension_w * tension_pct)
        for px in range(fill_w):
            t_frac = px / tension_w
            if t_frac < 0.5:
                c = (40, 120, 40)
            elif t_frac < 0.75:
                c = (200, 180, 40)
            else:
                c = (200, 60, 40)
            pygame.draw.line(gui_surf, c, (tension_x + px, 8), (tension_x + px, 27))

        # Tension border pulse during combat (red pulse during FOREBODING)
        if combat_active:
            pulse_val = int(40 * abs(math.sin(game_time * 3.0)))
            border_c = (200 + pulse_val // 2, 60, 40)
            pygame.draw.rect(gui_surf, border_c, (tension_x, 8, tension_w, 20), 2)
        else:
            pygame.draw.rect(gui_surf, COL_GUI_BORDER, (tension_x, 8, tension_w, 20), 1)

        tension_label = font_sm.render("TENSION", True, (120, 120, 140))
        gui_surf.blit(tension_label, (tension_x + tension_w // 2 - tension_label.get_width() // 2, 10))

        # Incident counter
        inc_x = tension_x + tension_w + 20
        inc_text = font.render("Incident 4/7", True, (180, 140, 60))
        gui_surf.blit(inc_text, (inc_x, 10))

        # Depth layer indicator
        depth_text = font_sm.render(f"Layer {depth_layer}", True, EARTH_GOLD)
        gui_surf.blit(depth_text, (W - 100, 12))

        # === BOTTOM PANEL ===
        bot_h = 140
        bot_y = H - bot_h
        pygame.draw.rect(gui_surf, (*COL_GUI_BG, 220), (0, bot_y, W, bot_h))

        tone_color = TONE_COLORS[selected_tone]
        pygame.draw.rect(gui_surf, tone_color, (0, bot_y, W, bot_h), 1)

        # Unit info panel — use display names
        display_name = TONE_DISPLAY.get(selected_tone, selected_tone.upper())
        draw_fractal_text(gui_surf, display_name, 20, bot_y + 10, 22,
                          tone_color, tuple(c // 3 for c in tone_color))

        stats = [
            "HP: 85/100",
            "ATK: 12  DEF: 8",
            "Rank: Veteran",
        ]
        for si, stat in enumerate(stats):
            st = font_sm.render(stat, True, (160, 160, 180))
            gui_surf.blit(st, (20, bot_y + 38 + si * 18))

        # Build buttons — updated names (no separate Tower)
        btn_data = [
            ("Tree of Life [Q]", (139, 90, 43)),
            ("Res. Forge [W]", (140, 45, 45)),
            ("Harm. Mill [E]", (100, 100, 130)),
            ("Sentinel [R]", SENTINEL_STONE),
        ]
        for bi, (bname, bcolor) in enumerate(btn_data):
            bx = W - 450 + bi * 110
            by = bot_y + 15
            bw, bh = 100, 55
            pygame.draw.rect(gui_surf, (35, 32, 50, 200), (bx, by, bw, bh))
            pygame.draw.rect(gui_surf, bcolor, (bx, by, bw, bh), 1)
            bt = font_sm.render(bname, True, bcolor)
            gui_surf.blit(bt, (bx + bw // 2 - bt.get_width() // 2, by + bh // 2 - 6))

        # Squad bar + Form Squad button
        if show_formation and depth_layer >= 2:
            squad_y = bot_y + 85
            squad_label = font_sm.render("Squad 1: Rose Formation", True, TONE_COLORS["soldier"])
            gui_surf.blit(squad_label, (20, squad_y))
            harmony = font_sm.render("Harmony: 94%", True, (255, 230, 80))
            gui_surf.blit(harmony, (200, squad_y))
            units_label = font_sm.render("3W 2R", True, (160, 160, 180))
            gui_surf.blit(units_label, (320, squad_y))

            # Form Squad button
            fsq_x, fsq_y = 390, squad_y - 3
            fsq_w, fsq_h = 90, 18
            pygame.draw.rect(gui_surf, (60, 45, 20, 200), (fsq_x, fsq_y, fsq_w, fsq_h))
            pygame.draw.rect(gui_surf, EARTH_GOLD, (fsq_x, fsq_y, fsq_w, fsq_h), 1)
            fsq_text = font_sm.render("Form Squad (F)", True, EARTH_GOLD)
            gui_surf.blit(fsq_text, (fsq_x + 4, fsq_y + 2))

        # Chord preview
        if depth_layer >= 2:
            chord_x = W - 450
            chord_y = bot_y + 85
            chord_label = font_sm.render("Rose: 94%  Spiral: 87%  Koch: 72%", True, (140, 140, 160))
            gui_surf.blit(chord_label, (chord_x, chord_y))

        # Formation discovery hint
        if depth_layer >= 2:
            hint_y = bot_y + 105
            hint_text = font_sm.render("Move 3+ units together to discover formations", True, (100, 100, 120))
            gui_surf.blit(hint_text, (20, hint_y))

        # === MINIMAP ===
        mm_size = 150
        mm_x = W - mm_size - 10
        mm_y = top_h + 10
        # Solid background + simple rect border (Koch bumps are too large at this scale)
        pygame.draw.rect(gui_surf, (*COL_GUI_BG, 200), (mm_x, mm_y, mm_size, mm_size))

        # Minimap terrain
        mm_terrain = pygame.Surface((mm_size - 4, mm_size - 4))
        mm_terrain.fill((30, 60, 40))
        gui_surf.blit(mm_terrain, (mm_x + 2, mm_y + 2))

        # Minimap sentinel markers (golden dots with small aura)
        for s in sentinels:
            mx = mm_x + 2 + int(s["x"] / W * (mm_size - 4))
            my = mm_y + 2 + int(s["y"] / H * (mm_size - 4))
            mm_aura = pygame.Surface((10, 10), pygame.SRCALPHA)
            pygame.draw.circle(mm_aura, (*EARTH_GOLD, 40), (5, 5), 4)
            gui_surf.blit(mm_aura, (mx - 5, my - 5))
            pygame.draw.circle(gui_surf, EARTH_GOLD, (mx, my), 2)

        # Minimap units
        for u in player_units:
            mx = mm_x + 2 + int(u["x"] / W * (mm_size - 4))
            my = mm_y + 2 + int(u["y"] / H * (mm_size - 4))
            pygame.draw.circle(gui_surf, TONE_COLORS[u["tone"]], (mx, my), 2)

        # Minimap enemy dots
        all_enemies = enemies_approaching + [{"x": e["x"], "y": e["y"]} for e in enemies_in_field]
        for eu in all_enemies:
            mx = mm_x + 2 + int(eu["x"] / W * (mm_size - 4))
            my = mm_y + 2 + int(eu["y"] / H * (mm_size - 4))
            pygame.draw.circle(gui_surf, (200, 40, 40), (mx, my), 2)

        # Camera viewport (simple golden rect)
        cam_w = int(mm_size * 0.4)
        cam_h = int(mm_size * 0.35)
        cam_x = mm_x + 10
        cam_y = mm_y + 15
        pygame.draw.rect(gui_surf, EARTH_GOLD, (cam_x, cam_y, cam_w, cam_h), 1)

        # Border drawn last, on top of terrain
        pygame.draw.rect(gui_surf, GHOST_STONE, (mm_x, mm_y, mm_size, mm_size), 1)

        # Minimap attack flash on spawn edge (during combat)
        if combat_active:
            flash_alpha = int(80 * abs(math.sin(game_time * 4)))
            # Flash on right edge (EAST spawn)
            flash_surf = pygame.Surface((3, mm_size), pygame.SRCALPHA)
            flash_surf.fill((255, 60, 40, flash_alpha))
            gui_surf.blit(flash_surf, (mm_x + mm_size - 3, mm_y))

        screen.blit(gui_surf, (0, 0))

        # === INCIDENT ALERT BANNER (center screen) ===
        if alert_timer > 0:
            alert_alpha = min(1.0, alert_timer / 0.5) if alert_timer < 0.5 else 1.0
            alert_surf = pygame.Surface((W, H), pygame.SRCALPHA)
            # Dark backdrop
            bar_h = 40
            bar_y = H // 2 - 60
            pygame.draw.rect(alert_surf, (20, 10, 10, int(180 * alert_alpha)),
                             (W // 4, bar_y, W // 2, bar_h))
            # Red border
            pygame.draw.rect(alert_surf, (200, 40, 40, int(220 * alert_alpha)),
                             (W // 4, bar_y, W // 2, bar_h), 2)
            screen.blit(alert_surf, (0, 0))
            # Text
            alert_text = font_alert.render(
                f"ENEMIES APPROACHING  [{alert_direction}]", True,
                (255, 80, 60))
            at_alpha_surf = pygame.Surface(alert_text.get_size(), pygame.SRCALPHA)
            at_alpha_surf.fill((255, 255, 255, int(255 * alert_alpha)))
            alert_text_copy = alert_text.copy()
            alert_text_copy.blit(at_alpha_surf, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
            screen.blit(alert_text_copy,
                        (W // 2 - alert_text.get_width() // 2, bar_y + 8))

        # === CONTROLS HELP ===
        help_text = "1-7: Tone  |  F: Formation  |  D: Depth  |  SPACE: Pulse  |  E: Enemy wave  |  ESC: Quit"
        ht = font_sm.render(help_text, True, (70, 70, 90))
        screen.blit(ht, (W // 2 - ht.get_width() // 2, H - 18))

        pygame.display.flip()

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
