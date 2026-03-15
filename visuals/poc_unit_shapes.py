"""
Proof-of-concept: The Seven Voices — Chromatic Heptarchy Unit Shapes.

All 7 player tones + Dark 7 enemy mirrors rendered with polar equations:
  Do (1) Gatherer  — Superellipse hex
  Re (2) Soldier   — Blade-like polar rose
  Mi (3) Archer    — Golden spiral bow
  Fa (4) Shield    — Reuleaux constant-width curve
  Sol(5) Knight    — Cycloid rolling thunder
  La (6) Healer    — Gaussian bell envelope
  Ti (7) Sage      — Julia set boundary

Controls:
  LEFT/RIGHT  Change rank
  E           Toggle enemy (Dark 7) variants
  ESC         Quit
"""
import pygame
import math
import random
import sys

# --- Chromatic Heptarchy Palette (VDD Section 8) ---
COL_BG = (20, 20, 30)
BOUNDARY_WHITE = (240, 235, 220)

TONE_COLORS = {
    "gatherer": (50, 130, 220),
    "soldier":  (200, 60, 60),
    "archer":   (140, 100, 200),
    "shield":   (160, 150, 130),
    "knight":   (218, 165, 32),
    "healer":   (46, 139, 87),
    "sage":     (100, 50, 150),
}
TONE_ACCENTS = {
    "gatherer": (80, 180, 255),
    "soldier":  (255, 100, 80),
    "archer":   (180, 130, 255),
    "shield":   (200, 190, 170),
    "knight":   (255, 200, 60),
    "healer":   (80, 200, 120),
    "sage":     (150, 80, 220),
}
TONE_NAMES = {
    "gatherer": "Do (1)", "soldier": "Re (2)", "archer": "Mi (3)",
    "shield": "Fa (4)", "knight": "Sol (5)", "healer": "La (6)", "sage": "Ti (7)",
}
DARK7_COLORS = {
    "gatherer": (20, 80, 20),
    "soldier":  (80, 80, 100),
    "archer":   (140, 0, 140),
    "shield":   (90, 70, 40),
    "knight":   (140, 100, 20),
    "healer":   (55, 10, 15),
    "sage":     (40, 15, 60),
}
DARK7_NAMES = {
    "gatherer": "Blight Reaper", "soldier": "Hollow Warden",
    "archer": "Fade Ranger", "shield": "Ironbark",
    "knight": "Thornknight", "healer": "Bloodtithe", "sage": "Hexweaver",
}
RANK_COLORS = {
    0: (140, 140, 140), 1: (205, 127, 50), 2: (192, 192, 210),
    3: (255, 215, 0), 4: (80, 180, 255),
}
RANK_NAMES = ["Recruit", "Veteran", "Corporal", "Sergeant", "Captain"]
WORKER_RANK_NAMES = ["Novice", "Foreman", "Master"]


# --- Shape helpers ---
def draw_polar_shape(surf, cx, cy, radius, color, r_func, n_points=120,
                     width=0, rotation=0.0):
    points = []
    for i in range(n_points):
        theta = rotation + 2 * math.pi * i / n_points
        r = r_func(theta) * radius
        points.append((cx + r * math.cos(theta), cy + r * math.sin(theta)))
    if len(points) >= 3:
        if width == 0:
            pygame.draw.polygon(surf, color, points)
        else:
            pygame.draw.polygon(surf, color, points, width)
    return points


def hex_shape(n=4.0):
    def r_func(theta):
        ct, st = abs(math.cos(theta)), abs(math.sin(theta))
        d = (ct ** n + st ** n)
        return 1.0 / (d ** (1.0 / n)) if d > 1e-10 else 1.0
    return r_func


def blade_shape(k, sharpness=0.6):
    def r_func(theta):
        v = abs(math.cos(k * theta))
        return v ** sharpness if v > 1e-10 else 0.0
    return r_func


def reuleaux_shape(n_sides=3):
    def r_func(theta):
        t = theta % (2 * math.pi / n_sides)
        half = math.pi / n_sides
        d = math.cos(half)
        return max(0.3, min(1.0, math.cos(t - half) / d)) if d > 1e-10 else 1.0
    return r_func


def cycloid_shape(n_lobes=3):
    def r_func(theta):
        return 0.6 + 0.4 * abs(math.cos(n_lobes * theta / 2))
    return r_func


def gaussian_shape(sigma=0.4):
    def r_func(theta):
        diff = ((theta + math.pi) % (2 * math.pi)) - math.pi
        return 0.5 + 0.5 * math.exp(-diff * diff / (2 * sigma * sigma))
    return r_func


def julia_boundary_shape(c_real=-0.7269, c_imag=0.1889, max_iter=20):
    def r_func(theta):
        z_r, z_i = 0.8 * math.cos(theta), 0.8 * math.sin(theta)
        for i in range(max_iter):
            zr2 = z_r * z_r - z_i * z_i + c_real
            zi2 = 2 * z_r * z_i + c_imag
            z_r, z_i = zr2, zi2
            if z_r * z_r + z_i * z_i > 4:
                return 0.3 + 0.7 * (i / max_iter)
        return 0.4
    return r_func


# --- Unit draw functions ---
def draw_gatherer(surf, cx, cy, radius, rank=0, enemy=False):
    color = DARK7_COLORS["gatherer"] if enemy else TONE_COLORS["gatherer"]
    rot = math.pi / 6
    pts = draw_polar_shape(surf, cx, cy, radius, color, hex_shape(4.0), rotation=rot)
    if enemy:
        def jagged(t): return hex_shape(4.0)(t) * (1.0 + 0.08 * math.sin(17 * t))
        draw_polar_shape(surf, cx, cy, radius * 1.05, (40, 100, 30), jagged, rotation=rot, width=2)
    elif pts and len(pts) >= 3:
        pygame.draw.polygon(surf, (0, 0, 0), pts, 2)
    if rank >= 1:
        draw_polar_shape(surf, cx, cy, radius * 0.55, tuple(min(255, c + 40) for c in color),
                         hex_shape(4.0), rotation=rot + 0.05, width=max(1, radius // 15))
    if rank >= 2:
        draw_polar_shape(surf, cx, cy, radius * 0.3, tuple(min(255, c + 70) for c in color),
                         hex_shape(4.0), rotation=rot + 0.10, width=max(1, radius // 15))


def draw_soldier(surf, cx, cy, radius, rank=0, enemy=False):
    color = DARK7_COLORS["soldier"] if enemy else TONE_COLORS["soldier"]
    k_values = [1.5, 2.5, 3.5, 4.0, 5.0]
    k = k_values[min(rank, len(k_values) - 1)]
    if not enemy and rank >= 1:
        tint = RANK_COLORS.get(rank, (140, 140, 140))
        blend = 2 if rank >= 3 else 4
        color = tuple((a * (blend - 1) + b) // blend for a, b in zip(color, tint))
    rot = -math.pi / 2
    pts = draw_polar_shape(surf, cx, cy, radius, color, blade_shape(k), rotation=rot)
    if not enemy and pts and len(pts) >= 3:
        pygame.draw.polygon(surf, (0, 0, 0), pts, 2)
    if rank >= 2:
        draw_polar_shape(surf, cx, cy, radius * 0.5, tuple(min(255, c + 50) for c in color),
                         blade_shape(k + 0.5), rotation=rot)
    if rank >= 3:
        pygame.draw.circle(surf, RANK_COLORS[rank], (int(cx), int(cy)), max(2, radius // 6))
    if enemy:
        def jag(t): return blade_shape(k)(t) * (1.0 + 0.12 * math.sin(13 * t))
        draw_polar_shape(surf, cx, cy, radius * 1.08, (100, 95, 115), jag, rotation=rot, width=2)


def draw_archer(surf, cx, cy, radius, rank=0, enemy=False):
    color = DARK7_COLORS["archer"] if enemy else TONE_COLORS["archer"]
    phi = (1 + math.sqrt(5)) / 2
    b = math.log(phi) / (math.pi / 2)
    top_pts, bot_pts = [], []
    for i in range(60):
        theta = math.pi * 0.1 + (math.pi * 1.3) * i / 59
        r = 0.3 * math.exp(b * theta) * radius / 3.0
        x = cx + r * math.cos(theta) * 0.5
        top_pts.append((x, cy - r * math.sin(theta) * 0.7))
        bot_pts.append((x, cy + r * math.sin(theta) * 0.7))
    bow_polygon = top_pts + bot_pts[::-1]
    if len(bow_polygon) >= 3:
        pygame.draw.polygon(surf, tuple(max(0, c - 40) for c in color), bow_polygon)
        pygame.draw.polygon(surf, color, bow_polygon, 2)
    if not enemy:
        for pts_list in [top_pts, bot_pts]:
            if len(pts_list) >= 2:
                pygame.draw.lines(surf, (0, 0, 0), False, pts_list, max(4, radius // 10))
    for pts_list in [top_pts, bot_pts]:
        if len(pts_list) >= 2:
            pygame.draw.lines(surf, color, False, pts_list, max(3, radius // 12))
    pygame.draw.line(surf, color, (cx - radius * 0.1, cy - radius * 0.65),
                     (cx - radius * 0.1, cy + radius * 0.65), max(1, radius // 30))
    pygame.draw.line(surf, BOUNDARY_WHITE, (cx - radius * 0.3, cy),
                     (cx + radius * 0.8, cy), max(1, radius // 25))
    hs = radius * 0.12
    pygame.draw.polygon(surf, BOUNDARY_WHITE, [
        (cx + radius * 0.8, cy), (cx + radius * 0.8 - hs, cy - hs * 0.6),
        (cx + radius * 0.8 - hs, cy + hs * 0.6)])
    if rank >= 1:
        fib_angles = [0.5, 0.8, 1.1, 1.4, 1.8]
        for i in range(min(rank + 1, len(fib_angles))):
            theta = math.pi * 0.1 + fib_angles[i]
            r = 0.3 * math.exp(b * theta) * radius / 3.0
            for m in [1, -1]:
                pygame.draw.circle(surf, TONE_ACCENTS["archer"],
                                   (int(cx + r * math.cos(theta) * 0.5),
                                    int(cy + m * r * math.sin(theta) * 0.7)),
                                   max(2, radius // 15))
    if enemy:
        n = 40
        pts = [(cx + radius * (0.85 + 0.08 * math.sin(11 * (2 * math.pi * i / n))) * math.cos(2 * math.pi * i / n),
                cy + radius * (0.85 + 0.08 * math.sin(11 * (2 * math.pi * i / n))) * math.sin(2 * math.pi * i / n))
               for i in range(n)]
        pygame.draw.polygon(surf, (160, 0, 160), pts, 2)


def draw_shield(surf, cx, cy, radius, rank=0, enemy=False):
    color = DARK7_COLORS["shield"] if enemy else TONE_COLORS["shield"]
    n_sides = 3 + min(rank, 2)
    pts = draw_polar_shape(surf, cx, cy, radius * 0.9, color, reuleaux_shape(n_sides),
                           n_points=180, rotation=-math.pi / 2)
    if not enemy and pts and len(pts) >= 3:
        pygame.draw.polygon(surf, (0, 0, 0), pts, 2)
    if rank >= 1:
        draw_polar_shape(surf, cx, cy, radius * 0.55, tuple(min(255, c + 30) for c in color),
                         reuleaux_shape(n_sides), n_points=180, rotation=-math.pi / 2,
                         width=max(1, radius // 12))
    rng = random.Random(42)
    for _ in range(5 + rank * 2):
        a, d = rng.uniform(0, 2 * math.pi), rng.uniform(0.1, 0.5) * radius
        pygame.draw.circle(surf, tuple(min(255, c + 20) for c in color),
                           (int(cx + d * math.cos(a)), int(cy + d * math.sin(a))),
                           max(1, radius // 20))
    if enemy:
        def jag(t): return reuleaux_shape(n_sides)(t) * (1.0 + 0.10 * math.sin(11 * t))
        draw_polar_shape(surf, cx, cy, radius * 0.95, (110, 85, 50), jag,
                         n_points=180, rotation=-math.pi / 2, width=2)


def draw_knight(surf, cx, cy, radius, rank=0, enemy=False):
    color = DARK7_COLORS["knight"] if enemy else TONE_COLORS["knight"]
    n_lobes = 3 + min(rank, 3)
    pts = draw_polar_shape(surf, cx, cy, radius * 0.95, color, cycloid_shape(n_lobes),
                           n_points=150, rotation=-math.pi / 2)
    if not enemy and pts and len(pts) >= 3:
        pygame.draw.polygon(surf, (0, 0, 0), pts, 2)
    streak_c = TONE_ACCENTS["knight"] if not enemy else (170, 120, 30)
    for i in range(n_lobes):
        a = -math.pi / 2 + 2 * math.pi * i / n_lobes
        pygame.draw.line(surf, streak_c, (int(cx + radius * 0.2 * math.cos(a)),
                         int(cy + radius * 0.2 * math.sin(a))),
                         (int(cx + radius * 0.7 * math.cos(a)),
                         int(cy + radius * 0.7 * math.sin(a))), max(1, radius // 20))
    if rank >= 2:
        pygame.draw.circle(surf, TONE_ACCENTS["knight"], (int(cx), int(cy)), max(2, radius // 5))
    if enemy:
        def jag(t): return cycloid_shape(n_lobes)(t) * (1.0 + 0.08 * math.sin(15 * t))
        draw_polar_shape(surf, cx, cy, radius, (160, 115, 25), jag,
                         n_points=150, rotation=-math.pi / 2, width=2)


def draw_healer(surf, cx, cy, radius, rank=0, enemy=False):
    color = DARK7_COLORS["healer"] if enemy else TONE_COLORS["healer"]
    sigma = 0.4 + rank * 0.08
    pts = draw_polar_shape(surf, cx, cy, radius * 0.9, color, gaussian_shape(sigma),
                           n_points=120, rotation=-math.pi / 2)
    if not enemy and pts and len(pts) >= 3:
        pygame.draw.polygon(surf, (0, 0, 0), pts, 2)
    ring_c = TONE_ACCENTS["healer"] if not enemy else (80, 15, 20)
    for r_i in range(1 + min(rank, 3)):
        pygame.draw.circle(surf, ring_c, (int(cx), int(cy)),
                           int(radius * (0.3 + r_i * 0.18)), max(1, radius // 25))
    cross_c = tuple(min(255, c + 60) for c in color)
    for angle in [0, math.pi / 2]:
        pts_line = [(int(cx + (-0.6 + 1.2 * i / 19) * radius * 0.6 * math.cos(angle) -
                         math.sin((-0.6 + 1.2 * i / 19) * 6) * 3 * math.sin(angle)),
                     int(cy + (-0.6 + 1.2 * i / 19) * radius * 0.6 * math.sin(angle) +
                         math.sin((-0.6 + 1.2 * i / 19) * 6) * 3 * math.cos(angle)))
                    for i in range(20)]
        if len(pts_line) >= 2:
            pygame.draw.lines(surf, cross_c, False, pts_line, max(1, radius // 20))
    if enemy:
        def jag(t): return gaussian_shape(sigma)(t) * (1.0 + 0.10 * math.sin(13 * t))
        draw_polar_shape(surf, cx, cy, radius * 0.95, (75, 15, 20), jag,
                         n_points=120, rotation=-math.pi / 2, width=2)


def draw_sage(surf, cx, cy, radius, rank=0, enemy=False):
    color = DARK7_COLORS["sage"] if enemy else TONE_COLORS["sage"]
    c_values = [(-0.7269, 0.1889), (-0.8, 0.156), (-0.4, 0.6),
                (-0.835, -0.2321), (-0.70176, -0.3842)]
    c_r, c_i = c_values[min(rank, len(c_values) - 1)]
    mi = 15 + rank * 5
    pts = draw_polar_shape(surf, cx, cy, radius * 0.9, color,
                           julia_boundary_shape(c_r, c_i, mi), n_points=200)
    if not enemy and pts and len(pts) >= 3:
        pygame.draw.polygon(surf, (0, 0, 0), pts, 2)
    if rank >= 1:
        c_r2, c_i2 = c_values[min(rank - 1, len(c_values) - 1)]
        ic = TONE_ACCENTS["sage"] if not enemy else (60, 20, 80)
        draw_polar_shape(surf, cx, cy, radius * 0.45, ic,
                         julia_boundary_shape(c_r2, c_i2, mi - 5),
                         n_points=150, rotation=0.3, width=max(1, radius // 15))
    pygame.draw.circle(surf, (10, 8, 25), (int(cx), int(cy)), max(2, radius // 8))
    gc = TONE_ACCENTS["sage"] if not enemy else (60, 20, 80)
    pygame.draw.circle(surf, gc, (int(cx), int(cy)), max(3, radius // 6), 1)
    if enemy:
        def jag(t): return julia_boundary_shape(c_r, c_i, mi)(t) * (1.0 + 0.15 * math.sin(17 * t))
        draw_polar_shape(surf, cx, cy, radius * 0.95, (55, 20, 80), jag, n_points=200, width=2)


# --- Main interactive window ---
TONE_ORDER = ["gatherer", "soldier", "archer", "shield", "knight", "healer", "sage"]
DRAW_FUNCS = {
    "gatherer": draw_gatherer, "soldier": draw_soldier, "archer": draw_archer,
    "shield": draw_shield, "knight": draw_knight, "healer": draw_healer,
    "sage": draw_sage,
}
MAX_RANKS = {"gatherer": 2, "soldier": 4, "archer": 4, "shield": 2,
             "knight": 3, "healer": 2, "sage": 4}


def main():
    pygame.init()
    W, H = 1400, 780
    screen = pygame.display.set_mode((W, H))
    pygame.display.set_caption("VDD PoC: The Seven Voices — Chromatic Heptarchy")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont(None, 22)
    font_lg = pygame.font.SysFont(None, 30)
    font_sm = pygame.font.SysFont(None, 16)

    current_rank = 0
    show_enemy = False

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_RIGHT:
                    current_rank = min(4, current_rank + 1)
                elif event.key == pygame.K_LEFT:
                    current_rank = max(0, current_rank - 1)
                elif event.key == pygame.K_e:
                    show_enemy = not show_enemy

        screen.fill(COL_BG)

        # Title
        title = "The Seven Voices — Chromatic Heptarchy"
        ts = font_lg.render(title, True, (220, 220, 220))
        screen.blit(ts, (W // 2 - ts.get_width() // 2, 12))

        subtitle = "LEFT/RIGHT: Rank  |  E: Dark 7 variants  |  ESC: Quit"
        ss = font_sm.render(subtitle, True, (100, 100, 120))
        screen.blit(ss, (W // 2 - ss.get_width() // 2, 44))

        # Draw 7 columns
        col_w = W // 7
        sizes = [25, 45, 75]

        for col_idx, tone in enumerate(TONE_ORDER):
            base_x = col_idx * col_w + col_w // 2
            draw_func = DRAW_FUNCS[tone]
            rank = min(current_rank, MAX_RANKS[tone])
            color = TONE_COLORS[tone]

            # Column header: tone name + musical note
            header = f"{tone.upper()}"
            hs = font.render(header, True, color)
            screen.blit(hs, (base_x - hs.get_width() // 2, 70))

            tone_label = TONE_NAMES[tone]
            tl = font_sm.render(tone_label, True, tuple(min(255, c + 40) for c in color))
            screen.blit(tl, (base_x - tl.get_width() // 2, 92))

            rank_text = f"Rank {rank}"
            if tone == "gatherer":
                rank_text = WORKER_RANK_NAMES[min(rank, 2)]
            else:
                rank_text = RANK_NAMES[min(rank, 4)]
            rt = font_sm.render(rank_text, True, RANK_COLORS.get(rank, (140, 140, 140)))
            screen.blit(rt, (base_x - rt.get_width() // 2, 108))

            # Draw at multiple sizes
            y = 140
            for si, size in enumerate(sizes):
                # Player version
                px = base_x - (55 if show_enemy else 0)
                draw_func(screen, px, y + size, size, rank=rank, enemy=False)

                if show_enemy:
                    ex = base_x + 55
                    draw_func(screen, ex, y + size, size, rank=rank, enemy=True)

                y += size * 2 + 20

            # Dark 7 name (when enemy shown)
            if show_enemy:
                d7name = DARK7_NAMES[tone]
                d7_color = DARK7_COLORS[tone]
                d7s = font_sm.render(d7name, True, tuple(min(255, c + 60) for c in d7_color))
                screen.blit(d7s, (base_x - d7s.get_width() // 2, y + 5))

        # Color swatches at bottom
        swatch_y = H - 55
        swatch_size = 18
        for i, tone in enumerate(TONE_ORDER):
            sx = 30 + i * (swatch_size + 80)
            # Player swatch
            pygame.draw.rect(screen, TONE_COLORS[tone],
                             (sx, swatch_y, swatch_size, swatch_size))
            pygame.draw.rect(screen, (255, 255, 255),
                             (sx, swatch_y, swatch_size, swatch_size), 1)
            label = font_sm.render(tone[:4], True, TONE_COLORS[tone])
            screen.blit(label, (sx + swatch_size + 4, swatch_y + 1))

            if show_enemy:
                pygame.draw.rect(screen, DARK7_COLORS[tone],
                                 (sx, swatch_y + swatch_size + 4, swatch_size, swatch_size))
                pygame.draw.rect(screen, (80, 80, 80),
                                 (sx, swatch_y + swatch_size + 4, swatch_size, swatch_size), 1)

        # Rank indicator
        rc = RANK_COLORS.get(current_rank, (140, 140, 140))
        pygame.draw.circle(screen, rc, (W - 40, 30), 12)

        pygame.display.flip()
        clock.tick(30)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
