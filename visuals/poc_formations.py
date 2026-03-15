"""
Proof-of-concept: Harmonic Formations & Sentinel Lattice.

Demonstrates the VDD's formation visual language:
  - Rose formation (soldiers in polar rose arrangement)
  - Spiral formation (golden spiral positioning)
  - Koch formation (snowflake perimeter)
  - Sierpinski formation (triangle lattice)
  - Sentinel Lattice (D1-D6 dihedral symmetry progression)
  - Formation auras and spring connections
  - Harmony quality color spectrum

Controls:
  1-4      Select formation type (Rose/Spiral/Koch/Sierpinski)
  S        Cycle Sentinel symmetry order (D1→D2→D3→D4→D6)
  H        Cycle harmony quality (weak→thin→rich→perfect)
  +/-      Add/remove units from formation
  A        Toggle formation aura
  ESC      Quit
"""
import pygame
import math
import random
import sys

# --- Palette ---
COL_BG = (20, 20, 30)
EARTH_GOLD = (218, 165, 32)
BOUNDARY_WHITE = (240, 235, 220)
GHOST_STONE = (80, 75, 60)
SENTINEL_STONE = (140, 130, 100)

TONE_COLORS = {
    "gatherer": (50, 130, 220), "soldier": (200, 60, 60),
    "archer": (140, 100, 200), "shield": (160, 150, 130),
    "knight": (218, 165, 32), "healer": (46, 139, 87),
    "sage": (100, 50, 150),
}

# Harmony quality colors (VDD 8.4)
HARMONY_COLORS = {
    "weak": (120, 80, 80),
    "thin": (160, 160, 140),
    "rich": (180, 160, 255),
    "perfect": (255, 230, 80),
}


def draw_polar_shape(surf, cx, cy, radius, color, r_func, n_points=80,
                     rotation=0.0, width=0):
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


def blade_r(k, s=0.6):
    def f(t):
        v = abs(math.cos(k * t))
        return v ** s if v > 1e-10 else 0.0
    return f


def hex_r(t):
    ct, st = abs(math.cos(t)), abs(math.sin(t))
    d = ct ** 4 + st ** 4
    return 1.0 / (d ** 0.25) if d > 1e-10 else 1.0


def reuleaux_r(t):
    t2 = t % (2 * math.pi / 3)
    half = math.pi / 3
    d = math.cos(half)
    return max(0.3, min(1.0, math.cos(t2 - half) / d)) if d > 0.01 else 1.0


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


def koch_snowflake(cx, cy, size, depth):
    r = size * 0.45
    angles = [math.pi / 2, math.pi / 2 + 2 * math.pi / 3,
              math.pi / 2 + 4 * math.pi / 3]
    verts = [(cx + r * math.cos(a), cy - r * math.sin(a)) for a in angles]
    all_pts = []
    for i in range(3):
        all_pts.extend(koch_pts(*verts[i], *verts[(i + 1) % 3], depth))
    return all_pts


def sierpinski_pts(x1, y1, x2, y2, x3, y3, depth):
    """Return vertex positions for Sierpinski formation slots."""
    if depth == 0:
        cx = (x1 + x2 + x3) / 3
        cy = (y1 + y2 + y3) / 3
        return [(cx, cy)]
    mx1, my1 = (x1 + x2) / 2, (y1 + y2) / 2
    mx2, my2 = (x2 + x3) / 2, (y2 + y3) / 2
    mx3, my3 = (x1 + x3) / 2, (y1 + y3) / 2
    pts = []
    pts.extend(sierpinski_pts(x1, y1, mx1, my1, mx3, my3, depth - 1))
    pts.extend(sierpinski_pts(mx1, my1, x2, y2, mx2, my2, depth - 1))
    pts.extend(sierpinski_pts(mx3, my3, mx2, my2, x3, y3, depth - 1))
    return pts


def draw_unit_at(surf, x, y, tone, size=12):
    """Draw a small unit shape by tone."""
    color = TONE_COLORS.get(tone, (200, 200, 200))
    if tone == "gatherer":
        draw_polar_shape(surf, x, y, size, color, hex_r, rotation=math.pi / 6)
    elif tone == "soldier":
        draw_polar_shape(surf, x, y, size, color, blade_r(2.5), rotation=-math.pi / 2)
    elif tone == "archer":
        pygame.draw.arc(surf, color, (int(x - size * 0.6), int(y - size * 0.8),
                        int(size * 1.2), int(size * 1.6)), -1, 1, 2)
        pygame.draw.line(surf, color, (int(x - size * 0.2), int(y - size * 0.7)),
                         (int(x - size * 0.2), int(y + size * 0.7)), 1)
    elif tone == "shield":
        draw_polar_shape(surf, x, y, size, color, reuleaux_r, n_points=60, rotation=-math.pi / 2)
    elif tone == "knight":
        draw_polar_shape(surf, x, y, size, color,
                         lambda t: 0.6 + 0.4 * abs(math.cos(1.5 * t)),
                         rotation=-math.pi / 2)
    elif tone == "healer":
        pygame.draw.circle(surf, color, (int(x), int(y)), size - 2)
        pygame.draw.circle(surf, tuple(min(255, c + 40) for c in color),
                           (int(x), int(y)), size - 2, 1)
    elif tone == "sage":
        draw_polar_shape(surf, x, y, size, color,
                         lambda t: 0.5 + 0.3 * math.sin(5 * t + 0.7 * math.cos(3 * t)),
                         n_points=60)
    # Outline
    pygame.draw.circle(surf, (0, 0, 0), (int(x), int(y)), size, 1)


def draw_sentinel(surf, cx, cy, size=24):
    """Draw a Sentinel standing stone."""
    w = int(size * 0.35)
    h = int(size * 0.7)
    body = [(cx - w, cy + h // 2), (cx - w * 2 // 3, cy - h // 3),
            (cx, cy - h // 2), (cx + w * 2 // 3, cy - h // 3),
            (cx + w, cy + h // 2)]
    pygame.draw.polygon(surf, SENTINEL_STONE, body)
    pygame.draw.polygon(surf, (0, 0, 0), body, 1)
    # Voronoi dots
    rng = random.Random(hash((cx, cy)) % 10000)
    for _ in range(4):
        dx = rng.randint(-w + 2, w - 2)
        dy = rng.randint(-h // 3, h // 3)
        pygame.draw.circle(surf, tuple(c + rng.randint(-10, 10) for c in SENTINEL_STONE),
                           (cx + dx, cy + dy), 1)
    # Aura
    aura = pygame.Surface((size * 2, size * 2), pygame.SRCALPHA)
    pygame.draw.circle(aura, (*EARTH_GOLD, 18), (size, size), size - 2)
    surf.blit(aura, (cx - size, cy - size))


def draw_koch_rect(surf, rect, depth, color, width=1):
    x, y, w, h = rect
    corners = [(x, y), (x + w, y), (x + w, y + h), (x, y + h)]
    for i in range(4):
        pts = koch_pts(*corners[i], *corners[(i + 1) % 4], depth)
        pts.append(corners[(i + 1) % 4])
        int_pts = [(int(p[0]), int(p[1])) for p in pts]
        if len(int_pts) >= 2:
            pygame.draw.lines(surf, color, False, int_pts, width)


def main():
    pygame.init()
    W, H = 1280, 720
    screen = pygame.display.set_mode((W, H))
    pygame.display.set_caption("VDD PoC: Harmonic Formations & Sentinel Lattice")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont(None, 24)
    font_lg = pygame.font.SysFont(None, 32)
    font_sm = pygame.font.SysFont(None, 18)

    formation_type = 0  # 0=Rose, 1=Spiral, 2=Koch, 3=Sierpinski
    formation_names = ["Rose", "Golden Spiral", "Koch Snowflake", "Sierpinski"]
    sentinel_order = 0  # 0=D1(2), 1=D2(4), 2=D3(6), 3=D4(8), 4=D6(12)
    sentinel_configs = [
        ("D1", 2), ("D2", 4), ("D3", 6), ("D4", 8), ("D6", 12)
    ]
    harmony_idx = 2  # 0=weak, 1=thin, 2=rich, 3=perfect
    harmony_names = ["weak", "thin", "rich", "perfect"]
    n_units = 7
    show_aura = True
    game_time = 0.0

    running = True
    while running:
        dt = clock.tick(30) / 1000.0
        game_time += dt

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key in (pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4):
                    formation_type = event.key - pygame.K_1
                elif event.key == pygame.K_s:
                    sentinel_order = (sentinel_order + 1) % len(sentinel_configs)
                elif event.key == pygame.K_h:
                    harmony_idx = (harmony_idx + 1) % 4
                elif event.key in (pygame.K_EQUALS, pygame.K_PLUS):
                    n_units = min(15, n_units + 1)
                elif event.key == pygame.K_MINUS:
                    n_units = max(3, n_units - 1)
                elif event.key == pygame.K_a:
                    show_aura = not show_aura

        screen.fill(COL_BG)

        # === LEFT HALF: Formation ===
        form_cx, form_cy = W // 4, H // 2
        form_r = 160

        harmony = harmony_names[harmony_idx]
        harmony_color = HARMONY_COLORS[harmony]

        # Title
        title = f"{formation_names[formation_type]} Formation"
        ts = font_lg.render(title, True, harmony_color)
        screen.blit(ts, (form_cx - ts.get_width() // 2, 30))

        info = f"Units: {n_units}  |  Harmony: {harmony.upper()} ({[40, 65, 85, 97][harmony_idx]}%)"
        inf = font.render(info, True, (160, 160, 180))
        screen.blit(inf, (form_cx - inf.get_width() // 2, 65))

        # Compute unit positions
        positions = []
        tones = ["soldier", "archer", "soldier", "shield", "knight",
                 "soldier", "archer", "healer", "soldier", "archer",
                 "shield", "knight", "sage", "healer", "soldier"]

        if formation_type == 0:  # Rose
            for i in range(n_units):
                angle = 2 * math.pi * i / n_units - math.pi / 2 + game_time * 0.1
                r = form_r * 0.6
                positions.append((form_cx + r * math.cos(angle),
                                  form_cy + r * math.sin(angle)))
        elif formation_type == 1:  # Golden Spiral
            phi = (1 + math.sqrt(5)) / 2
            for i in range(n_units):
                angle = i * 2 * math.pi / phi + game_time * 0.05
                r = form_r * 0.12 * math.sqrt(i + 1)
                positions.append((form_cx + r * math.cos(angle),
                                  form_cy + r * math.sin(angle)))
        elif formation_type == 2:  # Koch
            snow_pts = koch_snowflake(form_cx, form_cy, form_r * 1.5, 2)
            step = max(1, len(snow_pts) // n_units)
            for i in range(n_units):
                idx = min(i * step, len(snow_pts) - 1)
                positions.append(snow_pts[idx])
        elif formation_type == 3:  # Sierpinski
            h_tri = form_r * math.sqrt(3) * 0.8
            x1, y1 = form_cx, form_cy - h_tri * 0.6
            x2, y2 = form_cx - form_r * 0.8, form_cy + h_tri * 0.4
            x3, y3 = form_cx + form_r * 0.8, form_cy + h_tri * 0.4
            depth = 2 if n_units > 6 else 1
            slot_pts = sierpinski_pts(x1, y1, x2, y2, x3, y3, depth)
            for i in range(min(n_units, len(slot_pts))):
                positions.append(slot_pts[i])

        # Formation aura
        if show_aura and len(positions) >= 3:
            aura_surf = pygame.Surface((W, H), pygame.SRCALPHA)
            alpha = [15, 20, 30, 50][harmony_idx]

            if formation_type == 0:  # Rose aura
                pts = []
                for i in range(120):
                    theta = 2 * math.pi * i / 120 + game_time * 0.2
                    r = form_r * 0.75 * abs(math.cos(2.5 * theta))
                    pts.append((int(form_cx + r * math.cos(theta)),
                                int(form_cy + r * math.sin(theta))))
                if len(pts) >= 3:
                    pygame.draw.polygon(aura_surf, (*harmony_color, alpha), pts)
                    pygame.draw.polygon(aura_surf, (*harmony_color, alpha + 30), pts, 1)

            elif formation_type == 1:  # Spiral aura
                spiral_pts = []
                for i in range(80):
                    t = i * 0.12
                    r = form_r * 0.04 * t
                    spiral_pts.append((int(form_cx + r * math.cos(t + game_time * 0.3)),
                                       int(form_cy + r * math.sin(t + game_time * 0.3))))
                if len(spiral_pts) >= 2:
                    pygame.draw.lines(aura_surf, (*harmony_color, alpha + 30),
                                      False, spiral_pts, 2)

            elif formation_type == 2:  # Koch aura
                snow = koch_snowflake(form_cx, form_cy, form_r * 1.5, 2)
                int_snow = [(int(p[0]), int(p[1])) for p in snow]
                if len(int_snow) >= 3:
                    pygame.draw.polygon(aura_surf, (*harmony_color, alpha), int_snow)
                    pygame.draw.polygon(aura_surf, (*harmony_color, alpha + 20), int_snow, 1)

            elif formation_type == 3:  # Sierpinski aura
                h_tri = form_r * math.sqrt(3) * 0.8
                tri = [(int(form_cx), int(form_cy - h_tri * 0.6)),
                       (int(form_cx - form_r * 0.8), int(form_cy + h_tri * 0.4)),
                       (int(form_cx + form_r * 0.8), int(form_cy + h_tri * 0.4))]
                pygame.draw.polygon(aura_surf, (*harmony_color, alpha), tri)
                pygame.draw.polygon(aura_surf, (*harmony_color, alpha + 20), tri, 1)

            screen.blit(aura_surf, (0, 0))

        # Spring connections
        if show_aura:
            spring_surf = pygame.Surface((W, H), pygame.SRCALPHA)
            spring_alpha = [10, 20, 35, 60][harmony_idx]
            for i in range(len(positions)):
                for j in range(i + 1, len(positions)):
                    dist = math.sqrt((positions[i][0] - positions[j][0]) ** 2 +
                                     (positions[i][1] - positions[j][1]) ** 2)
                    if dist < form_r * 1.2:
                        pygame.draw.line(spring_surf, (*harmony_color, spring_alpha),
                                         (int(positions[i][0]), int(positions[i][1])),
                                         (int(positions[j][0]), int(positions[j][1])), 1)
            screen.blit(spring_surf, (0, 0))

        # Draw units
        for i, pos in enumerate(positions):
            tone = tones[i % len(tones)]
            draw_unit_at(screen, pos[0], pos[1], tone, size=14)

        # === RIGHT HALF: Sentinel Lattice ===
        sent_cx, sent_cy = 3 * W // 4, H // 2
        sent_name, sent_count = sentinel_configs[sentinel_order]
        sent_r = 150

        # Title
        st_title = f"Sentinel Lattice — {sent_name} ({sent_count} Sentinels)"
        st = font_lg.render(st_title, True, EARTH_GOLD)
        screen.blit(st, (sent_cx - st.get_width() // 2, 30))

        # Sentinel positions
        sentinel_positions = []
        for i in range(sent_count):
            angle = 2 * math.pi * i / sent_count - math.pi / 2
            sx = sent_cx + sent_r * 0.7 * math.cos(angle)
            sy = sent_cy + sent_r * 0.7 * math.sin(angle)
            sentinel_positions.append((sx, sy))

        # Symmetry axes (gold lines through center)
        n_axes = sent_count // 2
        for i in range(n_axes):
            p1 = sentinel_positions[i]
            opposite = (i + sent_count // 2) % sent_count
            p2 = sentinel_positions[opposite]
            pygame.draw.line(screen, EARTH_GOLD,
                             (int(p1[0]), int(p1[1])),
                             (int(p2[0]), int(p2[1])), 1)

        # Interior fill zone
        if sent_count >= 3:
            fill_surf = pygame.Surface((W, H), pygame.SRCALPHA)
            hex_pts = [(int(p[0]), int(p[1])) for p in sentinel_positions]
            pygame.draw.polygon(fill_surf, (*EARTH_GOLD, 12), hex_pts)
            screen.blit(fill_surf, (0, 0))

        # Draw Sentinels
        for sx, sy in sentinel_positions:
            draw_sentinel(screen, int(sx), int(sy), 28)

        # Ghost placement guide (one potential position)
        ghost_angle = 2 * math.pi * sent_count / (sent_count + 2) - math.pi / 2 + 0.3
        gx = sent_cx + sent_r * 0.7 * math.cos(ghost_angle)
        gy = sent_cy + sent_r * 0.7 * math.sin(ghost_angle)
        ghost_surf = pygame.Surface((40, 40), pygame.SRCALPHA)
        body = [(20 - 5, 20 + 10), (20 - 3, 20 - 6), (20, 20 - 10),
                (20 + 3, 20 - 6), (20 + 5, 20 + 10)]
        pygame.draw.polygon(ghost_surf, (*GHOST_STONE, 60), body)
        pygame.draw.polygon(ghost_surf, (*GHOST_STONE, 100), body, 1)
        screen.blit(ghost_surf, (int(gx - 20), int(gy - 20)))

        # Dashed potential axis
        for i in range(0, int(sent_r * 1.4), 8):
            t = i / (sent_r * 1.4)
            dx = sent_cx + (gx - sent_cx) * t
            dy = sent_cy + (gy - sent_cy) * t
            if i % 16 < 8:
                pygame.draw.circle(screen, (*GHOST_STONE, 80), (int(dx), int(dy)), 1)

        # Symmetry order label
        sym_info = {
            "D1": "Mirror line — bilateral glow",
            "D2": "Cross — quadrant shading",
            "D3": "Triangle — Star of David",
            "D4": "Square — strong grid",
            "D6": "Hexagon — nature's tiling",
        }
        sym_desc = font_sm.render(sym_info[sent_name], True, (140, 140, 160))
        screen.blit(sym_desc, (sent_cx - sym_desc.get_width() // 2, H - 90))

        # === BOTTOM: Controls ===
        controls = "1-4: Formation  |  S: Sentinel order  |  H: Harmony  |  +/-: Units  |  A: Aura  |  ESC: Quit"
        ct = font_sm.render(controls, True, (80, 80, 100))
        screen.blit(ct, (W // 2 - ct.get_width() // 2, H - 30))

        # Harmony color swatch bar
        swatch_y = H - 60
        for hi, (hname, hcolor) in enumerate(HARMONY_COLORS.items()):
            sx = W // 2 - 150 + hi * 80
            pygame.draw.rect(screen, hcolor, (sx, swatch_y, 20, 12))
            if hi == harmony_idx:
                pygame.draw.rect(screen, BOUNDARY_WHITE, (sx - 1, swatch_y - 1, 22, 14), 1)
            hl = font_sm.render(hname, True, hcolor)
            screen.blit(hl, (sx + 24, swatch_y - 1))

        pygame.display.flip()

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
