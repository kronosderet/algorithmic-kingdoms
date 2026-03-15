"""
Generate PNG samples for the Resonance Chromatic Heptarchy.

Renders every unit tone (7 player + 7 Dark 7), buildings, Sentinel lattice,
and harmonic formation compositions to individual PNGs + composite grid sheets.

Output directory: visuals/samples/
"""
import os
import math
import random

# ---------------------------------------------------------------------------
# Headless pygame init
# ---------------------------------------------------------------------------
os.environ["SDL_VIDEODRIVER"] = "dummy"
import pygame
pygame.init()
pygame.display.set_mode((1, 1))

# ---------------------------------------------------------------------------
# Chromatic Heptarchy Palette (VDD Section 8)
# ---------------------------------------------------------------------------
COL_BG = (20, 20, 30)

# The Seven Tone Colors
TONE_COLORS = {
    "gatherer":  (50, 130, 220),   # Do — Worker Blue
    "soldier":   (200, 60, 60),    # Re — Military Red
    "archer":    (140, 100, 200),  # Mi — Precision Purple
    "shield":    (160, 150, 130),  # Fa — Stone Tan
    "knight":    (218, 165, 32),   # Sol — Earth Gold
    "healer":    (46, 139, 87),    # La — Life Green
    "sage":      (100, 50, 150),   # Ti — Void Violet
}
TONE_ACCENTS = {
    "gatherer":  (80, 180, 255),
    "soldier":   (255, 100, 80),
    "archer":    (180, 130, 255),
    "shield":    (200, 190, 170),
    "knight":    (255, 200, 60),
    "healer":    (80, 200, 120),
    "sage":      (150, 80, 220),
}

# The Dark 7 — Enemy Tone Colors
DARK7_COLORS = {
    "blight_reaper":   (20, 80, 20),    # Do mirror — fungal green
    "hollow_warden":   (80, 80, 100),   # Re mirror — hollow gray-blue
    "fade_ranger":     (140, 0, 140),   # Mi mirror — aggressive magenta
    "ironbark":        (90, 70, 40),    # Fa mirror — bark brown
    "thornknight":     (140, 100, 20),  # Sol mirror — tarnished gold
    "bloodtithe":      (55, 10, 15),    # La mirror — dark blood red
    "hexweaver":       (40, 15, 60),    # Ti mirror — abyss purple
}

# Rank colors
RANK_COLORS = {
    0: (140, 140, 140), 1: (205, 127, 50), 2: (192, 192, 210),
    3: (255, 215, 0), 4: (80, 180, 255),
}

# Building palette
_TH_BROWN = (139, 90, 43)
_TH_GREEN = (30, 110, 50)
_BK_MAROON = (140, 45, 45)
_RF_GRAY = (100, 100, 130)
_TW_STONE = (160, 160, 140)
_FORGE_ORANGE = (255, 140, 40)
_STEEL_BLUE = (100, 160, 220)
_SENTINEL_STONE = (140, 130, 100)
_SENTINEL_GLOW = (218, 165, 32)

# System colors
CONVERGENT_BLUE = (15, 25, 60)
DIVERGENT_RED = (120, 20, 40)
RESONANCE_GLOW = (180, 160, 255)
BOUNDARY_WHITE = (240, 235, 220)


# ---------------------------------------------------------------------------
# Shape helpers
# ---------------------------------------------------------------------------

def draw_polar_shape(surf, cx, cy, radius, color, r_func, n_points=120,
                     width=0, rotation=0.0):
    """Draw a shape defined by polar function r_func(theta)."""
    points = []
    for i in range(n_points):
        theta = rotation + 2 * math.pi * i / n_points
        r = r_func(theta) * radius
        x = cx + r * math.cos(theta)
        y = cy + r * math.sin(theta)
        points.append((x, y))
    if len(points) >= 3:
        if width == 0:
            pygame.draw.polygon(surf, color, points)
        else:
            pygame.draw.polygon(surf, color, points, width)
    return points


def hex_shape(n_power=4.0):
    """Superellipse that approximates a hexagon."""
    def r_func(theta):
        ct = abs(math.cos(theta))
        st = abs(math.sin(theta))
        denom = (ct ** n_power + st ** n_power)
        if denom < 1e-10:
            return 1.0
        return 1.0 / (denom ** (1.0 / n_power))
    return r_func


def blade_shape(k, sharpness=0.6):
    """Sharpened polar rose — blade-like petal tips."""
    def r_func(theta):
        v = abs(math.cos(k * theta))
        return v ** sharpness if v > 1e-10 else 0.0
    return r_func


def rose_shape(k):
    """Polar rose: r = cos(k * theta)."""
    def r_func(theta):
        return abs(math.cos(k * theta))
    return r_func


def reuleaux_shape(n_sides=3):
    """Constant-width curve (Reuleaux polygon)."""
    def r_func(theta):
        # Approximate Reuleaux with smooth constant-width curve
        t = theta % (2 * math.pi / n_sides)
        half = math.pi / n_sides
        # Distance from center of regular polygon to edge of Reuleaux
        d = math.cos(half)
        if d < 1e-10:
            return 1.0
        r = math.cos(t - half) / d
        return max(0.3, min(1.0, r))
    return r_func


def cycloid_shape(n_lobes=3):
    """Epicycloid-inspired shape for Knight."""
    def r_func(theta):
        return 0.6 + 0.4 * abs(math.cos(n_lobes * theta / 2))
    return r_func


def gaussian_shape(sigma=0.4):
    """Gaussian bell envelope on polar coords for Healer."""
    def r_func(theta):
        # Angular Gaussian — warm, rounded, widest at front
        diff = ((theta + math.pi) % (2 * math.pi)) - math.pi
        return 0.5 + 0.5 * math.exp(-diff * diff / (2 * sigma * sigma))
    return r_func


def julia_boundary_shape(c_real=-0.7269, c_imag=0.1889, max_iter=20):
    """Sample Julia set boundary points as a polar shape."""
    def r_func(theta):
        # Map theta to a circle, iterate, use escape time as radius
        z_r = 0.8 * math.cos(theta)
        z_i = 0.8 * math.sin(theta)
        for i in range(max_iter):
            zr2 = z_r * z_r - z_i * z_i + c_real
            zi2 = 2 * z_r * z_i + c_imag
            z_r, z_i = zr2, zi2
            if z_r * z_r + z_i * z_i > 4:
                return 0.3 + 0.7 * (i / max_iter)
        return 0.4
    return r_func


# ---------------------------------------------------------------------------
# Unit draw functions — The Seven Tones
# ---------------------------------------------------------------------------

def draw_gatherer(surf, cx, cy, radius, rank=0, enemy=False):
    """Do (1) — Superellipse hex, nature's tiling choice."""
    color = DARK7_COLORS["blight_reaper"] if enemy else TONE_COLORS["gatherer"]
    rotation = math.pi / 6

    pts = draw_polar_shape(surf, cx, cy, radius, color, hex_shape(4.0),
                           rotation=rotation)

    if enemy:
        def jagged(theta):
            base = hex_shape(4.0)(theta)
            return base * (1.0 + 0.08 * math.sin(17 * theta))
        draw_polar_shape(surf, cx, cy, radius * 1.05, (40, 100, 30),
                         jagged, rotation=rotation, width=2)
    elif pts and len(pts) >= 3:
        pygame.draw.polygon(surf, (0, 0, 0), pts, 2)

    if rank >= 1:
        inner_color = tuple(min(255, c + 40) for c in color)
        draw_polar_shape(surf, cx, cy, radius * 0.55, inner_color, hex_shape(4.0),
                         rotation=rotation + 0.05, width=max(1, radius // 15))
    if rank >= 2:
        inner_color2 = tuple(min(255, c + 70) for c in color)
        draw_polar_shape(surf, cx, cy, radius * 0.3, inner_color2, hex_shape(4.0),
                         rotation=rotation + 0.10, width=max(1, radius // 15))


def draw_soldier(surf, cx, cy, radius, rank=0, enemy=False):
    """Re (2) — Blade-like polar rose, petals that cut."""
    color = DARK7_COLORS["hollow_warden"] if enemy else TONE_COLORS["soldier"]

    k_values = [1.5, 2.5, 3.5, 4.0, 5.0]
    k = k_values[min(rank, len(k_values) - 1)]

    if not enemy and rank >= 1:
        tint = RANK_COLORS.get(rank, (140, 140, 140))
        blend = 2 if rank >= 3 else 4
        color = tuple((a * (blend - 1) + b) // blend for a, b in zip(color, tint))

    rotation = -math.pi / 2
    pts = draw_polar_shape(surf, cx, cy, radius, color, blade_shape(k),
                           rotation=rotation)

    if not enemy and pts and len(pts) >= 3:
        pygame.draw.polygon(surf, (0, 0, 0), pts, 2)

    if rank >= 2:
        inner_color = tuple(min(255, c + 50) for c in color)
        draw_polar_shape(surf, cx, cy, radius * 0.5, inner_color,
                         blade_shape(k + 0.5), rotation=rotation)

    if rank >= 3:
        pygame.draw.circle(surf, RANK_COLORS[rank], (int(cx), int(cy)),
                           max(2, radius // 6))

    if enemy:
        def jagged_blade(theta):
            base = blade_shape(k)(theta)
            return base * (1.0 + 0.12 * math.sin(13 * theta))
        draw_polar_shape(surf, cx, cy, radius * 1.08, (100, 95, 115),
                         jagged_blade, rotation=rotation, width=2)


def draw_archer(surf, cx, cy, radius, rank=0, enemy=False):
    """Mi (3) — Golden spiral bow, Fibonacci precision."""
    color = DARK7_COLORS["fade_ranger"] if enemy else TONE_COLORS["archer"]
    phi = (1 + math.sqrt(5)) / 2
    b = math.log(phi) / (math.pi / 2)

    top_pts = []
    bot_pts = []
    for i in range(60):
        theta = math.pi * 0.1 + (math.pi * 1.3) * i / 59
        r = 0.3 * math.exp(b * theta) * radius / 3.0
        x = cx + r * math.cos(theta) * 0.5
        top_pts.append((x, cy - r * math.sin(theta) * 0.7))
        bot_pts.append((x, cy + r * math.sin(theta) * 0.7))

    bow_polygon = top_pts + bot_pts[::-1]
    if len(bow_polygon) >= 3:
        fill_c = tuple(max(0, c - 40) for c in color)
        pygame.draw.polygon(surf, fill_c, bow_polygon)
        pygame.draw.polygon(surf, color, bow_polygon, 2)

    if not enemy:
        for pts_list in [top_pts, bot_pts]:
            if len(pts_list) >= 2:
                pygame.draw.lines(surf, (0, 0, 0), False, pts_list, max(4, radius // 10))

    for pts_list in [top_pts, bot_pts]:
        if len(pts_list) >= 2:
            pygame.draw.lines(surf, color, False, pts_list, max(3, radius // 12))

    # Bowstring
    string_top = cy - radius * 0.65
    string_bot = cy + radius * 0.65
    pygame.draw.line(surf, color, (cx - radius * 0.1, string_top),
                     (cx - radius * 0.1, string_bot), max(1, radius // 30))

    # Arrow
    arrow_tip_x = cx + radius * 0.8
    arrow_tail_x = cx - radius * 0.3
    pygame.draw.line(surf, BOUNDARY_WHITE, (arrow_tail_x, cy),
                     (arrow_tip_x, cy), max(1, radius // 25))
    head_size = radius * 0.12
    pygame.draw.polygon(surf, BOUNDARY_WHITE, [
        (arrow_tip_x, cy),
        (arrow_tip_x - head_size, cy - head_size * 0.6),
        (arrow_tip_x - head_size, cy + head_size * 0.6),
    ])

    # Fibonacci dots
    if rank >= 1:
        fib_angles = [0.5, 0.8, 1.1, 1.4, 1.8]
        n_dots = min(rank + 1, len(fib_angles))
        dot_color = TONE_ACCENTS["archer"]
        for i in range(n_dots):
            theta = math.pi * 0.1 + fib_angles[i]
            r = 0.3 * math.exp(b * theta) * radius / 3.0
            for mirror in [1, -1]:
                dx = cx + r * math.cos(theta) * 0.5
                dy = cy + mirror * r * math.sin(theta) * 0.7
                pygame.draw.circle(surf, dot_color, (int(dx), int(dy)),
                                   max(2, radius // 15))

    if enemy:
        n = 40
        pts = []
        for i in range(n):
            theta = 2 * math.pi * i / n
            r = radius * (0.85 + 0.08 * math.sin(11 * theta))
            pts.append((cx + r * math.cos(theta), cy + r * math.sin(theta)))
        pygame.draw.polygon(surf, (160, 0, 160), pts, 2)


def draw_shield(surf, cx, cy, radius, rank=0, enemy=False):
    """Fa (4) — Reuleaux constant-width curve, the immovable."""
    color = DARK7_COLORS["ironbark"] if enemy else TONE_COLORS["shield"]

    n_sides = 3 + min(rank, 2)  # 3 → 5 sides with rank
    pts = draw_polar_shape(surf, cx, cy, radius * 0.9, color,
                           reuleaux_shape(n_sides), n_points=180,
                           rotation=-math.pi / 2)

    if not enemy and pts and len(pts) >= 3:
        pygame.draw.polygon(surf, (0, 0, 0), pts, 2)

    # Inner constant-width echo
    if rank >= 1:
        inner_color = tuple(min(255, c + 30) for c in color)
        draw_polar_shape(surf, cx, cy, radius * 0.55, inner_color,
                         reuleaux_shape(n_sides), n_points=180,
                         rotation=-math.pi / 2, width=max(1, radius // 12))

    # Voronoi-like texture dots
    rng = random.Random(42)
    for _ in range(5 + rank * 2):
        angle = rng.uniform(0, 2 * math.pi)
        dist = rng.uniform(0.1, 0.5) * radius
        px = int(cx + dist * math.cos(angle))
        py = int(cy + dist * math.sin(angle))
        dot_c = tuple(min(255, c + 20) for c in color)
        pygame.draw.circle(surf, dot_c, (px, py), max(1, radius // 20))

    if enemy:
        def jagged_reuleaux(theta):
            base = reuleaux_shape(n_sides)(theta)
            return base * (1.0 + 0.10 * math.sin(11 * theta))
        draw_polar_shape(surf, cx, cy, radius * 0.95, (110, 85, 50),
                         jagged_reuleaux, n_points=180,
                         rotation=-math.pi / 2, width=2)


def draw_knight(surf, cx, cy, radius, rank=0, enemy=False):
    """Sol (5) — Cycloid, rolling thunder."""
    color = DARK7_COLORS["thornknight"] if enemy else TONE_COLORS["knight"]

    n_lobes = 3 + min(rank, 3)
    pts = draw_polar_shape(surf, cx, cy, radius * 0.95, color,
                           cycloid_shape(n_lobes), n_points=150,
                           rotation=-math.pi / 2)

    if not enemy and pts and len(pts) >= 3:
        pygame.draw.polygon(surf, (0, 0, 0), pts, 2)

    # Inner motion blur lines (momentum streaks)
    streak_color = TONE_ACCENTS["knight"] if not enemy else (170, 120, 30)
    for i in range(n_lobes):
        angle = -math.pi / 2 + 2 * math.pi * i / n_lobes
        x1 = cx + radius * 0.2 * math.cos(angle)
        y1 = cy + radius * 0.2 * math.sin(angle)
        x2 = cx + radius * 0.7 * math.cos(angle)
        y2 = cy + radius * 0.7 * math.sin(angle)
        pygame.draw.line(surf, streak_color, (int(x1), int(y1)),
                         (int(x2), int(y2)), max(1, radius // 20))

    # Central dot
    if rank >= 2:
        pygame.draw.circle(surf, TONE_ACCENTS["knight"], (int(cx), int(cy)),
                           max(2, radius // 5))

    if enemy:
        def jagged_cyc(theta):
            base = cycloid_shape(n_lobes)(theta)
            return base * (1.0 + 0.08 * math.sin(15 * theta))
        draw_polar_shape(surf, cx, cy, radius, (160, 115, 25),
                         jagged_cyc, n_points=150,
                         rotation=-math.pi / 2, width=2)


def draw_healer(surf, cx, cy, radius, rank=0, enemy=False):
    """La (6) — Gaussian bell, warmth that holds."""
    color = DARK7_COLORS["bloodtithe"] if enemy else TONE_COLORS["healer"]

    sigma = 0.4 + rank * 0.08
    pts = draw_polar_shape(surf, cx, cy, radius * 0.9, color,
                           gaussian_shape(sigma), n_points=120,
                           rotation=-math.pi / 2)

    if not enemy and pts and len(pts) >= 3:
        pygame.draw.polygon(surf, (0, 0, 0), pts, 2)

    # Concentric heal rings
    n_rings = 1 + min(rank, 3)
    ring_color = TONE_ACCENTS["healer"] if not enemy else (80, 15, 20)
    for r_i in range(n_rings):
        ring_r = radius * (0.3 + r_i * 0.18)
        pygame.draw.circle(surf, ring_color, (int(cx), int(cy)),
                           int(ring_r), max(1, radius // 25))

    # Sine wave cross (heal symbol)
    cross_color = tuple(min(255, c + 60) for c in color)
    for angle in [0, math.pi / 2]:
        pts_line = []
        for i in range(20):
            t = -0.6 + 1.2 * i / 19
            x = cx + t * radius * 0.6 * math.cos(angle) - math.sin(t * 6) * 3 * math.sin(angle)
            y = cy + t * radius * 0.6 * math.sin(angle) + math.sin(t * 6) * 3 * math.cos(angle)
            pts_line.append((int(x), int(y)))
        if len(pts_line) >= 2:
            pygame.draw.lines(surf, cross_color, False, pts_line, max(1, radius // 20))

    if enemy:
        def jagged_gauss(theta):
            base = gaussian_shape(sigma)(theta)
            return base * (1.0 + 0.10 * math.sin(13 * theta))
        draw_polar_shape(surf, cx, cy, radius * 0.95, (75, 15, 20),
                         jagged_gauss, n_points=120,
                         rotation=-math.pi / 2, width=2)


def draw_sage(surf, cx, cy, radius, rank=0, enemy=False):
    """Ti (7) — Julia set boundary, the bridge between worlds."""
    color = DARK7_COLORS["hexweaver"] if enemy else TONE_COLORS["sage"]

    # Julia parameters shift with rank
    c_values = [
        (-0.7269, 0.1889),
        (-0.8, 0.156),
        (-0.4, 0.6),
        (-0.835, -0.2321),
        (-0.70176, -0.3842),
    ]
    c_r, c_i = c_values[min(rank, len(c_values) - 1)]
    max_iter = 15 + rank * 5

    pts = draw_polar_shape(surf, cx, cy, radius * 0.9, color,
                           julia_boundary_shape(c_r, c_i, max_iter),
                           n_points=200, rotation=0)

    if not enemy and pts and len(pts) >= 3:
        pygame.draw.polygon(surf, (0, 0, 0), pts, 2)

    # Inner Julia echo (smaller, different c)
    if rank >= 1:
        c_r2, c_i2 = c_values[min(rank - 1, len(c_values) - 1)]
        inner_color = TONE_ACCENTS["sage"] if not enemy else (60, 20, 80)
        draw_polar_shape(surf, cx, cy, radius * 0.45, inner_color,
                         julia_boundary_shape(c_r2, c_i2, max_iter - 5),
                         n_points=150, rotation=0.3, width=max(1, radius // 15))

    # Central void dot
    void_color = (10, 8, 25)
    pygame.draw.circle(surf, void_color, (int(cx), int(cy)),
                       max(2, radius // 8))
    # Glow ring
    glow_c = TONE_ACCENTS["sage"] if not enemy else (60, 20, 80)
    pygame.draw.circle(surf, glow_c, (int(cx), int(cy)),
                       max(3, radius // 6), 1)

    if enemy:
        def jagged_julia(theta):
            base = julia_boundary_shape(c_r, c_i, max_iter)(theta)
            return base * (1.0 + 0.15 * math.sin(17 * theta))
        draw_polar_shape(surf, cx, cy, radius * 0.95, (55, 20, 80),
                         jagged_julia, n_points=200, rotation=0, width=2)


# ---------------------------------------------------------------------------
# Building draw functions
# ---------------------------------------------------------------------------

def _l_system_expand(axiom, rules, iters):
    s = axiom
    for _ in range(iters):
        s = "".join(rules.get(c, c) for c in s)
    return s


def _l_system_render(surf, cx, cy, instructions, angle_deg=22.5,
                     step=8, start_angle=-90, col_trunk=_TH_BROWN,
                     col_tip=_TH_GREEN, line_width=2):
    angle_rad = math.radians(angle_deg)
    cur_angle = math.radians(start_angle)
    x, y = float(cx), float(cy)
    stack = []
    depth = 0
    max_depth = max(1, instructions.count('['))
    for ch in instructions:
        if ch == 'F':
            nx = x + step * math.cos(cur_angle)
            ny = y + step * math.sin(cur_angle)
            t = min(1.0, depth / max(1, max_depth * 0.5))
            col = tuple(int(a + (b - a) * t) for a, b in zip(col_trunk, col_tip))
            w = max(1, line_width - depth // 3)
            pygame.draw.line(surf, col, (int(x), int(y)), (int(nx), int(ny)), w)
            x, y = nx, ny
        elif ch == '+':
            cur_angle += angle_rad
        elif ch == '-':
            cur_angle -= angle_rad
        elif ch == '[':
            stack.append((x, y, cur_angle, depth))
            depth += 1
        elif ch == ']':
            if stack:
                x, y, cur_angle, depth = stack.pop()


def _sierpinski(surf, x1, y1, x2, y2, x3, y3, depth, color):
    if depth == 0:
        pygame.draw.polygon(surf, color,
                            [(int(x1), int(y1)), (int(x2), int(y2)), (int(x3), int(y3))])
        return
    mx1, my1 = (x1 + x2) / 2, (y1 + y2) / 2
    mx2, my2 = (x2 + x3) / 2, (y2 + y3) / 2
    mx3, my3 = (x1 + x3) / 2, (y1 + y3) / 2
    darker = tuple(max(0, c - 12 * depth) for c in color)
    _sierpinski(surf, x1, y1, mx1, my1, mx3, my3, depth - 1, color)
    _sierpinski(surf, mx1, my1, x2, y2, mx2, my2, depth - 1, darker)
    _sierpinski(surf, mx3, my3, mx2, my2, x3, y3, depth - 1, color)


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


def draw_town_hall(surf, cx, cy, size, **_kw):
    half = int(size * 0.45)
    foundation = pygame.Surface((half * 2, half * 2), pygame.SRCALPHA)
    foundation.fill((15, 15, 20, 80))
    surf.blit(foundation, (cx - half, cy - half))
    tree_y = cy + half - 4
    iters = 4
    instructions = _l_system_expand("F", {"F": "FF+[+F-F-F]-[-F+F+F]"}, iters)
    step = size / (3.0 * (1.5 ** iters))
    _l_system_render(surf, cx, tree_y, instructions, angle_deg=22.5,
                     step=step, col_trunk=_TH_BROWN, col_tip=_TH_GREEN,
                     line_width=max(1, 4 - iters))


def draw_barracks(surf, cx, cy, size, **_kw):
    half = int(size * 0.45)
    foundation = pygame.Surface((half * 2, half * 2), pygame.SRCALPHA)
    foundation.fill((15, 15, 20, 80))
    surf.blit(foundation, (cx - half, cy - half))
    h_tri = half * math.sqrt(3)
    x1, y1 = cx, cy - h_tri * 0.6
    x2, y2 = cx - half, cy + h_tri * 0.4
    x3, y3 = cx + half, cy + h_tri * 0.4
    _sierpinski(surf, x1, y1, x2, y2, x3, y3, 4, _BK_MAROON)
    border_c = tuple(min(255, c + 40) for c in _BK_MAROON)
    pygame.draw.polygon(surf, border_c,
                        [(int(x1), int(y1)), (int(x2), int(y2)),
                         (int(x3), int(y3))], 2)


def draw_refinery(surf, cx, cy, size, **_kw):
    half = int(size * 0.45)
    foundation = pygame.Surface((half * 2, half * 2), pygame.SRCALPHA)
    foundation.fill((15, 15, 20, 80))
    surf.blit(foundation, (cx - half, cy - half))
    R, r, d = 5.0, 3.0, 5.0
    scale = size * 0.35 / (R + r + d)
    max_t = 6 * math.pi
    n_points = max(20, int(max_t * 15))
    points = []
    for i in range(n_points):
        t = max_t * i / max(1, n_points - 1)
        x = (R + r) * math.cos(t) - d * math.cos((R + r) / r * t)
        y = (R + r) * math.sin(t) - d * math.sin((R + r) / r * t)
        points.append((cx + x * scale, cy + y * scale))
    if len(points) >= 2:
        pygame.draw.lines(surf, _RF_GRAY, True, points, max(1, size // 40))
    step_pts = max(1, len(points) // 8)
    for i in range(0, len(points), step_pts):
        pygame.draw.circle(surf, _STEEL_BLUE,
                           (int(points[i][0]), int(points[i][1])),
                           max(2, size // 25))


def draw_sentinel(surf, cx, cy, size, level=1, **_kw):
    """Sentinel — standing stone with Koch resonance field aura.

    Level 1: basic stone + Koch depth-1 field outline
    Level 2: amplified stone + Koch depth-2 field + golden pulse ring
    """
    size = int(size)
    cx, cy = int(cx), int(cy)
    # --- Koch resonance field (drawn first, behind the stone) ---
    field_radius = size * 0.42
    koch_depth = min(level, 2)
    field_pts = _koch_snowflake(cx, cy, field_radius * 2, koch_depth)
    int_field = [(int(p[0]), int(p[1])) for p in field_pts]

    if len(int_field) >= 3:
        # Faint fill showing resonance zone
        field_surf = pygame.Surface((int(size * 1.2), int(size * 1.2)), pygame.SRCALPHA)
        shifted = [(int(p[0] - cx + size * 0.6), int(p[1] - cy + size * 0.6))
                   for p in field_pts]
        fill_alpha = 18 if level == 1 else 28
        pygame.draw.polygon(field_surf, (*RESONANCE_GLOW, fill_alpha), shifted)
        # Koch outline
        border_alpha = 50 if level == 1 else 90
        border_color = RESONANCE_GLOW if level == 1 else _SENTINEL_GLOW
        pygame.draw.polygon(field_surf, (*border_color, border_alpha), shifted,
                            max(1, int(size) // 40))
        surf.blit(field_surf, (int(cx - size * 0.6), int(cy - size * 0.6)))

    # Level 2: extra golden pulse ring (interference pattern hint)
    if level >= 2:
        pulse_surf = pygame.Surface((int(size * 1.2), int(size * 1.2)), pygame.SRCALPHA)
        pcx, pcy = int(size * 0.6), int(size * 0.6)
        for ring_i in range(3):
            ring_r = int(field_radius * (0.6 + ring_i * 0.25))
            ring_alpha = 35 - ring_i * 10
            pygame.draw.circle(pulse_surf, (*_SENTINEL_GLOW, max(0, ring_alpha)),
                               (pcx, pcy), ring_r, max(1, size // 50))
        surf.blit(pulse_surf, (int(cx - size * 0.6), int(cy - size * 0.6)))

    # --- Standing stone body (tall Reuleaux-inspired monolith) ---
    h = int(size * 0.7)
    w = int(size * 0.3)
    body_pts = [
        (cx - w // 2, cy + h // 3),
        (cx - w // 3, cy - h // 3),
        (cx, cy - h // 2),
        (cx + w // 3, cy - h // 3),
        (cx + w // 2, cy + h // 3),
    ]
    stone_color = _SENTINEL_STONE if level == 1 else (160, 148, 115)
    pygame.draw.polygon(surf, stone_color, body_pts)
    border_c = (0, 0, 0) if level == 1 else (80, 60, 30)
    pygame.draw.polygon(surf, border_c, body_pts, 2)

    # Voronoi cell texture (deterministic dots)
    rng = random.Random(137)
    for _ in range(7):
        ox = rng.randint(-w // 3, w // 3)
        oy = rng.randint(-h // 3, h // 4)
        dot_c = tuple(min(255, c + rng.randint(-15, 15)) for c in stone_color)
        pygame.draw.circle(surf, dot_c, (cx + ox, cy + oy), max(1, size // 25))

    # Level 2: golden glow dots on stone surface (absorbed energy)
    if level >= 2:
        for _ in range(4):
            ox = rng.randint(-w // 4, w // 4)
            oy = rng.randint(-h // 4, h // 5)
            pygame.draw.circle(surf, _SENTINEL_GLOW, (cx + ox, cy + oy),
                               max(1, size // 22))

    # Faint golden aura glow around stone
    aura_surf = pygame.Surface((size, size), pygame.SRCALPHA)
    for r_i in range(3):
        alpha = 25 - r_i * 7
        r_size = int(size * 0.25) + r_i * 5
        pygame.draw.circle(aura_surf, (*_SENTINEL_GLOW, max(0, alpha)),
                           (size // 2, size // 2), r_size)
    surf.blit(aura_surf, (cx - size // 2, cy - size // 2))


# ---------------------------------------------------------------------------
# Formation compositions
# ---------------------------------------------------------------------------

def draw_rose_formation(surf, cx, cy, size):
    """Rose formation — 5 soldiers in polar rose arrangement."""
    n_units = 5
    formation_r = size * 0.35
    for i in range(n_units):
        angle = 2 * math.pi * i / n_units - math.pi / 2
        ux = cx + formation_r * math.cos(angle)
        uy = cy + formation_r * math.sin(angle)
        draw_soldier(surf, ux, uy, size * 0.12, rank=2)

    # Formation aura — rose shape
    rose_color = (*TONE_COLORS["soldier"][:3],)
    aura_surf = pygame.Surface((int(size * 1.2), int(size * 1.2)), pygame.SRCALPHA)
    acx, acy = int(size * 0.6), int(size * 0.6)
    pts = []
    for i in range(120):
        theta = 2 * math.pi * i / 120
        r = formation_r * 1.4 * abs(math.cos(2.5 * theta))
        x = acx + r * math.cos(theta)
        y = acy + r * math.sin(theta)
        pts.append((x, y))
    if len(pts) >= 3:
        pygame.draw.polygon(aura_surf, (*rose_color, 30), pts)
        pygame.draw.polygon(aura_surf, (*rose_color, 60), pts, 1)
    surf.blit(aura_surf, (int(cx - size * 0.6), int(cy - size * 0.6)))

    # Spring connections
    for i in range(n_units):
        for j in range(i + 1, n_units):
            a1 = 2 * math.pi * i / n_units - math.pi / 2
            a2 = 2 * math.pi * j / n_units - math.pi / 2
            x1 = cx + formation_r * math.cos(a1)
            y1 = cy + formation_r * math.sin(a1)
            x2 = cx + formation_r * math.cos(a2)
            y2 = cy + formation_r * math.sin(a2)
            pygame.draw.line(surf, (*TONE_COLORS["soldier"], 40),
                             (int(x1), int(y1)), (int(x2), int(y2)), 1)


def draw_spiral_formation(surf, cx, cy, size):
    """Golden spiral formation — mixed archers and soldiers."""
    phi = (1 + math.sqrt(5)) / 2
    n_units = 7
    for i in range(n_units):
        angle = i * 2 * math.pi / phi
        r = size * 0.08 * math.sqrt(i + 1)
        ux = cx + r * math.cos(angle)
        uy = cy + r * math.sin(angle)
        if i % 2 == 0:
            draw_archer(surf, ux, uy, size * 0.10, rank=1)
        else:
            draw_soldier(surf, ux, uy, size * 0.10, rank=1)

    # Spiral aura
    aura_surf = pygame.Surface((int(size * 1.2), int(size * 1.2)), pygame.SRCALPHA)
    acx, acy = int(size * 0.6), int(size * 0.6)
    spiral_pts = []
    for i in range(100):
        t = i * 0.1
        r = size * 0.03 * t
        x = acx + r * math.cos(t)
        y = acy + r * math.sin(t)
        spiral_pts.append((int(x), int(y)))
    if len(spiral_pts) >= 2:
        pygame.draw.lines(aura_surf, (*TONE_ACCENTS["archer"], 50),
                          False, spiral_pts, 1)
    surf.blit(aura_surf, (int(cx - size * 0.6), int(cy - size * 0.6)))


def draw_koch_formation(surf, cx, cy, size):
    """Koch formation — shields and soldiers in snowflake arrangement."""
    # Koch snowflake perimeter positions
    depth = 2
    points = _koch_snowflake(cx, cy, size * 0.6, depth)
    n_units = 6
    step = max(1, len(points) // n_units)
    for i in range(0, min(len(points), n_units * step), step):
        px, py = points[i]
        if (i // step) % 2 == 0:
            draw_shield(surf, px, py, size * 0.10, rank=1)
        else:
            draw_soldier(surf, px, py, size * 0.10, rank=1)

    # Koch aura
    aura_pts = [(int(p[0]), int(p[1])) for p in points]
    if len(aura_pts) >= 3:
        aura_surf = pygame.Surface((int(size * 1.2), int(size * 1.2)), pygame.SRCALPHA)
        shifted = [(int(p[0] - cx + size * 0.6), int(p[1] - cy + size * 0.6))
                   for p in points]
        pygame.draw.polygon(aura_surf, (*TONE_COLORS["shield"], 25), shifted)
        pygame.draw.polygon(aura_surf, (*TONE_ACCENTS["shield"], 50), shifted, 1)
        surf.blit(aura_surf, (int(cx - size * 0.6), int(cy - size * 0.6)))


def draw_sentinel_lattice(surf, cx, cy, size):
    """D3 Sentinel lattice — 6 Sentinels with symmetry axes."""
    n = 6
    lattice_r = size * 0.30
    positions = []
    for i in range(n):
        angle = 2 * math.pi * i / n - math.pi / 2
        sx = cx + lattice_r * math.cos(angle)
        sy = cy + lattice_r * math.sin(angle)
        positions.append((sx, sy))
        draw_sentinel(surf, sx, sy, size * 0.22)

    # Symmetry axes (gold lines)
    for i in range(3):
        p1 = positions[i]
        p2 = positions[(i + 3) % n]
        pygame.draw.line(surf, _SENTINEL_GLOW,
                         (int(p1[0]), int(p1[1])),
                         (int(p2[0]), int(p2[1])), 1)

    # Interior fill zone (faint gold wash)
    hex_pts = [(int(p[0]), int(p[1])) for p in positions]
    fill_surf = pygame.Surface((int(size), int(size)), pygame.SRCALPHA)
    shifted = [(int(p[0] - cx + size / 2), int(p[1] - cy + size / 2)) for p in positions]
    if len(shifted) >= 3:
        pygame.draw.polygon(fill_surf, (*_SENTINEL_GLOW, 15), shifted)
    surf.blit(fill_surf, (int(cx - size / 2), int(cy - size / 2)))


# ---------------------------------------------------------------------------
# Sentinel resonance defense composition
# ---------------------------------------------------------------------------

def draw_sentinel_defense(surf, cx, cy, size):
    """Sentinel resonance field damaging incoming enemies.

    Shows: Sentinel at center with Koch field, 3 enemies inside field
    being bleached/destabilized, spirograph absorption trail from a dying enemy.
    """
    # Draw the Sentinel (level 2 — amplified)
    draw_sentinel(surf, cx, cy, size * 0.5, level=2)

    # Koch field outline (larger, visible)
    field_r = size * 0.40
    field_pts = _koch_snowflake(cx, cy, field_r * 2, 2)
    int_pts = [(int(p[0]), int(p[1])) for p in field_pts]
    if len(int_pts) >= 3:
        field_surf = pygame.Surface((int(size), int(size)), pygame.SRCALPHA)
        shifted = [(int(p[0] - cx + size / 2), int(p[1] - cy + size / 2))
                   for p in field_pts]
        pygame.draw.polygon(field_surf, (*RESONANCE_GLOW, 22), shifted)
        pygame.draw.polygon(field_surf, (*RESONANCE_GLOW, 70), shifted, 2)
        surf.blit(field_surf, (int(cx - size / 2), int(cy - size / 2)))

    # Enemies inside field (bleached/destabilized)
    enemy_positions = [
        (cx + size * 0.22, cy - size * 0.15),
        (cx - size * 0.18, cy + size * 0.20),
        (cx + size * 0.05, cy + size * 0.30),
    ]
    enemy_funcs = [
        (draw_soldier, "hollow_warden"),
        (draw_archer, "fade_ranger"),
        (draw_knight, "thornknight"),
    ]
    for (ex, ey), (func, _name) in zip(enemy_positions, enemy_funcs):
        func(surf, ex, ey, size * 0.08, rank=1, enemy=True)
        # Bleaching effect — white shimmer overlay
        bleach_surf = pygame.Surface((int(size * 0.2), int(size * 0.2)), pygame.SRCALPHA)
        bcx, bcy = int(size * 0.1), int(size * 0.1)
        pygame.draw.circle(bleach_surf, (255, 255, 255, 25), (bcx, bcy), int(size * 0.06))
        surf.blit(bleach_surf, (int(ex - size * 0.1), int(ey - size * 0.1)))

    # Spirograph absorption trail — from dying enemy toward Sentinel
    dying_x, dying_y = cx - size * 0.30, cy - size * 0.25
    # Small Lissajous bloom at death point
    n_bloom = 40
    a_ratio, b_ratio = 3, 2
    bloom_r = size * 0.05
    bloom_pts = []
    for i in range(n_bloom):
        t = 2 * math.pi * i / n_bloom
        bx = dying_x + bloom_r * math.sin(a_ratio * t + 0.3)
        by = dying_y + bloom_r * math.sin(b_ratio * t)
        bloom_pts.append((int(bx), int(by)))
    if len(bloom_pts) >= 3:
        bloom_surf = pygame.Surface((int(size), int(size)), pygame.SRCALPHA)
        shifted_bloom = [(int(p[0] - cx + size / 2), int(p[1] - cy + size / 2))
                         for p in bloom_pts]
        pygame.draw.polygon(bloom_surf, (255, 180, 80, 60), shifted_bloom)
        pygame.draw.polygon(bloom_surf, (255, 200, 100, 120), shifted_bloom, 1)
        surf.blit(bloom_surf, (int(cx - size / 2), int(cy - size / 2)))

    # Contracting spirograph trail from death point to Sentinel
    R_spiro, r_spiro, d_spiro = 4.0, 2.5, 3.0
    n_trail = 5
    for t_i in range(n_trail):
        frac = (t_i + 1) / (n_trail + 1)
        trail_x = dying_x + (cx - dying_x) * frac
        trail_y = dying_y + (cy - dying_y) * frac
        trail_r = size * 0.015 * (1.0 - frac * 0.6)
        # Tiny spirograph dot
        trail_alpha = int(180 * (1.0 - frac * 0.5))
        trail_color = tuple(int(a + (b - a) * frac) for a, b in
                            zip(DIVERGENT_RED, _SENTINEL_GLOW))
        pygame.draw.circle(surf, trail_color,
                           (int(trail_x), int(trail_y)),
                           max(2, int(trail_r)))


# ---------------------------------------------------------------------------
# Dark 7 composition
# ---------------------------------------------------------------------------

def draw_dark7_army(surf, cx, cy, size):
    """Enemy wave — all 7 Dark 7 types in attack formation."""
    enemy_funcs = [
        (draw_gatherer, "blight_reaper"),
        (draw_soldier, "hollow_warden"),
        (draw_archer, "fade_ranger"),
        (draw_shield, "ironbark"),
        (draw_knight, "thornknight"),
        (draw_healer, "bloodtithe"),
        (draw_sage, "hexweaver"),
    ]
    unit_r = size * 0.11
    spread = size * 0.32
    for i, (func, _name) in enumerate(enemy_funcs):
        angle = 2 * math.pi * i / len(enemy_funcs) - math.pi / 2
        ux = cx + spread * math.cos(angle)
        uy = cy + spread * math.sin(angle)
        func(surf, ux, uy, unit_r, rank=1, enemy=True)

    # Divergent aura (jagged red circle)
    aura_surf = pygame.Surface((int(size), int(size)), pygame.SRCALPHA)
    acx, acy = int(size / 2), int(size / 2)
    n = 60
    aura_pts = []
    for i in range(n):
        theta = 2 * math.pi * i / n
        r = spread * 1.3 + 5 * math.sin(11 * theta)
        aura_pts.append((int(acx + r * math.cos(theta)),
                         int(acy + r * math.sin(theta))))
    if len(aura_pts) >= 3:
        pygame.draw.polygon(aura_surf, (*DIVERGENT_RED, 40), aura_pts)
        pygame.draw.polygon(aura_surf, (*DIVERGENT_RED, 80), aura_pts, 1)
    surf.blit(aura_surf, (int(cx - size / 2), int(cy - size / 2)))


# ---------------------------------------------------------------------------
# Rendering & Grid Sheet
# ---------------------------------------------------------------------------

TILE = 128
DRAW_RADIUS = 48
BLDG_SIZE = 96
COMP_SIZE = 200  # composition tile size


def render_unit_png(draw_func, rank, enemy, filepath):
    surf = pygame.Surface((TILE, TILE), pygame.SRCALPHA)
    surf.fill((0, 0, 0, 0))
    draw_func(surf, TILE // 2, TILE // 2, DRAW_RADIUS, rank=rank, enemy=enemy)
    pygame.image.save(surf, filepath)


def render_building_png(draw_func, filepath, **kwargs):
    surf = pygame.Surface((TILE, TILE), pygame.SRCALPHA)
    surf.fill((0, 0, 0, 0))
    draw_func(surf, TILE // 2, TILE // 2, BLDG_SIZE, **kwargs)
    pygame.image.save(surf, filepath)


def render_composition_png(draw_func, filepath, size=COMP_SIZE):
    surf = pygame.Surface((size, size), pygame.SRCALPHA)
    surf.fill((*COL_BG, 255))
    draw_func(surf, size // 2, size // 2, size)
    pygame.image.save(surf, filepath)


def build_unit_list():
    """All 7 player tones × ranks + Dark 7 enemies."""
    units = []
    tone_data = [
        ("gatherer", draw_gatherer, 3),
        ("soldier", draw_soldier, 5),
        ("archer", draw_archer, 5),
        ("shield", draw_shield, 3),
        ("knight", draw_knight, 4),
        ("healer", draw_healer, 3),
        ("sage", draw_sage, 5),
    ]
    for tone_name, draw_func, max_rank in tone_data:
        for rank in range(max_rank):
            units.append((f"{tone_name}_{rank}_friendly.png", draw_func, rank, False))
        units.append((f"{tone_name}_1_enemy.png", draw_func, 1, True))
    return units


def build_building_list():
    return [
        ("building_town_hall.png", draw_town_hall, {}),
        ("building_barracks.png", draw_barracks, {}),
        ("building_refinery.png", draw_refinery, {}),
        ("building_sentinel_lv1.png", draw_sentinel, {"level": 1}),
        ("building_sentinel_lv2.png", draw_sentinel, {"level": 2}),
    ]


def build_composition_list():
    return [
        ("formation_rose.png", draw_rose_formation),
        ("formation_spiral.png", draw_spiral_formation),
        ("formation_koch.png", draw_koch_formation),
        ("sentinel_lattice_d3.png", draw_sentinel_lattice),
        ("sentinel_resonance_defense.png", draw_sentinel_defense),
        ("dark7_army.png", draw_dark7_army),
    ]


def generate_grid_sheet(items, out_dir, filename, cols=8, tile_size=TILE):
    """Composite items into a labeled grid sheet."""
    total = len(items)
    rows = math.ceil(total / cols)
    label_h = 18
    cell_h = tile_size + label_h
    sheet_w = cols * tile_size
    sheet_h = rows * cell_h

    sheet = pygame.Surface((sheet_w, sheet_h))
    sheet.fill(COL_BG)
    font = pygame.font.SysFont(None, 14)

    for idx, item in enumerate(items):
        col = idx % cols
        row = idx // cols
        x = col * tile_size
        y = row * cell_h

        # Load the individual PNG
        img_path = os.path.join(out_dir, item[0])
        if os.path.exists(img_path):
            img = pygame.image.load(img_path)
            if img.get_size() != (tile_size, tile_size):
                img = pygame.transform.smoothscale(img, (tile_size, tile_size))
            sheet.blit(img, (x, y))

        label = item[0].replace(".png", "")
        lbl_surf = font.render(label, True, (160, 160, 180))
        lbl_x = x + (tile_size - lbl_surf.get_width()) // 2
        lbl_y = y + tile_size + 1
        sheet.blit(lbl_surf, (lbl_x, lbl_y))

    grid_path = os.path.join(out_dir, filename)
    pygame.image.save(sheet, grid_path)
    return grid_path


def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    out_dir = os.path.join(script_dir, "samples")
    os.makedirs(out_dir, exist_ok=True)

    units = build_unit_list()
    buildings = build_building_list()
    compositions = build_composition_list()

    total = len(units) + len(buildings) + len(compositions)
    print(f"Generating {total} samples in: {out_dir}")
    count = 0

    # Units
    for filename, draw_func, rank, enemy in units:
        filepath = os.path.join(out_dir, filename)
        render_unit_png(draw_func, rank, enemy, filepath)
        count += 1
        print(f"  [{count:2d}/{total}] {filename}")

    # Buildings
    for filename, draw_func, kwargs in buildings:
        filepath = os.path.join(out_dir, filename)
        render_building_png(draw_func, filepath, **kwargs)
        count += 1
        print(f"  [{count:2d}/{total}] {filename}")

    # Compositions
    for filename, draw_func in compositions:
        filepath = os.path.join(out_dir, filename)
        render_composition_png(draw_func, filepath)
        count += 1
        print(f"  [{count:2d}/{total}] {filename}")

    # Grid sheets
    unit_items = [(f, d, r, e) for f, d, r, e in units]
    grid1 = generate_grid_sheet(unit_items, out_dir, "sheet_all_tones.png")
    print(f"  Grid -> {os.path.basename(grid1)}")

    bldg_items = [(f, d, k) for f, d, k in buildings]
    grid2 = generate_grid_sheet(bldg_items, out_dir, "sheet_buildings.png", cols=6)
    print(f"  Grid -> {os.path.basename(grid2)}")

    comp_items = [(f, d) for f, d in compositions]
    grid3 = generate_grid_sheet(comp_items, out_dir, "sheet_compositions.png",
                                cols=6, tile_size=COMP_SIZE)
    print(f"  Grid -> {os.path.basename(grid3)}")

    print("Done.")


if __name__ == "__main__":
    main()
