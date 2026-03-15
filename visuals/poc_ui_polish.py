"""
Proof-of-concept: UI polish elements (VDD Phase 5).

Fibonacci HP bars, mathematical resource icons, breathing selection ring,
minimap heat overlay, dissolving notifications, wave timer arc.

Controls:
  UP/DOWN     Adjust HP
  1/2/3       Select unit (changes selection ring color)
  SPACE       Toggle multi-select
  N           Trigger notification
  W           Advance wave timer
  Click map   Add combat heat
  ESC         Quit
"""
import pygame
import math
import random
import sys

# --- palette ---
COL_BG = (20, 20, 30)
TERRAIN_GOLD = (218, 165, 32)
WORKER_BLUE = (50, 130, 220)
SOLDIER_RED = (200, 60, 60)
ARCHER_GREEN = (140, 100, 200)  # Mi — Precision Purple (renamed from green)
GLOW_WHITE = (240, 235, 220)
HP_GREEN = (0, 200, 80)
HP_YELLOW = (220, 200, 0)
HP_RED = (200, 40, 40)
TERRAIN_GRASS = (46, 139, 87)

W, H = 1280, 720


def lerp_c(c1, c2, t):
    t = max(0, min(1, t))
    return tuple(int(a + (b - a) * t) for a, b in zip(c1, c2))


# ── Fibonacci HP bar ────────────────────────────────────────
def fibonacci_segments(n=8):
    """Generate Fibonacci proportions for bar segments."""
    fibs = [1, 1]
    for _ in range(n - 2):
        fibs.append(fibs[-1] + fibs[-2])
    total = sum(fibs)
    return [f / total for f in fibs]


def draw_fib_hp_bar(surf, x, y, w, h, hp_pct, time_acc):
    """HP bar with Fibonacci-proportioned segments."""
    pygame.draw.rect(surf, (25, 25, 35), (x, y, w, h))
    segs = fibonacci_segments(8)
    cx = x
    for i, seg_pct in enumerate(segs):
        seg_w = seg_pct * w
        # what fraction of this segment is filled
        seg_start = sum(segs[:i])
        seg_end = seg_start + seg_pct
        if hp_pct <= seg_start:
            fill = 0
        elif hp_pct >= seg_end:
            fill = 1
        else:
            fill = (hp_pct - seg_start) / seg_pct

        if fill > 0:
            # color gradient
            global_t = (seg_start + seg_pct * fill * 0.5)
            if global_t > 0.6:
                c = HP_GREEN
            elif global_t > 0.3:
                c = lerp_c(HP_YELLOW, HP_GREEN, (global_t - 0.3) / 0.3)
            else:
                c = lerp_c(HP_RED, HP_YELLOW, global_t / 0.3)

            fill_w = int(seg_w * fill)
            pygame.draw.rect(surf, c, (int(cx), y, fill_w, h))

        # segment border
        pygame.draw.rect(surf, (50, 50, 60), (int(cx), y, max(1, int(seg_w)), h), 1)
        cx += seg_w

    pygame.draw.rect(surf, (80, 80, 100), (x, y, w, h), 1)


# ── resource icons ──────────────────────────────────────────
def draw_gold_icon(surf, cx, cy, size, t):
    phi = (1 + math.sqrt(5)) / 2
    b = math.log(phi) / (math.pi / 2)
    pts = []
    for i in range(50):
        theta = t * 0.5 + i * 0.15
        r = 0.5 * math.exp(b * theta * 0.3) * size * 0.15
        if r > size * 0.45:
            break
        pts.append((int(cx + r * math.cos(theta)),
                     int(cy + r * math.sin(theta))))
    if len(pts) >= 2:
        pygame.draw.lines(surf, TERRAIN_GOLD, False, pts, 2)


def draw_wood_icon(surf, cx, cy, size, t):
    sway = math.sin(t * 1.5) * 0.1
    pygame.draw.line(surf, (139, 90, 43), (int(cx), int(cy + size * 0.4)),
                     (int(cx), int(cy - size * 0.1)), 2)
    for ang, ln in [(-0.5 + sway, 0.25), (0.4 + sway, 0.3), (-0.3 - sway, 0.2)]:
        ex = cx + math.cos(-math.pi / 2 + ang) * size * ln
        ey = cy - size * 0.1 + math.sin(-math.pi / 2 + ang) * size * ln
        pygame.draw.line(surf, (30, 110, 50), (int(cx), int(cy - size * 0.1)),
                         (int(ex), int(ey)), 2)


def draw_stone_icon(surf, cx, cy, size, t):
    pulse = 1.0 + 0.06 * math.sin(t * 2)
    for i in range(6):
        a = i * math.pi / 3 + t * 0.1
        r = size * 0.35 * pulse
        ex, ey = cx + r * math.cos(a), cy + r * math.sin(a)
        pygame.draw.line(surf, (160, 150, 130), (int(cx), int(cy)),
                         (int(ex), int(ey)), 1)
        a2 = (i + 1) * math.pi / 3 + t * 0.1
        ex2, ey2 = cx + r * math.cos(a2), cy + r * math.sin(a2)
        pygame.draw.line(surf, (140, 135, 115), (int(ex), int(ey)),
                         (int(ex2), int(ey2)), 1)


def draw_iron_icon(surf, cx, cy, size, t):
    pulse = 1.0 + 0.04 * math.sin(t * 3)
    r = size * 0.3 * pulse
    for i in range(4):
        a = i * math.pi / 2 + math.pi / 4
        for j in range(4):
            a2 = j * math.pi / 2 + math.pi / 4
            x1, y1 = cx + r * math.cos(a) * 0.5, cy + r * math.sin(a) * 0.5
            x2, y2 = cx + r * math.cos(a2), cy + r * math.sin(a2)
            pygame.draw.line(surf, (100, 160, 220), (int(x1), int(y1)),
                             (int(x2), int(y2)), 1)


# ── breathing selection ring ────────────────────────────────
def draw_selection_ring(surf, cx, cy, radius, color, t, k=3):
    r = radius * (1.0 + 0.08 * math.sin(t * 3))
    rot = t * 0.5
    pts = []
    for i in range(100):
        theta = rot + 2 * math.pi * i / 100
        rv = abs(math.cos(k * theta)) * r
        pts.append((int(cx + rv * math.cos(theta)),
                     int(cy + rv * math.sin(theta))))
    if len(pts) >= 3:
        pygame.draw.polygon(surf, color, pts, 2)


# ── minimap with heat overlay ───────────────────────────────
class Minimap:
    def __init__(self, x, y, w, h):
        self.rect = pygame.Rect(x, y, w, h)
        self.heat_points = []  # (mx, my, intensity, age)

    def add_heat(self, mx, my):
        # convert screen click to minimap coords
        rx = (mx - self.rect.x) / self.rect.w
        ry = (my - self.rect.y) / self.rect.h
        if 0 <= rx <= 1 and 0 <= ry <= 1:
            self.heat_points.append([rx, ry, 1.0, 0])

    def update(self, dt):
        for hp in self.heat_points:
            hp[3] += dt
            hp[2] = max(0, 1.0 - hp[3] / 3.0)  # fade over 3 sec
        self.heat_points = [hp for hp in self.heat_points if hp[2] > 0]

    def draw(self, surf):
        # terrain background
        bg = pygame.Surface((self.rect.w, self.rect.h))
        bg.fill((25, 60, 35))
        # simple noise terrain
        for ty in range(0, self.rect.h, 8):
            for tx in range(0, self.rect.w, 8):
                n = math.sin(tx * 0.1) * math.cos(ty * 0.15) * 0.5 + 0.5
                c = lerp_c((25, 60, 35), TERRAIN_GRASS, n * 0.4)
                pygame.draw.rect(bg, c, (tx, ty, 8, 8))
        surf.blit(bg, self.rect.topleft)

        # heat overlay
        for hp in self.heat_points:
            hx = int(self.rect.x + hp[0] * self.rect.w)
            hy = int(self.rect.y + hp[1] * self.rect.h)
            r = int(15 * hp[2])
            if r > 0:
                heat_surf = pygame.Surface((r * 2, r * 2), pygame.SRCALPHA)
                alpha = int(120 * hp[2])
                pygame.draw.circle(heat_surf, (200, 40, 40, alpha), (r, r), r)
                surf.blit(heat_surf, (hx - r, hy - r))

        # border
        pygame.draw.rect(surf, (80, 80, 100), self.rect, 2)


# ── dissolving notifications ────────────────────────────────
class Notification:
    def __init__(self, text, color, y):
        self.text = text
        self.color = color
        self.y = y
        self.age = 0
        self.duration = 2.5
        self.alive = True

    def update(self, dt):
        self.age += dt
        self.y -= dt * 20  # drift up
        if self.age > self.duration:
            self.alive = False

    def draw(self, surf, font):
        t = self.age / self.duration
        for i, ch in enumerate(self.text):
            # each char fades independently with delay
            char_t = max(0, t - i * 0.03)
            alpha = max(0, 1.0 - char_t * 1.5)
            if alpha <= 0:
                continue
            char_y = self.y - char_t * 10  # individual drift
            c = lerp_c(self.color, COL_BG, 1 - alpha)
            cs = font.render(ch, True, c)
            surf.blit(cs, (W // 2 - len(self.text) * 5 + i * 12, int(char_y)))


# ── wave timer arc ──────────────────────────────────────────
def draw_wave_timer(surf, cx, cy, radius, progress, time_acc):
    """Circular arc with polar rose petals that bloom as timer fills."""
    # background circle
    pygame.draw.circle(surf, (30, 30, 45), (cx, cy), radius, 2)

    # arc fill
    if progress <= 0:
        return

    # color shift: blue -> yellow -> red
    if progress < 0.5:
        c = lerp_c(WORKER_BLUE, HP_YELLOW, progress * 2)
    else:
        c = lerp_c(HP_YELLOW, HP_RED, (progress - 0.5) * 2)

    # draw arc as line segments
    n_segs = int(100 * progress)
    pulse_speed = 1.0 + progress * 4  # pulses faster near wave
    pulse = 1.0 + 0.05 * math.sin(time_acc * pulse_speed) * progress
    pts = []
    for i in range(n_segs + 1):
        angle = -math.pi / 2 + 2 * math.pi * progress * i / max(1, n_segs)
        # rose petal modulation
        rose = 1.0 + 0.15 * abs(math.cos(3 * angle)) * progress
        r = radius * rose * pulse
        pts.append((int(cx + r * math.cos(angle)),
                     int(cy + r * math.sin(angle))))
    if len(pts) >= 2:
        pygame.draw.lines(surf, c, False, pts, 3)

    # center text
    font = pygame.font.SysFont(None, 20)
    pct_text = f"{int(progress * 100)}%"
    ts = font.render(pct_text, True, c)
    surf.blit(ts, (cx - ts.get_width() // 2, cy - ts.get_height() // 2))


# ── main ─────────────────────────────────────────────────────
def main():
    pygame.init()
    screen = pygame.display.set_mode((W, H))
    pygame.display.set_caption("VDD PoC: UI Polish (Phase 5)")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont(None, 24)
    font_lg = pygame.font.SysFont(None, 32)
    font_sm = pygame.font.SysFont(None, 20)
    font_notif = pygame.font.SysFont(None, 26)

    hp_pct = 0.75
    selected_unit = 1
    unit_colors = [WORKER_BLUE, SOLDIER_RED, ARCHER_GREEN]
    unit_names = ["Worker", "Soldier", "Archer"]
    multi_select = False
    wave_progress = 0.0
    time_acc = 0
    notifications = []
    notif_messages = [
        ("WAVE INCOMING", HP_RED),
        ("GOLD BONUS 200", TERRAIN_GOLD),
        ("UNIT PROMOTED", HP_GREEN),
        ("BUILDING COMPLETE", WORKER_BLUE),
    ]
    notif_idx = 0

    minimap = Minimap(W - 220, H - 200, 200, 180)

    # demo unit positions for selection rings
    unit_positions = [(300, 350), (420, 320), (360, 400)]

    running = True
    while running:
        dt = clock.tick(30) / 1000.0
        time_acc += dt

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_UP:
                    hp_pct = min(1.0, hp_pct + 0.05)
                elif event.key == pygame.K_DOWN:
                    hp_pct = max(0.0, hp_pct - 0.05)
                elif event.key == pygame.K_1:
                    selected_unit = 0
                elif event.key == pygame.K_2:
                    selected_unit = 1
                elif event.key == pygame.K_3:
                    selected_unit = 2
                elif event.key == pygame.K_SPACE:
                    multi_select = not multi_select
                elif event.key == pygame.K_n:
                    msg, col = notif_messages[notif_idx % len(notif_messages)]
                    notifications.append(Notification(msg, col, 300))
                    notif_idx += 1
                elif event.key == pygame.K_w:
                    wave_progress = min(1.0, wave_progress + 0.15)
                    if wave_progress >= 1.0:
                        wave_progress = 0.0
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = event.pos
                minimap.add_heat(mx, my)

        # update
        minimap.update(dt)
        for n in notifications:
            n.update(dt)
        notifications = [n for n in notifications if n.alive]

        # draw
        screen.fill(COL_BG)

        # title
        screen.blit(font_lg.render("UI Polish (Phase 5)", True, TERRAIN_GOLD), (20, 10))

        # ── Fibonacci HP bar ──
        screen.blit(font.render("Fibonacci HP Bar:", True, GLOW_WHITE), (20, 60))
        draw_fib_hp_bar(screen, 220, 58, 400, 24, hp_pct, time_acc)
        screen.blit(font_sm.render(f"{int(hp_pct * 100)}%", True, GLOW_WHITE), (630, 62))

        # ── resource icons ──
        screen.blit(font.render("Resource Icons:", True, GLOW_WHITE), (20, 110))
        icons = [("Gold", draw_gold_icon, TERRAIN_GOLD, 1250),
                 ("Wood", draw_wood_icon, (30, 110, 50), 830),
                 ("Stone", draw_stone_icon, (160, 150, 130), 445),
                 ("Iron", draw_iron_icon, (100, 160, 220), 120)]
        for i, (name, draw_fn, color, amt) in enumerate(icons):
            ix = 220 + i * 160
            draw_fn(screen, ix, 130, 30, time_acc)
            screen.blit(font_sm.render(f"{name}: {amt}", True, color), (ix + 20, 120))

        # ── selection rings + demo units ──
        screen.blit(font.render(f"Selection: {unit_names[selected_unit]}  "
                                f"{'(multi)' if multi_select else '(single)'}",
                                True, unit_colors[selected_unit]), (20, 180))

        # draw simple unit shapes
        for i, (ux, uy) in enumerate(unit_positions):
            # simple colored circle as placeholder unit
            uc = unit_colors[i]
            pygame.draw.circle(screen, uc, (ux, uy), 15)
            pygame.draw.circle(screen, (0, 0, 0), (ux, uy), 15, 1)

            # selection ring
            if multi_select or i == selected_unit:
                draw_selection_ring(screen, ux, uy, 30,
                                    unit_colors[i], time_acc + i * 2, k=3)

        # ── wave timer ──
        screen.blit(font.render("Wave Timer:", True, GLOW_WHITE), (20, 460))
        draw_wave_timer(screen, 150, 560, 60, wave_progress, time_acc)

        # ── minimap ──
        screen.blit(font.render("Minimap (click to add heat):", True, GLOW_WHITE),
                     (W - 220, H - 225))
        minimap.draw(screen)

        # ── notifications ──
        for n in notifications:
            n.draw(screen, font_notif)

        # controls
        ctrl = "UP/DN: HP  1/2/3: unit  SPACE: multi  N: notify  W: wave  Click map: heat  ESC: quit"
        screen.blit(font_sm.render(ctrl, True, (120, 120, 140)), (20, H - 20))

        pygame.display.flip()

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
