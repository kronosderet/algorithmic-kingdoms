"""
Proof-of-concept: Mandelbrot Throne — Main Menu with Visual Duality.

Demonstrates the VDD's core visual thesis: player = convergent (interior),
enemy = divergent (exterior), with the Mandelbrot boundary as the battlefield.

Features:
  - Dual-palette rendering: convergent blues/golds for interior, divergent reds for exterior
  - Julia set transitions per difficulty (Douady rabbit, dendrite, chaos)
  - Polar rose difficulty buttons (3/5/7 petals)
  - Golden ratio title positioning
  - Koch-bordered button frames

Controls:
  1/2/3    Preview Julia set (Easy/Medium/Hard)
  SPACE    Toggle slow zoom drift
  D        Toggle duality mode (convergent vs divergent palette)
  ESC      Quit / Return to Mandelbrot
"""
import pygame
import sys
import math

# --- Chromatic Heptarchy System Colors (VDD Section 8.3) ---
COL_BG         = (20, 20, 30)
EARTH_GOLD     = (218, 165, 32)
BRONZE         = (205, 127, 50)
CONVERGENT_BLUE = (15, 25, 60)
DIVERGENT_RED  = (120, 20, 40)
RESONANCE_GLOW = (180, 160, 255)
BOUNDARY_WHITE = (240, 235, 220)
FRACTAL_DEEP   = (10, 8, 25)
GHOST_STONE    = (80, 75, 60)
LIFE_GREEN     = (46, 139, 87)
COL_STONE      = (160, 150, 130)

# Tone colors for difficulty rose petals
SOLDIER_RED    = (200, 60, 60)
ARCHER_PURPLE  = (140, 100, 200)
SAGE_VIOLET    = (100, 50, 150)

# Render resolution (quarter, then scaled up)
RENDER_W, RENDER_H = 320, 180
DISPLAY_W, DISPLAY_H = 1280, 720
MAX_ITER = 128
PHI = (1 + math.sqrt(5)) / 2  # Golden ratio


def lerp_color(c1, c2, t):
    t = max(0.0, min(1.0, t))
    return tuple(int(a + (b - a) * t) for a, b in zip(c1, c2))


def build_convergent_palette(max_iter):
    """Player-side palette: cool blues, warm golds, deep greens."""
    palette = [None] * (max_iter + 1)
    for i in range(max_iter):
        t = i / max_iter
        if t < 0.12:
            c = lerp_color(FRACTAL_DEEP, CONVERGENT_BLUE, t / 0.12)
        elif t < 0.25:
            c = lerp_color(CONVERGENT_BLUE, EARTH_GOLD, (t - 0.12) / 0.13)
        elif t < 0.40:
            c = lerp_color(EARTH_GOLD, BRONZE, (t - 0.25) / 0.15)
        elif t < 0.55:
            c = lerp_color(BRONZE, LIFE_GREEN, (t - 0.40) / 0.15)
        elif t < 0.70:
            c = lerp_color(LIFE_GREEN, COL_STONE, (t - 0.55) / 0.15)
        elif t < 0.85:
            c = lerp_color(COL_STONE, RESONANCE_GLOW, (t - 0.70) / 0.15)
        elif t < 0.95:
            c = lerp_color(RESONANCE_GLOW, BOUNDARY_WHITE, (t - 0.85) / 0.10)
        else:
            c = lerp_color(BOUNDARY_WHITE, FRACTAL_DEEP, (t - 0.95) / 0.05)
        palette[i] = c
    palette[max_iter] = COL_BG  # Interior = void
    return palette


def build_divergent_palette(max_iter):
    """Enemy-side palette: hot reds, acid greens, bruised purples."""
    palette = [None] * (max_iter + 1)
    for i in range(max_iter):
        t = i / max_iter
        if t < 0.15:
            c = lerp_color(FRACTAL_DEEP, DIVERGENT_RED, t / 0.15)
        elif t < 0.30:
            c = lerp_color(DIVERGENT_RED, (200, 80, 40), (t - 0.15) / 0.15)
        elif t < 0.45:
            c = lerp_color((200, 80, 40), (180, 200, 30), (t - 0.30) / 0.15)
        elif t < 0.60:
            c = lerp_color((180, 200, 30), (80, 40, 100), (t - 0.45) / 0.15)
        elif t < 0.75:
            c = lerp_color((80, 40, 100), (40, 15, 60), (t - 0.60) / 0.15)
        elif t < 0.90:
            c = lerp_color((40, 15, 60), (200, 40, 40), (t - 0.75) / 0.15)
        else:
            c = lerp_color((200, 40, 40), FRACTAL_DEEP, (t - 0.90) / 0.10)
        palette[i] = c
    palette[max_iter] = (5, 3, 15)  # Interior = deep abyss
    return palette


def build_duality_palette(max_iter):
    """Both worlds: convergent interior, divergent exterior, boundary highlighted."""
    conv = build_convergent_palette(max_iter)
    div = build_divergent_palette(max_iter)
    palette = [None] * (max_iter + 1)
    for i in range(max_iter):
        t = i / max_iter
        # Near-boundary iterations get boundary white highlight
        if 0.3 < t < 0.5:
            boundary_t = 1.0 - abs(t - 0.4) / 0.1
            c = lerp_color(div[i], BOUNDARY_WHITE, boundary_t * 0.4)
        else:
            c = div[i]
        palette[i] = c
    # Interior uses convergent deep blue instead of black
    palette[max_iter] = CONVERGENT_BLUE
    return palette


def render_fractal_progressive(surf, cx, cy, zoom, max_iter, palette,
                                julia_c=None, row_start=0, row_count=10):
    w, h = surf.get_width(), surf.get_height()
    aspect = w / h
    x_range = 3.0 / zoom
    y_range = x_range / aspect
    x_min = cx - x_range / 2
    y_min = cy - y_range / 2
    dx = x_range / w
    dy = y_range / h
    log2 = math.log(2.0)

    pixels = pygame.PixelArray(surf)
    row_end = min(h, row_start + row_count)

    for py in range(row_start, row_end):
        ci = y_min + py * dy
        for px in range(w):
            cr = x_min + px * dx
            if julia_c is not None:
                zr, zi = cr, ci
                jr, ji = julia_c.real, julia_c.imag
            else:
                zr, zi = 0.0, 0.0
                jr, ji = cr, ci

            iteration = 0
            for iteration in range(max_iter):
                zr2, zi2 = zr * zr, zi * zi
                if zr2 + zi2 > 4.0:
                    break
                zi = 2.0 * zr * zi + ji
                zr = zr2 - zi2 + jr
            else:
                pixels[px, py] = surf.map_rgb(palette[max_iter])
                continue

            if iteration > 0:
                mag = math.sqrt(zr * zr + zi * zi)
                if mag > 1.0:
                    smooth = iteration - math.log(math.log(mag)) / log2
                else:
                    smooth = iteration
                idx = int((smooth / max_iter) * (max_iter - 1))
                idx = max(0, min(max_iter - 1, idx))
            else:
                idx = 0
            pixels[px, py] = surf.map_rgb(palette[idx])

    del pixels
    return row_end if row_end < h else -1


def koch_border_pts(x1, y1, x2, y2, depth):
    """Generate Koch curve points between two endpoints."""
    if depth == 0:
        return [(x1, y1)]
    dx, dy = x2 - x1, y2 - y1
    ax, ay = x1 + dx / 3, y1 + dy / 3
    bx, by = x1 + 2 * dx / 3, y1 + 2 * dy / 3
    px = (ax + bx) / 2 + math.sqrt(3) / 6 * (y1 - y2)
    py = (ay + by) / 2 + math.sqrt(3) / 6 * (x2 - x1)
    pts = []
    pts.extend(koch_border_pts(x1, y1, ax, ay, depth - 1))
    pts.extend(koch_border_pts(ax, ay, px, py, depth - 1))
    pts.extend(koch_border_pts(px, py, bx, by, depth - 1))
    pts.extend(koch_border_pts(bx, by, x2, y2, depth - 1))
    return pts


def draw_koch_rect(surf, rect, depth, color, width=1):
    """Draw a Koch-bordered rectangle."""
    x, y, w, h = rect
    corners = [(x, y), (x + w, y), (x + w, y + h), (x, y + h)]
    for i in range(4):
        pts = koch_border_pts(*corners[i], *corners[(i + 1) % 4], depth)
        pts.append(corners[(i + 1) % 4])
        int_pts = [(int(p[0]), int(p[1])) for p in pts]
        if len(int_pts) >= 2:
            pygame.draw.lines(surf, color, False, int_pts, width)


def draw_rose_decoration(surf, cx, cy, radius, k, color, alpha=80):
    """Draw a faint polar rose decoration."""
    pts = []
    for i in range(100):
        theta = 2 * math.pi * i / 100
        r = radius * abs(math.cos(k * theta))
        pts.append((int(cx + r * math.cos(theta)), int(cy + r * math.sin(theta))))
    if len(pts) >= 3:
        deco_surf = pygame.Surface(surf.get_size(), pygame.SRCALPHA)
        pygame.draw.polygon(deco_surf, (*color, alpha), pts)
        pygame.draw.polygon(deco_surf, (*color, alpha + 40), pts, 1)
        surf.blit(deco_surf, (0, 0))


def main():
    pygame.init()
    screen = pygame.display.set_mode((DISPLAY_W, DISPLAY_H))
    pygame.display.set_caption("VDD PoC: The Mandelbrot Throne — Visual Duality")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont(None, 28)
    font_lg = pygame.font.SysFont(None, 72)
    font_sub = pygame.font.SysFont(None, 26)
    font_sm = pygame.font.SysFont(None, 20)
    font_btn = pygame.font.SysFont(None, 24)
    font_desc = pygame.font.SysFont(None, 17)

    palette_modes = {
        "convergent": build_convergent_palette(MAX_ITER),
        "divergent": build_divergent_palette(MAX_ITER),
        "duality": build_duality_palette(MAX_ITER),
    }
    palette_mode = "duality"
    palette = palette_modes[palette_mode]

    cx, cy = -0.745, 0.186  # Seahorse valley
    zoom = 1.0
    drifting = False
    mode = "mandelbrot"
    julia_c = complex(-0.4, 0.6)

    render_surf = pygame.Surface((RENDER_W, RENDER_H))
    fractal_surf = None
    render_row = 0
    rendering = True
    rows_per_frame = 6

    # Difficulty data
    difficulties = [
        ("EASY", "Gentle pace — learn the game",
         "300 gold, 4 workers, 7 incidents",
         complex(-0.4, 0.6), 1.5, LIFE_GREEN, True),
        ("MEDIUM", "The intended challenge",
         "200 gold, 3 workers, 14 incidents",
         complex(-0.8, 0.156), 2.5, EARTH_GOLD, False),
        ("HARD", "For seasoned commanders",
         "180 gold, 3 workers, 21 incidents",
         complex(-0.7269, 0.1889), 3.5, SOLDIER_RED, False),
    ]

    running = True
    while running:
        dt = clock.tick(30) / 1000.0

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if mode == "julia":
                        mode = "mandelbrot"
                        zoom = 1.0
                        rendering = True
                        render_row = 0
                    else:
                        running = False
                elif event.key == pygame.K_SPACE:
                    drifting = not drifting
                elif event.key == pygame.K_d:
                    # Cycle palette modes
                    modes = ["convergent", "divergent", "duality"]
                    idx = modes.index(palette_mode)
                    palette_mode = modes[(idx + 1) % 3]
                    palette = palette_modes[palette_mode]
                    rendering = True
                    render_row = 0
                elif event.key in (pygame.K_1, pygame.K_2, pygame.K_3):
                    idx = event.key - pygame.K_1
                    mode = "julia"
                    julia_c = difficulties[idx][3]
                    zoom = 1.0
                    rendering = True
                    render_row = 0

        # Progressive rendering
        if rendering:
            jc = julia_c if mode == "julia" else None
            next_row = render_fractal_progressive(
                render_surf, cx, cy, zoom, MAX_ITER, palette,
                julia_c=jc, row_start=render_row, row_count=rows_per_frame)
            if next_row == -1:
                rendering = False
                render_row = 0
            else:
                render_row = next_row
            fractal_surf = pygame.transform.scale(render_surf, (DISPLAY_W, DISPLAY_H))

        if drifting and not rendering:
            zoom *= 1.0 + 0.3 * dt
            if zoom > 30.0:
                zoom = 1.0
            rendering = True
            render_row = 0

        # Draw
        if fractal_surf:
            screen.blit(fractal_surf, (0, 0))
        else:
            screen.fill(COL_BG)

        # Semi-transparent overlay
        overlay = pygame.Surface((DISPLAY_W, DISPLAY_H), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 70))
        screen.blit(overlay, (0, 0))

        # Golden ratio positioning
        title_y = int(DISPLAY_H / (PHI ** 3))  # ~h/φ³
        button_y = int(DISPLAY_H / (PHI ** 2))  # ~h/φ²

        # Title: "RESONANCE" with glow
        title_text = "RESONANCE"
        glow = font_lg.render(title_text, True, (EARTH_GOLD[0] // 3,
                                                   EARTH_GOLD[1] // 3,
                                                   EARTH_GOLD[2] // 3))
        screen.blit(glow, glow.get_rect(center=(DISPLAY_W // 2 + 2, title_y + 2)))
        title_surf = font_lg.render(title_text, True, EARTH_GOLD)
        screen.blit(title_surf, title_surf.get_rect(center=(DISPLAY_W // 2, title_y)))

        # Subtitle
        sub_text = "the mathematics made visible"
        sub_surf = font_sub.render(sub_text, True, GHOST_STONE)
        screen.blit(sub_surf, sub_surf.get_rect(center=(DISPLAY_W // 2, title_y + 50)))

        # Difficulty buttons with Koch borders and rose decorations
        btn_w, btn_h = 280, 105
        btn_gap = 20
        total_w = 3 * btn_w + 2 * btn_gap
        start_x = (DISPLAY_W - total_w) // 2

        for i, (name, desc1, desc2, jc, rose_k, btn_color, recommended) in enumerate(difficulties):
            bx = start_x + i * (btn_w + btn_gap)
            by = button_y

            # Button background (radial gradient approximation)
            btn_surf = pygame.Surface((btn_w, btn_h), pygame.SRCALPHA)
            for gy in range(btn_h):
                for gx in range(btn_w):
                    dist = math.sqrt((gx - btn_w / 2) ** 2 + (gy - btn_h / 2) ** 2)
                    max_dist = math.sqrt((btn_w / 2) ** 2 + (btn_h / 2) ** 2)
                    t = min(1.0, dist / max_dist)
                    c = lerp_color((35, 32, 50), (20, 18, 30), t)
                    btn_surf.set_at((gx, gy), (*c, 200))
            screen.blit(btn_surf, (bx, by))

            # Koch border
            draw_koch_rect(screen, (bx, by, btn_w, btn_h), 1, btn_color, 1)

            # Rose decoration at corners
            draw_rose_decoration(screen, bx + 25, by + 25, 15, rose_k, btn_color, 40)
            draw_rose_decoration(screen, bx + btn_w - 25, by + 25, 15, rose_k, btn_color, 40)

            # Button text
            name_surf = font_btn.render(name, True, btn_color)
            screen.blit(name_surf, name_surf.get_rect(centerx=bx + btn_w // 2, top=by + 10))

            d1_surf = font_desc.render(desc1, True, (150, 150, 170))
            screen.blit(d1_surf, d1_surf.get_rect(centerx=bx + btn_w // 2, top=by + 35))

            d2_surf = font_desc.render(desc2, True, (120, 120, 140))
            screen.blit(d2_surf, d2_surf.get_rect(centerx=bx + btn_w // 2, top=by + 53))

            # Key hint
            key_surf = font_desc.render(f"[{i + 1}]", True, GHOST_STONE)
            screen.blit(key_surf, key_surf.get_rect(centerx=bx + btn_w // 2, top=by + 73))

            if recommended:
                rec_surf = font_desc.render("Recommended for first game", True, EARTH_GOLD)
                screen.blit(rec_surf, rec_surf.get_rect(centerx=bx + btn_w // 2, top=by + 88))

        # Controls info
        controls = [
            "SPACE: drift  |  D: palette mode  |  1/2/3: Julia preview  |  ESC: quit",
        ]
        for ci, ctrl in enumerate(controls):
            cs = font_sm.render(ctrl, True, (80, 80, 100))
            screen.blit(cs, (DISPLAY_W // 2 - cs.get_width() // 2, DISPLAY_H - 55 + ci * 20))

        # Status bar
        palette_label = palette_mode.upper()
        if mode == "julia":
            info = f"Julia: c = {julia_c.real:.3f}+{julia_c.imag:.3f}i"
        else:
            info = f"Mandelbrot: seahorse valley"
        status = f"{info}  |  Palette: {palette_label}  |  Zoom: {zoom:.1f}x"
        st = font_sm.render(status, True, (90, 90, 110))
        screen.blit(st, (20, DISPLAY_H - 25))

        pygame.display.flip()

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
