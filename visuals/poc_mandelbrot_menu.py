"""
Proof-of-concept: Mandelbrot set menu background renderer.

Run standalone to see the fractal menu background.
Uses the game's actual color palette. Pure Python + pygame (no numpy).
Press SPACE to toggle slow zoom drift.
Press 1/2/3 to preview Julia set transitions (Easy/Medium/Hard).
ESC to quit.
"""
import pygame
import sys
import math

# --- Game palette (from constants.py) ---
COL_BG         = (20, 20, 30)
TERRAIN_GOLD   = (218, 165, 32)
RANK_BRONZE    = (205, 127, 50)
TERRAIN_GRASS  = (46, 139, 87)
COL_STONE      = (160, 150, 130)
COL_GUI_BG     = (30, 30, 45)
FRACTAL_DEEP   = (10, 8, 25)
GLOW_WHITE     = (240, 235, 220)

# Render resolution (quarter of display, then scaled up for speed)
RENDER_W, RENDER_H = 320, 180
DISPLAY_W, DISPLAY_H = 1280, 720
MAX_ITER = 128


def lerp_color(c1, c2, t):
    """Linearly interpolate between two RGB tuples."""
    t = max(0.0, min(1.0, t))
    return tuple(int(a + (b - a) * t) for a, b in zip(c1, c2))


def build_palette(max_iter):
    """Build a color lookup table using the game's palette."""
    palette = [None] * (max_iter + 1)

    for i in range(max_iter):
        t = i / max_iter
        if t < 0.15:
            c = lerp_color(FRACTAL_DEEP, TERRAIN_GOLD, t / 0.15)
        elif t < 0.35:
            c = lerp_color(TERRAIN_GOLD, RANK_BRONZE, (t - 0.15) / 0.20)
        elif t < 0.55:
            c = lerp_color(RANK_BRONZE, TERRAIN_GRASS, (t - 0.35) / 0.20)
        elif t < 0.75:
            c = lerp_color(TERRAIN_GRASS, COL_STONE, (t - 0.55) / 0.20)
        elif t < 0.90:
            c = lerp_color(COL_STONE, GLOW_WHITE, (t - 0.75) / 0.15)
        else:
            c = lerp_color(GLOW_WHITE, FRACTAL_DEEP, (t - 0.90) / 0.10)
        palette[i] = c

    # Interior = deep void
    palette[max_iter] = COL_BG
    return palette


def render_fractal(surf, cx, cy, zoom, max_iter, palette,
                   julia_c=None):
    """
    Render Mandelbrot or Julia set directly onto a pygame Surface.
    If julia_c is set, renders Julia set for that constant.
    Uses smooth coloring for band-free gradients.
    """
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

    for py in range(h):
        ci = y_min + py * dy
        for px in range(w):
            cr = x_min + px * dx

            if julia_c is not None:
                # Julia: z starts at pixel coord, c is fixed
                zr, zi = cr, ci
                jr, ji = julia_c.real, julia_c.imag
            else:
                # Mandelbrot: z starts at 0, c is pixel coord
                zr, zi = 0.0, 0.0
                jr, ji = cr, ci

            iteration = 0
            for iteration in range(max_iter):
                zr2 = zr * zr
                zi2 = zi * zi
                if zr2 + zi2 > 4.0:
                    break
                zi = 2.0 * zr * zi + ji
                zr = zr2 - zi2 + jr
            else:
                # Interior
                pixels[px, py] = surf.map_rgb(palette[max_iter])
                continue

            # Smooth coloring
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

    del pixels  # unlock surface


def render_fractal_progressive(surf, cx, cy, zoom, max_iter, palette,
                                julia_c=None, row_start=0, row_count=10):
    """Render a few rows at a time for progressive display. Returns next row."""
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
                zr2 = zr * zr
                zi2 = zi * zi
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
    return row_end if row_end < h else -1  # -1 = done


def main():
    pygame.init()
    screen = pygame.display.set_mode((DISPLAY_W, DISPLAY_H))
    pygame.display.set_caption("VDD PoC: Mandelbrot Menu Background")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont(None, 28)
    font_lg = pygame.font.SysFont(None, 64)
    font_sm = pygame.font.SysFont(None, 20)

    palette = build_palette(MAX_ITER)

    # Starting view: seahorse valley area
    cx, cy = -0.745, 0.186
    zoom = 1.0
    drifting = False  # start paused since rendering is slower in pure Python
    mode = "mandelbrot"
    julia_c = complex(-0.4, 0.6)

    # Render surface (small, then scaled up)
    render_surf = pygame.Surface((RENDER_W, RENDER_H))
    fractal_surf = None

    # Progressive rendering state
    render_row = 0
    rendering = True
    rows_per_frame = 6  # render N rows per frame for responsiveness

    # Menu overlay elements
    title = "RESONANCE"
    menu_items = ["[1] Easy  -  Douady Rabbit", "[2] Medium  -  Dendrite",
                  "[3] Hard  -  Chaos", "", "[SPACE] Toggle drift",
                  "[ESC] Quit"]

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
                elif event.key == pygame.K_1:
                    mode = "julia"
                    julia_c = complex(-0.4, 0.6)
                    zoom = 1.0
                    rendering = True
                    render_row = 0
                elif event.key == pygame.K_2:
                    mode = "julia"
                    julia_c = complex(-0.8, 0.156)
                    zoom = 1.0
                    rendering = True
                    render_row = 0
                elif event.key == pygame.K_3:
                    mode = "julia"
                    julia_c = complex(-0.7269, 0.1889)
                    zoom = 1.0
                    rendering = True
                    render_row = 0

        # Progressive rendering: do a few rows per frame
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

            # Scale up current state
            fractal_surf = pygame.transform.scale(render_surf,
                                                   (DISPLAY_W, DISPLAY_H))

        # Slow zoom drift (only trigger re-render when current is done)
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

        # Semi-transparent overlay for readability
        overlay = pygame.Surface((DISPLAY_W, DISPLAY_H), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 60))
        screen.blit(overlay, (0, 0))

        # Title with glow
        title_surf = font_lg.render(title, True, TERRAIN_GOLD)
        tr = title_surf.get_rect(center=(DISPLAY_W // 2, 120))
        glow_surf = font_lg.render(title, True, (TERRAIN_GOLD[0] // 2,
                                                   TERRAIN_GOLD[1] // 2,
                                                   TERRAIN_GOLD[2] // 2))
        gr = glow_surf.get_rect(center=(DISPLAY_W // 2 + 2, 122))
        screen.blit(glow_surf, gr)
        screen.blit(title_surf, tr)

        # Subtitle
        sub = font.render("~ forged from mathematics ~", True, COL_STONE)
        sr = sub.get_rect(center=(DISPLAY_W // 2, 170))
        screen.blit(sub, sr)

        # Menu items
        y = 280
        for item in menu_items:
            if item:
                color = GLOW_WHITE if item.startswith("[") else COL_STONE
                item_surf = font.render(item, True, color)
                ir = item_surf.get_rect(center=(DISPLAY_W // 2, y))
                screen.blit(item_surf, ir)
            y += 36

        # Mode indicator
        if mode == "julia":
            jtext = f"Julia set: c = {julia_c.real:.4f} + {julia_c.imag:.4f}i  |  ESC to return"
            js = font_sm.render(jtext, True, (180, 140, 80))
            screen.blit(js, (20, DISPLAY_H - 30))

        # Status
        status = "rendering..." if rendering else "complete"
        pct = f"{int(render_row / RENDER_H * 100)}%" if rendering else "100%"
        zt = font_sm.render(
            f"zoom: {zoom:.1f}x  |  {pct} {status}  |  "
            f"{'drifting' if drifting else 'paused (SPACE to drift)'}",
            True, (100, 100, 120))
        screen.blit(zt, (DISPLAY_W - 460, DISPLAY_H - 30))

        pygame.display.flip()

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
