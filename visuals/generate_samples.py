"""
Generate PNG samples for all unit and building shapes.
v10_1: blade-like soldiers, black enemies, filled archer bows, black edges,
       VDD Phase 3 algorithmic building shapes (L-system, Sierpinski, Koch, Spirograph).

Renders each entity to a 128x128 transparent PNG, then composites
a combined grid sheet (all_entities.png).

Output directory: visuals/samples/
Naming: {type}_{rank}_{side}.png  (units)
        building_{type}[_lv2].png (buildings)
"""
import os
import sys
import math
import random

# ---------------------------------------------------------------------------
# Headless pygame init (no display window needed)
# ---------------------------------------------------------------------------
os.environ["SDL_VIDEODRIVER"] = "dummy"
import pygame
pygame.init()
# We need a tiny dummy display so pygame.draw works
pygame.display.set_mode((1, 1))

# ---------------------------------------------------------------------------
# Palette (v10_1 updated)
# ---------------------------------------------------------------------------
COL_BG = (20, 20, 30)
WORKER_BLUE = (50, 130, 220)
SOLDIER_RED = (200, 60, 60)
ARCHER_GREEN = (50, 190, 50)
RANK_COLORS = {
    0: (140, 140, 140),
    1: (205, 127, 50),
    2: (192, 192, 210),
    3: (255, 215, 0),
    4: (80, 180, 255),
}
RANK_NAMES = ["Recruit", "Veteran", "Corporal", "Sergeant", "Captain"]
WORKER_RANK_NAMES = ["Novice", "Foreman", "Master"]

# v10g2: enemy colors -> near-black with faint color accents
ENEMY_WORKER = (25, 35, 55)
ENEMY_SOLDIER = (35, 12, 12)
ENEMY_ARCHER = (35, 10, 30)
ENEMY_SIEGE = (40, 18, 8)
ENEMY_ELITE = (50, 10, 45)

# v10_1: building palette
_TH_BROWN = (139, 90, 43)
_TH_GREEN = (30, 110, 50)
_BK_MAROON = (140, 45, 45)
_RF_GRAY = (100, 100, 130)
_TW_STONE = (160, 160, 140)
_FORGE_ORANGE = (255, 140, 40)
_STEEL_BLUE = (100, 160, 220)

# ---------------------------------------------------------------------------
# Shape helpers
# ---------------------------------------------------------------------------

def draw_polar_shape(surf, cx, cy, radius, color, r_func, n_points=120,
                     width=0, rotation=0.0):
    """Draw a shape defined by polar function r_func(theta) -> radius multiplier."""
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
    """v10g2: Sharpened polar rose -- blade-like petal tips."""
    def r_func(theta):
        v = abs(math.cos(k * theta))
        return v ** sharpness if v > 1e-10 else 0.0
    return r_func


def rose_shape(k):
    """Polar rose: r = cos(k * theta)."""
    def r_func(theta):
        return abs(math.cos(k * theta))
    return r_func


def golden_spiral_bow(cx, cy, radius, surf, color, rank=0, enemy=False):
    """v10g2: Draw archer bow with filled body for visibility."""
    phi = (1 + math.sqrt(5)) / 2
    b = math.log(phi) / (math.pi / 2)
    n_arc = 60

    # compute both limb arcs
    top_pts = []
    bot_pts = []
    for i in range(n_arc):
        theta = math.pi * 0.1 + (math.pi * 1.3) * i / (n_arc - 1)
        r = 0.3 * math.exp(b * theta) * radius / 3.0
        x = cx + r * math.cos(theta) * 0.5
        top_pts.append((x, cy - r * math.sin(theta) * 0.7))
        bot_pts.append((x, cy + r * math.sin(theta) * 0.7))

    # v10g2: filled bow body polygon
    bow_polygon = top_pts + bot_pts[::-1]
    if len(bow_polygon) >= 3:
        fill_c = tuple(max(0, c - 40) for c in color)
        pygame.draw.polygon(surf, fill_c, bow_polygon)
        pygame.draw.polygon(surf, color, bow_polygon, 2)

    # v10g2: black shadow behind limbs (player only)
    if not enemy:
        for pts_list in [top_pts, bot_pts]:
            if len(pts_list) >= 2:
                pygame.draw.lines(surf, (0, 0, 0), False, pts_list, max(4, radius // 10))

    # bow limbs on top (v10g2: thicker)
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
    arrow_y = cy
    pygame.draw.line(surf, (240, 235, 220), (arrow_tail_x, arrow_y),
                     (arrow_tip_x, arrow_y), max(1, radius // 25))
    # Arrowhead
    head_size = radius * 0.12
    pygame.draw.polygon(surf, (240, 235, 220), [
        (arrow_tip_x, arrow_y),
        (arrow_tip_x - head_size, arrow_y - head_size * 0.6),
        (arrow_tip_x - head_size, arrow_y + head_size * 0.6),
    ])

    # Fibonacci dots on bow limbs (rank-based)
    if rank >= 1:
        fib_angles = [0.5, 0.8, 1.1, 1.4, 1.8]
        n_dots = min(rank + 1, len(fib_angles))
        dot_color = RANK_COLORS.get(rank, (200, 200, 200))
        for i in range(n_dots):
            theta = math.pi * 0.1 + fib_angles[i]
            r = 0.3 * math.exp(b * theta) * radius / 3.0
            for mirror in [1, -1]:
                dx = cx + r * math.cos(theta) * 0.5
                dy = cy + mirror * r * math.sin(theta) * 0.7
                pygame.draw.circle(surf, dot_color, (int(dx), int(dy)),
                                   max(2, radius // 15))


# ---------------------------------------------------------------------------
# v10_1: Building shape helpers (mirrored from entities.py)
# ---------------------------------------------------------------------------

def _l_system_expand(axiom, rules, iters):
    s = axiom
    for _ in range(iters):
        s = "".join(rules.get(c, c) for c in s)
    return s


def _l_system_render(surf, cx, cy, instructions, angle_deg=22.5,
                     step=8, start_angle=-90, col_trunk=_TH_BROWN,
                     col_tip=_TH_GREEN, line_width=2):
    """Interpret L-system string as turtle graphics."""
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


# ---------------------------------------------------------------------------
# Unit draw functions (v10g2)
# ---------------------------------------------------------------------------

def draw_worker(surf, cx, cy, radius, rank=0, enemy=False):
    """Worker: rounded hexagon with self-similar inner hexes + black edges."""
    color = ENEMY_WORKER if enemy else WORKER_BLUE
    rotation = math.pi / 6

    pts = draw_polar_shape(surf, cx, cy, radius, color, hex_shape(4.0),
                           rotation=rotation)

    # v10g2: black edge for player, jagged overlay for enemy
    if enemy:
        def jagged(theta):
            base = hex_shape(4.0)(theta)
            return base * (1.0 + 0.08 * math.sin(17 * theta))
        draw_polar_shape(surf, cx, cy, radius * 1.05, (60, 15, 15),
                         jagged, rotation=rotation, width=2)
    elif pts and len(pts) >= 3:
        pygame.draw.polygon(surf, (0, 0, 0), pts, 2)

    if rank >= 1:
        inner_r = radius * 0.55
        inner_color = tuple(min(255, c + 40) for c in color)
        draw_polar_shape(surf, cx, cy, inner_r, inner_color, hex_shape(4.0),
                         rotation=rotation + 0.05, width=max(1, radius // 15))
    if rank >= 2:
        inner_r2 = radius * 0.3
        inner_color2 = tuple(min(255, c + 70) for c in color)
        draw_polar_shape(surf, cx, cy, inner_r2, inner_color2, hex_shape(4.0),
                         rotation=rotation + 0.10, width=max(1, radius // 15))


def draw_soldier(surf, cx, cy, radius, rank=0, enemy=False):
    """Soldier: v10g2 blade-like polar rose with black edges."""
    base_color = ENEMY_SOLDIER if enemy else SOLDIER_RED

    k_values = [1.5, 2.5, 3.5, 4.0, 5.0]
    k = k_values[min(rank, len(k_values) - 1)]

    # rank tint (player only)
    if not enemy:
        if rank >= 3:
            tint = RANK_COLORS[rank]
            color = tuple((a + b) // 2 for a, b in zip(base_color, tint))
        elif rank >= 1:
            tint = RANK_COLORS[rank]
            color = tuple((a * 3 + b) // 4 for a, b in zip(base_color, tint))
        else:
            color = base_color
    else:
        color = base_color

    rotation = -math.pi / 2

    # v10g2: blade_shape for sharp petal tips
    pts = draw_polar_shape(surf, cx, cy, radius, color, blade_shape(k),
                           rotation=rotation)

    # v10g2: black edge shading for player soldiers
    if not enemy and pts and len(pts) >= 3:
        pygame.draw.polygon(surf, (0, 0, 0), pts, 2)

    if rank >= 2:
        inner_k = k + 0.5
        inner_color = tuple(min(255, c + 50) for c in color)
        inner_pts = draw_polar_shape(surf, cx, cy, radius * 0.5, inner_color,
                                     blade_shape(inner_k), rotation=rotation)
        if not enemy and inner_pts and len(inner_pts) >= 3:
            pygame.draw.polygon(surf, (0, 0, 0), inner_pts, 1)

    if rank >= 3:
        pygame.draw.circle(surf, RANK_COLORS[rank], (int(cx), int(cy)),
                           max(2, radius // 6))

    # v10g2: rank pip removed

    if enemy:
        def jagged_blade(theta):
            base = blade_shape(k)(theta)
            return base * (1.0 + 0.12 * math.sin(13 * theta))
        draw_polar_shape(surf, cx, cy, radius * 1.08, (80, 10, 10),
                         jagged_blade, rotation=rotation, width=2)


def draw_archer(surf, cx, cy, radius, rank=0, enemy=False):
    """Archer: v10g2 enhanced golden spiral bow with filled body."""
    color = ENEMY_ARCHER if enemy else ARCHER_GREEN
    golden_spiral_bow(cx, cy, radius, surf, color, rank=rank, enemy=enemy)

    if enemy:
        n = 40
        pts = []
        for i in range(n):
            theta = 2 * math.pi * i / n
            r = radius * (0.85 + 0.08 * math.sin(11 * theta))
            pts.append((cx + r * math.cos(theta), cy + r * math.sin(theta)))
        pygame.draw.polygon(surf, (60, 10, 40), pts, 2)


def draw_siege(surf, cx, cy, radius, rank=0, enemy=True):
    """Siege unit: v10g2 dark spiked polygon."""
    n_spikes = 8
    color = ENEMY_SIEGE
    outer_r = radius * 0.95
    inner_r = radius * 0.50
    points = []
    for i in range(n_spikes * 2):
        theta = -math.pi / 2 + math.pi * i / n_spikes
        r = outer_r if i % 2 == 0 else inner_r
        x = cx + r * math.cos(theta)
        y = cy + r * math.sin(theta)
        points.append((x, y))
    if len(points) >= 3:
        pygame.draw.polygon(surf, color, points)

    # Inner filled circle
    pygame.draw.circle(surf, (25, 12, 5), (int(cx), int(cy)),
                       int(radius * 0.30))

    # Jagged enemy border
    n = 50
    border_pts = []
    for i in range(n):
        theta = 2 * math.pi * i / n
        r = radius * (1.02 + 0.06 * math.sin(14 * theta))
        border_pts.append((cx + r * math.cos(theta),
                           cy + r * math.sin(theta)))
    pygame.draw.polygon(surf, (60, 20, 5), border_pts, 2)


def draw_elite(surf, cx, cy, radius, rank=0, enemy=True):
    """Elite unit: v10g2 dark compound rose with purple accents."""
    color1 = ENEMY_ELITE
    color2 = (100, 30, 90)

    # Primary rose: 5-petal
    draw_polar_shape(surf, cx, cy, radius * 0.95, color1,
                     rose_shape(2.5), rotation=-math.pi / 2)

    # Secondary rose: 7-petal, smaller
    draw_polar_shape(surf, cx, cy, radius * 0.55, color2,
                     rose_shape(3.5), rotation=0)

    # Central glow -- muted
    pygame.draw.circle(surf, (180, 40, 140), (int(cx), int(cy)),
                       max(3, radius // 8))

    # Jagged enemy halo
    n = 50
    halo_pts = []
    for i in range(n):
        theta = 2 * math.pi * i / n
        r = radius * (1.05 + 0.07 * math.sin(9 * theta))
        halo_pts.append((cx + r * math.cos(theta),
                         cy + r * math.sin(theta)))
    pygame.draw.polygon(surf, (40, 5, 35), halo_pts, 2)


# ---------------------------------------------------------------------------
# v10_1: Building draw functions (VDD Phase 3)
# ---------------------------------------------------------------------------

def draw_town_hall(surf, cx, cy, size, **_kw):
    """L-system branching tree for Town Hall."""
    # dark foundation
    half = int(size * 0.45)
    foundation = pygame.Surface((half * 2, half * 2), pygame.SRCALPHA)
    foundation.fill((15, 15, 20, 80))
    surf.blit(foundation, (cx - half, cy - half))
    # tree grows from bottom center upward
    tree_y = cy + half - 4
    iters = 4
    instructions = _l_system_expand("F", {"F": "FF+[+F-F-F]-[-F+F+F]"}, iters)
    step = size / (3.0 * (1.5 ** iters))
    _l_system_render(surf, cx, tree_y, instructions, angle_deg=22.5,
                     step=step, col_trunk=_TH_BROWN, col_tip=_TH_GREEN,
                     line_width=max(1, 4 - iters))


def draw_barracks(surf, cx, cy, size, **_kw):
    """Sierpinski triangle lattice for Barracks."""
    # dark foundation
    half = int(size * 0.45)
    foundation = pygame.Surface((half * 2, half * 2), pygame.SRCALPHA)
    foundation.fill((15, 15, 20, 80))
    surf.blit(foundation, (cx - half, cy - half))
    color = _BK_MAROON
    depth = 4
    h_tri = half * math.sqrt(3)
    x1, y1 = cx, cy - h_tri * 0.6
    x2, y2 = cx - half, cy + h_tri * 0.4
    x3, y3 = cx + half, cy + h_tri * 0.4
    _sierpinski(surf, x1, y1, x2, y2, x3, y3, depth, color)
    border_c = tuple(min(255, c + 40) for c in color)
    pygame.draw.polygon(surf, border_c,
                        [(int(x1), int(y1)), (int(x2), int(y2)),
                         (int(x3), int(y3))], 2)


def draw_refinery(surf, cx, cy, size, **_kw):
    """Spirograph epitrochoid gear for Refinery."""
    # dark foundation
    half = int(size * 0.45)
    foundation = pygame.Surface((half * 2, half * 2), pygame.SRCALPHA)
    foundation.fill((15, 15, 20, 80))
    surf.blit(foundation, (cx - half, cy - half))
    color = _RF_GRAY
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
        pygame.draw.lines(surf, color, True, points, max(1, size // 40))
    # cusp highlights
    accent = _STEEL_BLUE
    step_pts = max(1, len(points) // 8)
    for i in range(0, len(points), step_pts):
        pygame.draw.circle(surf, accent,
                           (int(points[i][0]), int(points[i][1])),
                           max(2, size // 25))


def draw_tower(surf, cx, cy, size, level=1, **_kw):
    """Koch snowflake battlement for Tower."""
    # dark foundation
    half = int(size * 0.45)
    foundation = pygame.Surface((half * 2, half * 2), pygame.SRCALPHA)
    foundation.fill((15, 15, 20, 80))
    surf.blit(foundation, (cx - half, cy - half))
    depth = 3
    if level >= 2:
        depth = min(4, depth + 1)
    points = _koch_snowflake(cx, cy, size, depth)
    int_pts = [(int(p[0]), int(p[1])) for p in points]
    if len(int_pts) >= 3:
        fill = _TW_STONE if level == 1 else (180, 160, 120)
        pygame.draw.polygon(surf, fill, int_pts)
        border = (200, 200, 180) if level == 1 else _FORGE_ORANGE
        pygame.draw.polygon(surf, border, int_pts, max(1, size // 30))
    # Lv.2: orange glow dots on Koch tips
    if level >= 2 and len(points) > 10:
        step_pts = max(1, len(points) // 12)
        for i in range(0, len(points), step_pts):
            pygame.draw.circle(surf, _FORGE_ORANGE,
                               (int(points[i][0]), int(points[i][1])),
                               max(2, size // 20))


# ---------------------------------------------------------------------------
# Rendering logic
# ---------------------------------------------------------------------------

TILE = 128  # px per sample image
DRAW_RADIUS = 48  # shape radius inside the tile
BLDG_SIZE = 96    # building shape size inside the tile


def render_unit_png(draw_func, rank, enemy, filepath):
    """Render a single unit to a 128x128 transparent-background PNG."""
    surf = pygame.Surface((TILE, TILE), pygame.SRCALPHA)
    surf.fill((0, 0, 0, 0))
    cx, cy = TILE // 2, TILE // 2
    draw_func(surf, cx, cy, DRAW_RADIUS, rank=rank, enemy=enemy)
    pygame.image.save(surf, filepath)


def render_building_png(draw_func, filepath, **kwargs):
    """Render a single building to a 128x128 transparent-background PNG."""
    surf = pygame.Surface((TILE, TILE), pygame.SRCALPHA)
    surf.fill((0, 0, 0, 0))
    cx, cy = TILE // 2, TILE // 2
    draw_func(surf, cx, cy, BLDG_SIZE, **kwargs)
    pygame.image.save(surf, filepath)


def build_unit_list():
    """Return list of (filename, draw_func, rank, enemy) for every unit sample."""
    units = []

    # Worker: ranks 0, 1, 2 -- friendly and enemy
    for rank in range(3):
        for enemy, side in [(False, "friendly"), (True, "enemy")]:
            name = f"worker_{rank}_{side}.png"
            units.append((name, draw_worker, rank, enemy))

    # Soldier: ranks 0..4 -- friendly and enemy
    for rank in range(5):
        for enemy, side in [(False, "friendly"), (True, "enemy")]:
            name = f"soldier_{rank}_{side}.png"
            units.append((name, draw_soldier, rank, enemy))

    # Archer: ranks 0..4 -- friendly and enemy
    for rank in range(5):
        for enemy, side in [(False, "friendly"), (True, "enemy")]:
            name = f"archer_{rank}_{side}.png"
            units.append((name, draw_archer, rank, enemy))

    # Siege: enemy only, no ranks (use rank=0)
    units.append(("siege_0_enemy.png", draw_siege, 0, True))

    # Elite: enemy only, no ranks (use rank=0)
    units.append(("elite_0_enemy.png", draw_elite, 0, True))

    return units


def build_building_list():
    """Return list of (filename, draw_func, kwargs) for every building sample."""
    buildings = [
        ("building_town_hall.png", draw_town_hall, {}),
        ("building_barracks.png", draw_barracks, {}),
        ("building_refinery.png", draw_refinery, {}),
        ("building_tower_lv1.png", draw_tower, {"level": 1}),
        ("building_tower_lv2.png", draw_tower, {"level": 2}),
    ]
    return buildings


def generate_grid_sheet(units, buildings, out_dir):
    """Composite all individual PNGs into a labeled grid sheet."""
    total_items = len(units) + len(buildings)
    cols = 8
    rows = math.ceil(total_items / cols)
    label_h = 18
    cell_h = TILE + label_h
    sheet_w = cols * TILE
    sheet_h = rows * cell_h

    sheet = pygame.Surface((sheet_w, sheet_h), pygame.SRCALPHA)
    sheet.fill((20, 20, 30, 255))

    font = pygame.font.SysFont(None, 16)

    # Draw units
    for idx, (filename, draw_func, rank, enemy) in enumerate(units):
        col = idx % cols
        row = idx // cols
        x = col * TILE
        y = row * cell_h

        cx = x + TILE // 2
        cy = y + TILE // 2
        draw_func(sheet, cx, cy, DRAW_RADIUS, rank=rank, enemy=enemy)

        label = filename.replace(".png", "")
        lbl_surf = font.render(label, True, (180, 180, 200))
        lbl_x = x + (TILE - lbl_surf.get_width()) // 2
        lbl_y = y + TILE + 1
        sheet.blit(lbl_surf, (lbl_x, lbl_y))

    # Draw buildings (continue after units)
    offset = len(units)
    for bidx, (filename, draw_func, kwargs) in enumerate(buildings):
        idx = offset + bidx
        col = idx % cols
        row = idx // cols
        x = col * TILE
        y = row * cell_h

        cx = x + TILE // 2
        cy = y + TILE // 2
        draw_func(sheet, cx, cy, BLDG_SIZE, **kwargs)

        label = filename.replace(".png", "")
        lbl_surf = font.render(label, True, (180, 200, 180))
        lbl_x = x + (TILE - lbl_surf.get_width()) // 2
        lbl_y = y + TILE + 1
        sheet.blit(lbl_surf, (lbl_x, lbl_y))

    grid_path = os.path.join(out_dir, "all_entities.png")
    pygame.image.save(sheet, grid_path)
    return grid_path


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    out_dir = os.path.join(script_dir, "samples")
    os.makedirs(out_dir, exist_ok=True)

    units = build_unit_list()
    buildings = build_building_list()
    total = len(units) + len(buildings)

    print(f"Generating {total} entity samples in: {out_dir}")

    for i, (filename, draw_func, rank, enemy) in enumerate(units, 1):
        filepath = os.path.join(out_dir, filename)
        render_unit_png(draw_func, rank, enemy, filepath)
        print(f"  [{i:2d}/{total}] {filename}")

    for j, (filename, draw_func, kwargs) in enumerate(buildings, len(units) + 1):
        filepath = os.path.join(out_dir, filename)
        render_building_png(draw_func, filepath, **kwargs)
        print(f"  [{j:2d}/{total}] {filename}")

    # Combined grid sheet
    grid_path = generate_grid_sheet(units, buildings, out_dir)
    print(f"  Grid sheet -> {os.path.basename(grid_path)}")

    print("Done.")


if __name__ == "__main__":
    main()
