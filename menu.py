import pygame
import math
from constants import SCREEN_WIDTH, SCREEN_HEIGHT, COL_BG, COL_TEXT, FPS

# --- Fractal palette (game-palette Mandelbrot) ---
_FRACTAL_DEEP   = (10, 8, 25)
_TERRAIN_GOLD   = (218, 165, 32)
_RANK_BRONZE    = (205, 127, 50)
_TERRAIN_GRASS  = (40, 118, 74)   # v10g2: desaturated to match constants.py
_COL_STONE      = (160, 150, 130)
_GLOW_WHITE     = (240, 235, 220)

# Fractal render resolution (tiny — scaled up 8x to 1280x720)
_FRAC_W, _FRAC_H = 160, 90
_MAX_ITER = 100

# Seahorse valley — rich in mini-brots that look like tiny fortresses
_VIEW_CX, _VIEW_CY = -0.745, 0.186
_VIEW_ZOOM = 1.0


def _lerp_color(c1, c2, t):
    t = max(0.0, min(1.0, t))
    return (int(c1[0] + (c2[0] - c1[0]) * t),
            int(c1[1] + (c2[1] - c1[1]) * t),
            int(c1[2] + (c2[2] - c1[2]) * t))


def _build_palette():
    """Build fractal color lookup table using the game's earth-tone palette."""
    pal = [None] * (_MAX_ITER + 1)
    for i in range(_MAX_ITER):
        t = i / _MAX_ITER
        if t < 0.15:
            c = _lerp_color(_FRACTAL_DEEP, _TERRAIN_GOLD, t / 0.15)
        elif t < 0.35:
            c = _lerp_color(_TERRAIN_GOLD, _RANK_BRONZE, (t - 0.15) / 0.20)
        elif t < 0.55:
            c = _lerp_color(_RANK_BRONZE, _TERRAIN_GRASS, (t - 0.35) / 0.20)
        elif t < 0.75:
            c = _lerp_color(_TERRAIN_GRASS, _COL_STONE, (t - 0.55) / 0.20)
        elif t < 0.90:
            c = _lerp_color(_COL_STONE, _GLOW_WHITE, (t - 0.75) / 0.15)
        else:
            c = _lerp_color(_GLOW_WHITE, _FRACTAL_DEEP, (t - 0.90) / 0.10)
        pal[i] = c
    pal[_MAX_ITER] = COL_BG  # interior = void
    return pal


def _render_fractal_rows(surf, palette, cx, cy, zoom,
                          row_start, row_count):
    """Render a band of Mandelbrot rows onto surf. Returns next row or -1 if done."""
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
            zr, zi = 0.0, 0.0
            iteration = 0
            for iteration in range(_MAX_ITER):
                zr2 = zr * zr
                zi2 = zi * zi
                if zr2 + zi2 > 4.0:
                    break
                zi = 2.0 * zr * zi + ci
                zr = zr2 - zi2 + cr
            else:
                pixels[px, py] = surf.map_rgb(palette[_MAX_ITER])
                continue

            # smooth coloring
            if iteration > 0:
                mag = zr * zr + zi * zi
                if mag > 1.0:
                    smooth = iteration - math.log(math.log(math.sqrt(mag))) / log2
                else:
                    smooth = float(iteration)
                idx = int((smooth / _MAX_ITER) * (_MAX_ITER - 1))
                idx = max(0, min(_MAX_ITER - 1, idx))
            else:
                idx = 0
            pixels[px, py] = surf.map_rgb(palette[idx])

    del pixels
    return row_end if row_end < h else -1


def _draw_polar_rose(surf, cx, cy, radius, k, color, width=1, rotation=0.0, n=80):
    """Draw a polar rose r=cos(k*theta) as decorative border."""
    pts = []
    for i in range(n):
        theta = rotation + 2 * math.pi * i / n
        r = abs(math.cos(k * theta)) * radius
        x = cx + r * math.cos(theta)
        y = cy + r * math.sin(theta)
        pts.append((int(x), int(y)))
    if len(pts) >= 3:
        pygame.draw.polygon(surf, color, pts, width)


def _draw_hex_ring(surf, cx, cy, radius, color, width=1, rotation=0.0, n=60):
    """Draw a superellipse hexagon as decorative ring."""
    pts = []
    np = 4.0
    for i in range(n):
        theta = rotation + 2 * math.pi * i / n
        ct = abs(math.cos(theta))
        st = abs(math.sin(theta))
        denom = (ct ** np + st ** np)
        if denom < 1e-10:
            r = radius
        else:
            r = radius / (denom ** (1.0 / np))
        pts.append((int(cx + r * math.cos(theta)), int(cy + r * math.sin(theta))))
    if len(pts) >= 3:
        pygame.draw.polygon(surf, color, pts, width)


class MainMenu:
    def __init__(self, screen):
        self.screen = screen
        self.clock = pygame.time.Clock()
        self.font_title = pygame.font.SysFont(None, 68)
        self.font_btn = pygame.font.SysFont(None, 32)
        self.font_desc = pygame.font.SysFont(None, 19)
        self.font_sub = pygame.font.SysFont(None, 24)
        self.font_ver = pygame.font.SysFont(None, 16)

        # fractal background state
        self._palette = _build_palette()
        self._frac_surf = pygame.Surface((_FRAC_W, _FRAC_H))
        self._frac_surf.fill(COL_BG)
        self._frac_scaled = None  # cached upscaled version
        self._frac_row = 0       # progressive render cursor
        self._frac_done = False
        self._frac_zoom = _VIEW_ZOOM
        self._frac_drift_timer = 0.0
        self._anim_t = 0.0  # animation timer for decorations

    def run(self):
        """Run menu loop. Returns 'easy', 'medium', 'hard', or 'exit'."""
        while True:
            dt = self.clock.tick(FPS) / 1000.0
            self._anim_t += dt
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return "exit"
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    result = self._check_buttons(event.pos)
                    if result:
                        return result
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        return "exit"
                    if event.key == pygame.K_1:
                        return "easy"
                    if event.key == pygame.K_2:
                        return "medium"
                    if event.key == pygame.K_3:
                        return "hard"

            # progressive fractal rendering: ~6 rows per frame
            if not self._frac_done:
                next_row = _render_fractal_rows(
                    self._frac_surf, self._palette,
                    _VIEW_CX, _VIEW_CY, self._frac_zoom,
                    self._frac_row, 6)
                if next_row == -1:
                    self._frac_done = True
                    self._frac_row = 0
                else:
                    self._frac_row = next_row
                self._frac_scaled = pygame.transform.scale(
                    self._frac_surf, (SCREEN_WIDTH, SCREEN_HEIGHT))

            # slow zoom drift
            if self._frac_done:
                self._frac_drift_timer += dt
                if self._frac_drift_timer > 3.0:
                    self._frac_drift_timer = 0.0
                    self._frac_zoom *= 1.5
                    if self._frac_zoom > 80.0:
                        self._frac_zoom = _VIEW_ZOOM
                    self._frac_done = False
                    self._frac_row = 0

            self._render()

    # --- Layout: golden ratio positioning ---
    _PHI = (1.0 + 5.0 ** 0.5) / 2.0  # ≈ 1.618
    # Title at h/phi³ — first golden subdivision
    _TITLE_Y = int(SCREEN_HEIGHT / (_PHI ** 3))          # ≈170
    _SUB_Y = _TITLE_Y + int(68 / _PHI)                   # ≈212
    # Difficulty buttons at h/phi² — second golden subdivision
    _BTN_Y = int(SCREEN_HEIGHT / (_PHI ** 2))             # ≈275
    _BTN_W = 180
    _BTN_H = 80
    _BTN_GAP = 10
    _EXIT_PAD = 30  # corner padding for quit button

    def _get_easy_btn_rect(self):
        cx = SCREEN_WIDTH // 2
        return pygame.Rect(cx - self._BTN_W - self._BTN_W // 2 - self._BTN_GAP,
                           self._BTN_Y, self._BTN_W, self._BTN_H)

    def _get_medium_btn_rect(self):
        cx = SCREEN_WIDTH // 2
        return pygame.Rect(cx - self._BTN_W // 2,
                           self._BTN_Y, self._BTN_W, self._BTN_H)

    def _get_hard_btn_rect(self):
        cx = SCREEN_WIDTH // 2
        return pygame.Rect(cx + self._BTN_W // 2 + self._BTN_GAP,
                           self._BTN_Y, self._BTN_W, self._BTN_H)

    def _get_exit_btn_rect(self):
        # v10_epsilon1: bottom-right, at h/phi (≈445) from top
        exit_y = int(SCREEN_HEIGHT / self._PHI) - 45 // 2  # centered on golden section
        return pygame.Rect(SCREEN_WIDTH - self._BTN_W - self._EXIT_PAD,
                           exit_y,
                           self._BTN_W, 45)

    def _check_buttons(self, pos):
        if self._get_easy_btn_rect().collidepoint(pos):
            return "easy"
        if self._get_medium_btn_rect().collidepoint(pos):
            return "medium"
        if self._get_hard_btn_rect().collidepoint(pos):
            return "hard"
        if self._get_exit_btn_rect().collidepoint(pos):
            return "exit"
        return None

    def _draw_diff_button(self, rect, name, desc, key, color_accent, mx, my,
                          leaf_k=2.5):
        hovered = rect.collidepoint(mx, my)
        cx, cy = rect.centerx, rect.centery

        # background panel with gradient feel
        btn_surf = pygame.Surface((rect.w, rect.h), pygame.SRCALPHA)
        if hovered:
            btn_surf.fill((30, 30, 50, 220))
            # inner glow
            glow_surf = pygame.Surface((rect.w, rect.h), pygame.SRCALPHA)
            glow_surf.fill((*color_accent, 30))
            btn_surf.blit(glow_surf, (0, 0))
        else:
            btn_surf.fill((20, 20, 35, 190))
        self.screen.blit(btn_surf, rect.topleft)

        # decorative polar rose border (breathing on hover)
        # leaf_k: 1.5 = 3 leaves, 2.5 = 5 leaves, 3.5 = 7 leaves
        rose_r = max(rect.w, rect.h) // 2 + 5
        rot = self._anim_t * 0.3 if hovered else 0.0
        k = leaf_k
        border_color = color_accent if hovered else tuple(c // 2 for c in color_accent)
        _draw_polar_rose(self.screen, cx, cy, rose_r, k, border_color,
                         width=2 if hovered else 1, rotation=rot)

        # corner accent dots (Fibonacci-spaced)
        phi = (1 + math.sqrt(5)) / 2
        for i in range(4):
            angle = i * math.pi / 2 + math.pi / 4
            dx = int(math.cos(angle) * (rect.w // 2 - 4))
            dy = int(math.sin(angle) * (rect.h // 2 - 4))
            dot_r = 3 if hovered else 2
            pygame.draw.circle(self.screen, color_accent,
                               (cx + dx, cy + dy), dot_r)

        # name text with slight glow
        if hovered:
            glow = self.font_btn.render(name, True,
                                        tuple(min(255, c + 40) for c in color_accent))
            self.screen.blit(glow, glow.get_rect(centerx=cx + 1, top=rect.top + 10))
        text_surf = self.font_btn.render(name, True, color_accent)
        self.screen.blit(text_surf, text_surf.get_rect(centerx=cx, top=rect.top + 9))

        # description
        desc_surf = self.font_desc.render(desc, True, (150, 150, 170))
        self.screen.blit(desc_surf, desc_surf.get_rect(centerx=cx, top=rect.top + 40))

        # key hint in a small hex ring
        key_surf = self.font_desc.render(f"[{key}]", True, (100, 100, 120))
        self.screen.blit(key_surf, key_surf.get_rect(centerx=cx, top=rect.top + 58))

    def _draw_button(self, rect, text, mx, my):
        hovered = rect.collidepoint(mx, my)
        cx, cy = rect.centerx, rect.centery
        accent = (140, 130, 160)

        btn_surf = pygame.Surface((rect.w, rect.h), pygame.SRCALPHA)
        if hovered:
            btn_surf.fill((30, 30, 50, 210))
            glow_surf = pygame.Surface((rect.w, rect.h), pygame.SRCALPHA)
            glow_surf.fill((*accent, 25))
            btn_surf.blit(glow_surf, (0, 0))
        else:
            btn_surf.fill((20, 20, 35, 170))
        self.screen.blit(btn_surf, rect.topleft)

        # hex ring border (rotating slowly on hover)
        hex_r = max(rect.w, rect.h) // 2 + 3
        hex_rot = math.pi / 6 + (self._anim_t * 0.2 if hovered else 0.0)
        hex_color = accent if hovered else tuple(c // 2 for c in accent)
        _draw_hex_ring(self.screen, cx, cy, hex_r, hex_color,
                       width=2 if hovered else 1, rotation=hex_rot)

        # corner accent dots
        for i in range(4):
            angle = i * math.pi / 2 + math.pi / 4
            dx = int(math.cos(angle) * (rect.w // 2 - 4))
            dy = int(math.sin(angle) * (rect.h // 2 - 4))
            dot_r = 3 if hovered else 2
            pygame.draw.circle(self.screen, hex_color, (cx + dx, cy + dy), dot_r)

        # text with glow on hover
        if hovered:
            glow = self.font_btn.render(text, True, (240, 240, 250))
            self.screen.blit(glow, glow.get_rect(center=(cx + 1, cy + 1)))
        text_surf = self.font_btn.render(text, True,
                                          (220, 220, 230) if hovered else (160, 160, 180))
        self.screen.blit(text_surf, text_surf.get_rect(center=(cx, cy)))

    def _render(self):
        # fractal background
        if self._frac_scaled:
            self.screen.blit(self._frac_scaled, (0, 0))
        else:
            self.screen.fill(COL_BG)

        # subtle vignette overlay (darker edges, brighter center for title)
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 60))
        self.screen.blit(overlay, (0, 0))

        mx, my = pygame.mouse.get_pos()
        cx = SCREEN_WIDTH // 2

        # --- decorative top rose (slowly rotating) ---
        rose_rot = self._anim_t * 0.15
        _draw_polar_rose(self.screen, cx, self._TITLE_Y - 30, 40, 3.5,
                         (109, 82, 16, 60), width=1, rotation=rose_rot, n=100)

        # --- title with multi-layer glow ---
        title_text = "Resonance"

        # deep shadow
        s3 = self.font_title.render(title_text, True, (40, 30, 10))
        self.screen.blit(s3, s3.get_rect(center=(cx + 3, self._TITLE_Y + 3)))
        # warm glow
        s2 = self.font_title.render(title_text, True, (140, 110, 30))
        self.screen.blit(s2, s2.get_rect(center=(cx + 1, self._TITLE_Y + 1)))
        # main title in warm gold
        s1 = self.font_title.render(title_text, True, (230, 205, 90))
        self.screen.blit(s1, s1.get_rect(center=(cx, self._TITLE_Y)))

        # --- subtitle with mathematical flourish ---
        sub_text = "~ forged from mathematics ~"
        sub_surf = self.font_sub.render(sub_text, True, (160, 150, 130))
        self.screen.blit(sub_surf, sub_surf.get_rect(center=(cx, self._SUB_Y)))

        # thin decorative line under subtitle (golden spiral inspired curve)
        line_y = self._SUB_Y + 18
        line_w = 280
        pts = []
        for i in range(60):
            t = i / 59.0
            lx = cx - line_w // 2 + int(t * line_w)
            ly = line_y + int(3 * math.sin(t * math.pi * 4 + self._anim_t * 0.5))
            pts.append((lx, ly))
        if len(pts) >= 2:
            pygame.draw.lines(self.screen, (109, 82, 16), False, pts, 1)

        # --- difficulty buttons (3/5/7 leaf polar roses) ---
        self._draw_diff_button(self._get_easy_btn_rect(),
                               "Easy", "Gentle pace, ample resources", "1",
                               (80, 200, 80), mx, my, leaf_k=1.5)
        self._draw_diff_button(self._get_medium_btn_rect(),
                               "Medium", "The intended challenge", "2",
                               (218, 165, 32), mx, my, leaf_k=2.5)
        self._draw_diff_button(self._get_hard_btn_rect(),
                               "Hard", "For seasoned commanders", "3",
                               (200, 60, 60), mx, my, leaf_k=3.5)

        # --- exit button ---
        self._draw_button(self._get_exit_btn_rect(), "Exit", mx, my)

        # --- bottom info bar ---
        hint_surf = self.font_desc.render(
            "Press 1 / 2 / 3 to start   |   ESC to quit", True, (70, 70, 90))
        self.screen.blit(hint_surf,
                         hint_surf.get_rect(center=(cx, SCREEN_HEIGHT - 50)))

        ver_surf = self.font_ver.render("v10_epsilon1", True, (50, 50, 65))
        self.screen.blit(ver_surf,
                         ver_surf.get_rect(bottomleft=(12, SCREEN_HEIGHT - 8)))

        pygame.display.flip()
